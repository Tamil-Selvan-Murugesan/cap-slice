"""PaddleOCR-VL-1.6 throughput run using the FULL pipeline (layout model + VLM).

The layout model runs in the client process (GPU); only VLM recognition goes to the vLLM server.
Paddle's own queues overlap loading, layout and VLM stages, and vl_rec_max_concurrency controls in-flight
region requests to vLLM.

One client process is the bottleneck (GPU ~33% busy at 1.66 pages/s), so --clients N starts N worker
processes, each with its own pipeline + layout model, on a round-robin split of the pages, all talking to the
same server. Workers warm up first and wait for a common start signal, so only processing is timed.
--concurrency is per client (server sees up to N x concurrency region requests).

Pipeline options are set explicitly (not left to installed defaults):
  pipeline_version="v1.6"        match the PaddleOCR-VL-1.6 server
  use_chart_recognition=True     charts -> tables (our investor decks)
  use_ocr_for_image_block=True   text inside image regions (logos, diagrams, KPI tiles)
  markdown_ignore_labels         Paddle's default hides header, footnote, aside_text, footer, number in the
                                 markdown (they are still recognised). We hide only footers and page
                                 numbers (--md-ignore) and also save the full per-page JSON (<page_id>.json:
                                 every block with label + box), so parsing can decide what to keep.

  python run_paddle.py --manifest pages/manifest.jsonl --warmup-manifest pages/warmup.jsonl --concurrency 64
  python run_paddle.py ... --clients 3 --concurrency 64 --run-name n3_c64
  python run_paddle.py ... --skip-existing     # resume: skip pages whose .md and .json already exist
  python run_paddle.py --manifest loops.jsonl ... --repetition-penalty 1.05 --run-name full_rerun   # re-run loops
"""
import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

from common import (GpuMonitor, Sampler, load_manifest, run_dir, scrape_counters,
                    write_summary)


def page_markdown(res) -> str:
    md = res.markdown or {}
    text = md.get("markdown_texts", "")
    return "\n\n".join(text) if isinstance(text, list) else (text or "")


def write_atomic(path: Path, text: str):
    """Write to a temp file and rename: a crash mid-write never leaves a truncated file that
    --skip-existing would treat as done."""
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(text)
    os.replace(tmp, path)


def page_done(md_dir: Path, page_id: str) -> bool:
    """A page counts as done only if both outputs exist and the JSON parses."""
    md, js = md_dir / f"{page_id}.md", md_dir / f"{page_id}.json"
    if not (md.exists() and js.exists()):
        return False
    try:
        json.loads(js.read_text())
        return True
    except (ValueError, OSError):
        return False


def input_path(res) -> str:
    j = res.json or {}
    return (j.get("res", j) or {}).get("input_path", "")


def make_pipeline(a):
    from paddleocr import PaddleOCRVL
    return PaddleOCRVL(pipeline_version="v1.6",
                       vl_rec_backend="vllm-server",
                       vl_rec_server_url=a.server_url,
                       vl_rec_max_concurrency=a.concurrency,
                       use_chart_recognition=a.charts,
                       use_ocr_for_image_block=True,
                       markdown_ignore_labels=[x for x in a.md_ignore.split(",") if x],
                       use_queues=True)


def predict_kwargs(a) -> dict:
    """Generation settings passed to Paddle's predict() (forwarded to the vLLM server)."""
    return ({"repetition_penalty": a.repetition_penalty}
            if getattr(a, "repetition_penalty", None) else {})


def process(pipeline, rows, md_dir: Path, t0: float, kwargs: dict | None = None):
    """Run the pipeline over rows; write <page_id>.md/.json; return (records, failures)."""
    path_to_id = {r["path"]: r["page_id"] for r in rows}
    records, failures, last = [], 0, t0
    for res in pipeline.predict_iter([r["path"] for r in rows], **(kwargs or {})):  # one result per image
        now = time.perf_counter()
        ip = input_path(res)
        pid = path_to_id.get(ip) or ip.rsplit("/", 1)[-1].rsplit(".", 1)[0]
        try:
            write_atomic(md_dir / f"{pid}.md", page_markdown(res))
            write_atomic(md_dir / f"{pid}.json", json.dumps(res.json, ensure_ascii=False, default=str))
        except Exception as e:  # keep going; count it
            failures += 1
            print(f"failed to extract markdown for {pid}: {e!r}", flush=True)
        # pipelined execution: per-page latency isn't observable, so log completion time and gap
        records.append({"page_id": pid, "done_at_s": now - t0, "gap_s": now - last})
        last = now
    return records, failures


def warm_rows(a, rows):
    return load_manifest(a.warmup_manifest) if a.warmup_manifest else rows[:a.warmup]


def worker(a):
    """One client process of a --clients run: warm up, signal ready, wait for go, process its shard."""
    sync = Path(a.sync_dir)
    rows = load_manifest(a.shard_manifest)
    pipeline = make_pipeline(a)
    for _ in pipeline.predict([r["path"] for r in warm_rows(a, rows)]):
        pass
    (sync / f"ready_{a.worker_index}").touch()
    while not (sync / "go").exists():
        time.sleep(0.2)
    t0 = time.perf_counter()
    records, failures = process(pipeline, rows, Path(a.md_dir), t0, predict_kwargs(a))
    with open(sync / f"records_{a.worker_index}.jsonl", "w") as f:
        for r in records:
            f.write(json.dumps({**r, "client": a.worker_index}) + "\n")
    (sync / f"failures_{a.worker_index}").write_text(str(failures))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", required=True)
    ap.add_argument("--warmup-manifest", help="pages used only for warm-up (not measured)")
    ap.add_argument("--no-charts", dest="charts", action="store_false",
                    help="disable chart recognition")
    ap.add_argument("--md-ignore", default="footer,footer_image,number",
                    help="layout labels left out of the markdown (comma-separated); all labels "
                         "are still recognised and kept in <page_id>.json")
    ap.add_argument("--limit", type=int)
    ap.add_argument("--server-url", default="http://localhost:8118/v1")
    ap.add_argument("--concurrency", type=int, default=64, help="vl_rec_max_concurrency per client")
    ap.add_argument("--clients", type=int, default=1, help="parallel client processes")
    ap.add_argument("--skip-existing", action="store_true",
                    help="skip pages whose .md and .json already exist in the run dir (resume)")
    ap.add_argument("--repetition-penalty", type=float,
                    help="e.g. 1.05 when re-running pages flagged by detect_loops.py")
    ap.add_argument("--warmup", type=int, default=16)
    ap.add_argument("--results", default="results")
    ap.add_argument("--run-name")
    # internal: worker mode
    ap.add_argument("--worker-index", type=int, help=argparse.SUPPRESS)
    ap.add_argument("--shard-manifest", help=argparse.SUPPRESS)
    ap.add_argument("--sync-dir", help=argparse.SUPPRESS)
    ap.add_argument("--md-dir", help=argparse.SUPPRESS)
    a = ap.parse_args()

    if a.worker_index is not None:
        return worker(a)

    rows = load_manifest(a.manifest, a.limit)
    run_name = a.run_name or (f"c{a.concurrency}" if a.clients == 1 else f"n{a.clients}_c{a.concurrency}")
    d = run_dir(a.results, "paddleocr-vl-1.6", run_name)
    if a.skip_existing:
        before_n = len(rows)
        rows = [r for r in rows if not page_done(d / "md", r["page_id"])]
        print(f"skip-existing: {before_n - len(rows)} done, {len(rows)} to go", flush=True)
        if not rows:
            print("nothing to do", flush=True)
            return
    metrics_url = a.server_url.rsplit("/v1", 1)[0] + "/metrics"

    if a.clients == 1:
        pipeline = make_pipeline(a)
        warm = warm_rows(a, rows)
        print(f"warmup: {len(warm)} pages ({'separate pages' if a.warmup_manifest else 'first pages of the set'})",
              flush=True)
        for _ in pipeline.predict([r["path"] for r in warm]):
            pass
        before = scrape_counters(metrics_url)
        with GpuMonitor(d / "gpu.csv"), Sampler(d / "server.jsonl", metrics_url) as smp:
            t0 = time.perf_counter()
            records, failures = process(pipeline, rows, d / "md", t0, predict_kwargs(a))
            wall = time.perf_counter() - t0
        after = scrape_counters(metrics_url)
    else:
        sync = d / "_sync"
        if sync.exists():
            for f in sync.iterdir():
                f.unlink()
        sync.mkdir(exist_ok=True)
        procs = []
        for i in range(a.clients):
            shard = sync / f"shard_{i}.jsonl"
            shard.write_text("".join(json.dumps(r) + "\n" for r in rows[i::a.clients]))
            cmd = [sys.executable, __file__, "--manifest", a.manifest, "--md-ignore", a.md_ignore,
                   "--server-url", a.server_url, "--concurrency", str(a.concurrency),
                   "--warmup", str(a.warmup), "--worker-index", str(i), "--shard-manifest", str(shard),
                   "--sync-dir", str(sync), "--md-dir", str(d / "md")]
            if a.warmup_manifest:
                cmd += ["--warmup-manifest", a.warmup_manifest]
            if not a.charts:
                cmd.append("--no-charts")
            if a.repetition_penalty:
                cmd += ["--repetition-penalty", str(a.repetition_penalty)]
            procs.append(subprocess.Popen(cmd))
        print(f"{a.clients} clients started; warming up...", flush=True)
        while len(list(sync.glob("ready_*"))) < a.clients:
            if any(p.poll() not in (None, 0) for p in procs):
                raise SystemExit("a client exited during warm-up; see output above")
            time.sleep(1)
        print("all clients ready; measuring", flush=True)
        before = scrape_counters(metrics_url)
        with GpuMonitor(d / "gpu.csv"), Sampler(d / "server.jsonl", metrics_url) as smp:
            t0 = time.perf_counter()
            (sync / "go").touch()
            codes = [p.wait() for p in procs]
            wall = time.perf_counter() - t0
        after = scrape_counters(metrics_url)
        records, failures = [], 0
        for i in range(a.clients):
            rf = sync / f"records_{i}.jsonl"
            if rf.exists():
                records += [json.loads(l) for l in rf.read_text().splitlines() if l.strip()]
            ff = sync / f"failures_{i}"
            failures += int(ff.read_text()) if ff.exists() else 0
        if any(codes):
            print(f"WARNING: client exit codes {codes}", flush=True)

    with open(d / "pages.jsonl", "w") as f:
        for r in records:
            f.write(json.dumps(r) + "\n")
    write_summary(d, model="paddleocr-vl-1.6", run_name=run_name,
                  config={"concurrency": a.concurrency, "clients": a.clients,
                          "repetition_penalty": a.repetition_penalty,
                          "chart_recognition": a.charts, "md_ignore": a.md_ignore},
                  n_pages=len(records) - failures, wall_s=wall, latencies=[],
                  failures=failures + (len(rows) - len(records)),
                  counters_before=before, counters_after=after, sampler=smp)


if __name__ == "__main__":
    main()
