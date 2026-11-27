"""MinerU 4 (MinerU2.5-Pro VLM) run over whole PDFs, written out per page like the other runners.

MinerU parses a document, not a page image, so this runner groups the manifest by PDF, parses each
PDF once and splits the result into md/<page_id>.md (MinerU's own Markdown renderer, one page at a
time) and md/<page_id>.json (that page's blocks: type, box, text, tables as HTML). The whole-document
middle JSON (MinerU's lossless output) is kept in docs/<doc_id>.json. score.py and detect_loops.py
read the per-page files exactly as for Paddle.

Tier and mode (defaults = full vision, like our PaddleOCR-VL setup):
  --tier advanced     MinerU2.5-Pro does layout AND reads every block (MinerU "xhigh" effort)
  --parse-mode ocr    never take text from the PDF's text layer. "auto" classifies each PDF and,
                      for ones it thinks are digital, keeps text-layer text -- which brings back the
                      wrong-OCR layers of our scans.

Concurrency: --procs parser processes (each loads its own MinerU layout/table models and gets a
page-balanced share of the PDFs) x --workers PDFs in flight per process (threads); each PDF fans out
up to --vlm-concurrency VLM requests, which vLLM batches.

  ./serve.sh mineru
  MINERU_MALLOC_TRIM=1 MALLOC_ARENA_MAX=2 MINERU_PROCESSING_WINDOW_SIZE=32 python run_mineru.py \\
      --manifest $FP/manifest.jsonl --procs 4 --workers 1 --skip-existing \\
      --results /workspace/results_full --run-name full

MINERU_MALLOC_TRIM=1 / MALLOC_ARENA_MAX=2 hand freed memory back to the OS after each page window
(main's runbook: without them a runner holds ~12 GB per large PDF; the pod's limit is 62 GB).
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
import threading
import time
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from common import (GpuMonitor, Sampler, load_manifest, page_done, run_dir, scrape_counters,
                    write_atomic, write_summary)

MODEL = "mineru2.5-pro"


def page_markdown(middle: dict, page: dict) -> str:
    """Render one page with MinerU's renderer by giving it a one-page document (as main's adapter)."""
    import copy

    from mineru.parser.base import ParseResult

    one = copy.deepcopy({k: v for k, v in middle.items() if k != "pages"})
    one["pages"] = [page]
    layout = one.get("extensions", {}).get("docvortex_layout")
    if layout and "pages" in layout:
        layout["pages"] = [p for p in layout["pages"] if p.get("page_idx") == page["page_idx"]]
    return ParseResult.from_dict(one).markdown()


def make_parser(a):
    from mineru.config import VlmConfig
    from mineru.parser.mineru_parser import MinerUParser
    return MinerUParser(tier=a.tier, parse_mode=a.parse_mode,
                        vlm_config=VlmConfig(server_url=a.server_url,
                                             max_concurrency=a.vlm_concurrency))


def parse_doc(a, pdf: str, rows: list[dict], md_dir: Path, docs_dir: Path) -> dict:
    """Parse one PDF and write its pages. Returns a per-document record."""
    t = time.perf_counter()
    result = make_parser(a).parse(pdf)
    middle = result.to_dict()
    doc_s = time.perf_counter() - t
    write_atomic(docs_dir / f"{rows[0]['doc_id']}.json", json.dumps(middle, ensure_ascii=False))
    by_idx = {p["page_idx"]: p for p in middle.get("pages", [])}
    written, missing = [], []
    for r in rows:
        page = by_idx.get(r["page_no"])
        if page is None:
            missing.append(r["page_id"])
            continue
        write_atomic(md_dir / f"{r['page_id']}.md", page_markdown(middle, page))
        write_atomic(md_dir / f"{r['page_id']}.json", json.dumps(page, ensure_ascii=False, default=str))
        written.append(r["page_id"])
    return {"doc_id": rows[0]["doc_id"], "pdf": pdf, "pages": len(written), "missing": missing,
            "doc_s": round(doc_s, 2),
            "parse_mode_used": middle.get("extensions", {}).get("mineru", {})}


def run_docs(a, order, docs, md_dir: Path, docs_dir: Path, t0: float, tag: str = ""):
    """Parse PDFs, a.workers at a time (threads). Returns (page records, doc records, failures)."""
    records, doc_records, failures, n_docs = [], [], [], 0
    n_pages = sum(len(docs[p]) for p in order)
    lock = threading.Lock()
    with ThreadPoolExecutor(max_workers=a.workers) as pool:
        futs = {pool.submit(parse_doc, a, p, docs[p], md_dir, docs_dir): p for p in order}
        for f in as_completed(futs):
            pdf, now = futs[f], time.perf_counter() - t0
            with lock:
                try:
                    rec = f.result()
                    doc_records.append(rec)
                    records += [{"page_id": r["page_id"], "doc_id": rec["doc_id"], "done_at_s": now,
                                 "doc_s": rec["doc_s"]} for r in docs[pdf]
                                if r["page_id"] not in rec["missing"]]
                    if rec["missing"]:
                        failures.append({"pdf": pdf, "missing_pages": rec["missing"]})
                except Exception as e:  # keep going; the PDF is re-tried by --skip-existing
                    failures.append({"pdf": pdf, "error": repr(e)})
                    print(f"{tag}FAILED {Path(pdf).name}: {e!r}", flush=True)
                n_docs += 1
                print(f"{tag}[{n_docs}/{len(order)}] {Path(pdf).name} ({len(docs[pdf])} p) | "
                      f"{len(records)}/{n_pages} pages, {len(records) / now:.2f} pages/s", flush=True)
    return records, doc_records, failures


def split_by_pages(order, docs, n: int) -> list[list[str]]:
    """Largest PDF first onto the least-loaded process, so every process gets ~the same pages."""
    shards, load = [[] for _ in range(n)], [0] * n
    for p in order:
        i = load.index(min(load))
        shards[i].append(p)
        load[i] += len(docs[p])
    return shards


def run_procs(a, order, docs, d: Path):
    """--procs N: N child processes (each its own MinerU models, a.workers PDFs in flight) on a
    page-balanced split of the PDFs; this process only monitors and merges."""
    sync = d / "_sync"
    shutil.rmtree(sync, ignore_errors=True)
    sync.mkdir()
    argv = [x for x in sys.argv[1:]]
    procs = []
    for i, shard in enumerate(split_by_pages(order, docs, a.procs)):
        if not shard:   # fewer PDFs left than processes (e.g. a resume): don't load models for nothing
            continue
        (sync / f"shard_{i}.json").write_text(json.dumps(shard))
        print(f"process {i}: {len(shard)} PDFs, {sum(len(docs[p]) for p in shard)} pages", flush=True)
        procs.append(subprocess.Popen([sys.executable, __file__, *argv, "--procs", "1", "--warmup-docs", "0",
                                       "--shard-file", str(sync / f"shard_{i}.json"),
                                       "--worker-index", str(i)]))
    codes = [p.wait() for p in procs]
    if any(codes):
        print(f"WARNING: process exit codes {codes}; re-run with --skip-existing", flush=True)
    out = []
    for kind in ("records", "docs", "failures"):
        rows = []
        for f in sorted(sync.glob(f"{kind}_*.jsonl")):
            rows += [json.loads(l) for l in f.read_text().splitlines() if l.strip()]
        out.append(rows)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", required=True, help="page manifest with pdf, page_no, page_id, doc_id")
    ap.add_argument("--pdf-root", default=None, help="base for relative 'pdf' paths (default: manifest dir)")
    ap.add_argument("--server-url", default="http://127.0.0.1:30000")
    ap.add_argument("--tier", default="advanced", choices=["standard", "advanced"])
    ap.add_argument("--parse-mode", default="ocr", choices=["ocr", "auto", "txt"])
    ap.add_argument("--procs", type=int, default=1,
                    help="parser processes, each with its own MinerU models and a page-balanced share of PDFs")
    ap.add_argument("--workers", type=int, default=1, help="PDFs in flight per process (threads)")
    ap.add_argument("--vlm-concurrency", type=int, default=100,
                    help="max VLM requests in flight per document (MinerU's default 100)")
    ap.add_argument("--warmup-docs", type=int, default=1,
                    help="parse the N smallest PDFs first, unmeasured (loads models, compiles kernels)")
    ap.add_argument("--limit-docs", type=int, default=None, help="only the first N PDFs (smoke test)")
    ap.add_argument("--skip-existing", action="store_true",
                    help="skip PDFs whose pages all have a .md and a valid .json")
    ap.add_argument("--results", default="results")
    ap.add_argument("--run-name", default="default")
    ap.add_argument("--shard-file", help=argparse.SUPPRESS)      # set by --procs for its children
    ap.add_argument("--worker-index", type=int, help=argparse.SUPPRESS)
    a = ap.parse_args()

    os.environ.setdefault("MINERU_MALLOC_TRIM", "1")
    rows = load_manifest(a.manifest)
    root = Path(a.pdf_root or Path(a.manifest).parent)
    docs = defaultdict(list)
    for r in rows:
        pdf = r["pdf"] if Path(r["pdf"]).is_absolute() else str(root / r["pdf"])
        docs[pdf].append(r)
    d = run_dir(a.results, MODEL, a.run_name)
    md_dir, docs_dir = d / "md", d / "docs"
    docs_dir.mkdir(exist_ok=True)

    if a.shard_file:  # child of --procs: parse my share, hand results to the parent, no monitoring
        tag = f"p{a.worker_index} "
        order = json.loads(Path(a.shard_file).read_text())
        recs, doc_recs, fails = run_docs(a, order, docs, md_dir, docs_dir, time.perf_counter(), tag)
        sync = Path(a.shard_file).parent
        for kind, rows_ in (("records", recs), ("docs", doc_recs), ("failures", fails)):
            (sync / f"{kind}_{a.worker_index}.jsonl").write_text(
                "".join(json.dumps({**x, "proc": a.worker_index}) + "\n" for x in rows_))
        return

    # largest first: the long annual reports start early instead of being the tail of the run
    order = sorted(docs, key=lambda p: -len(docs[p]))
    if a.limit_docs:
        order = order[:a.limit_docs]
    if a.warmup_docs and a.procs == 1:
        for pdf in sorted(order, key=lambda p: len(docs[p]))[:a.warmup_docs]:
            t = time.perf_counter()
            make_parser(a).parse(pdf)
            print(f"warmup: {Path(pdf).name} ({len(docs[pdf])} pages) {time.perf_counter() - t:.1f}s", flush=True)
    if a.skip_existing:
        before = len(order)
        order = [p for p in order if not all(page_done(md_dir, r["page_id"]) for r in docs[p])]
        print(f"skip-existing: {before - len(order)} PDFs already done, {len(order)} to parse", flush=True)
    if not order:
        print("nothing to do", flush=True)
        return
    n_pages = sum(len(docs[p]) for p in order)
    print(f"{len(order)} PDFs, {n_pages} pages, {a.procs} process(es) x {a.workers} PDF(s) in flight, "
          f"tier={a.tier} parse_mode={a.parse_mode}", flush=True)

    metrics_url = a.server_url.rstrip("/") + "/metrics"
    t0 = time.perf_counter()
    with GpuMonitor(d / "gpu.csv"), Sampler(d / "server.jsonl", metrics_url) as sampler:
        before = scrape_counters(metrics_url)
        if a.procs > 1:   # includes each process loading its models (~1 min), negligible over hours
            records, doc_records, failures = run_procs(a, order, docs, d)
        else:
            records, doc_records, failures = run_docs(a, order, docs, md_dir, docs_dir, t0)
        wall = time.perf_counter() - t0
        after = scrape_counters(metrics_url)

    with open(d / "pages.jsonl", "w") as fh:
        fh.writelines(json.dumps(r) + "\n" for r in records)
    with open(d / "docs.jsonl", "w") as fh:
        fh.writelines(json.dumps(r) + "\n" for r in doc_records)
    if failures:
        (d / "failures.jsonl").write_text("".join(json.dumps(x) + "\n" for x in failures))
        print(f"WARNING: {len(failures)} PDFs failed or lost pages -> {d / 'failures.jsonl'}; "
              f"re-run with --skip-existing", flush=True)
    write_summary(d, model=MODEL, run_name=a.run_name,
                  config={"tier": a.tier, "parse_mode": a.parse_mode, "procs": a.procs,
                          "workers": a.workers, "vlm_concurrency": a.vlm_concurrency,
                          "window": os.environ.get("MINERU_PROCESSING_WINDOW_SIZE", "64"),
                          "pdfs": len(order)},
                  n_pages=len(records), wall_s=wall,
                  latencies=[r["doc_s"] for r in doc_records],  # per DOCUMENT, not per page
                  failures=n_pages - len(records),
                  counters_before=before, counters_after=after, sampler=sampler)


if __name__ == "__main__":
    main()
