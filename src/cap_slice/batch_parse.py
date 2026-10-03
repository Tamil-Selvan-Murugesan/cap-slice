"""Parse many PDFs with one parser, caching every document's full output.

    uv run cap-slice-parse --parser docling                      # every downloaded PDF
    uv run cap-slice-parse --parser mineru --workers 8           # concurrent requests to the VLM server
    uv run cap-slice-parse --parser docling --paths data/bench/*.pdf --out parsed_bench

Output, per document (``<out>/<parser>/<doc_id>/``, doc_id = path under data/
without ``.pdf``):
  pages.json    per-page text: {"pages": [[page_no, text], ...], "seconds", ...}
  <raw files>   the parser's lossless output (docling.json; MinerU's JSON/Markdown)
  meta.json     written last: status, timings, versions. Its presence = done.

Per run (``<out>/<parser>/_runs/``):
  <run_id>.jsonl      one event per document (ok / error, seconds, pages)
  <run_id>_gpu.csv    nvidia-smi samples every 5 s (if a GPU is present)
  <run_id>_summary.json

Re-running skips documents that already have a meta.json with status "ok", so
an interrupted run resumes where it stopped. ``--retry-failed`` also redoes
documents whose last attempt failed.
"""

from __future__ import annotations

import argparse
import json
import os
import platform
import shutil
import subprocess
import sys
import threading
import time
import traceback
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from importlib import metadata
from pathlib import Path

from cap_slice.downloader import DATA_DIR, REPO_ROOT
from cap_slice.parsing import PARSERS, get_full_parser

PACKAGES = ("docling", "docling-core", "docling-ibm-models", "torch", "pymupdf", "pymupdf4llm",
            "mineru", "mineru-vl-utils", "vllm", "rapidocr", "rapidocr-onnxruntime")


def doc_id_for(pdf: Path) -> str:
    pdf = pdf.resolve()
    try:
        return str(pdf.relative_to(DATA_DIR.resolve()).with_suffix(""))
    except ValueError:
        return pdf.stem


def versions() -> dict[str, str]:
    out = {}
    for p in PACKAGES:
        try:
            out[p] = metadata.version(p)
        except metadata.PackageNotFoundError:
            pass
    return out


def machine() -> dict:
    info = {"host": platform.node(), "cpus": os.cpu_count(), "python": platform.python_version()}
    try:
        info["cpu"] = next(l.split(":", 1)[1].strip() for l in open("/proc/cpuinfo")
                           if l.startswith("model name"))
    except (OSError, StopIteration):
        pass
    if shutil.which("nvidia-smi"):
        q = subprocess.run(["nvidia-smi", "--query-gpu=name,memory.total,driver_version",
                            "--format=csv,noheader"], capture_output=True, text=True)
        info["gpus"] = [l.strip() for l in q.stdout.splitlines() if l.strip()]
    return info


class GpuMonitor:
    """Samples GPU utilisation, memory and power every few seconds to a CSV."""

    def __init__(self, path: Path, interval: float = 5.0) -> None:
        self.path, self.interval = path, interval
        self._stop = threading.Event()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self.enabled = shutil.which("nvidia-smi") is not None

    def _run(self) -> None:
        with self.path.open("a") as f:
            f.write("time,gpu,util_pct,mem_used_mib,power_w\n")
            while not self._stop.is_set():
                q = subprocess.run(["nvidia-smi", "--query-gpu=index,utilization.gpu,memory.used,power.draw",
                                    "--format=csv,noheader,nounits"], capture_output=True, text=True)
                now = datetime.now(timezone.utc).isoformat(timespec="seconds")
                for line in q.stdout.splitlines():
                    f.write(f"{now},{','.join(x.strip() for x in line.split(','))}\n")
                f.flush()
                self._stop.wait(self.interval)

    def __enter__(self):
        if self.enabled:
            self._thread.start()
        return self

    def __exit__(self, *exc):
        self._stop.set()
        if self.enabled:
            self._thread.join()


def write_atomic(path: Path, data: str | bytes) -> None:
    tmp = path.with_name(path.name + ".part")
    tmp.write_bytes(data if isinstance(data, bytes) else data.encode())
    tmp.replace(path)


def status_of(doc_dir: Path) -> str | None:
    meta = doc_dir / "meta.json"
    if not meta.exists():
        return None
    try:
        return json.loads(meta.read_text()).get("status")
    except json.JSONDecodeError:
        return None


def parse_one(parser: str, pdf: Path, doc_dir: Path, parse) -> dict:
    doc_dir.mkdir(parents=True, exist_ok=True)
    started = datetime.now(timezone.utc).isoformat(timespec="seconds")
    page_count = 0
    t0 = time.perf_counter()
    try:
        import pymupdf
        with pymupdf.open(pdf) as d:
            page_count = d.page_count
        t0 = time.perf_counter()
        out = parse(pdf)
        seconds = time.perf_counter() - t0
        for name, content in out.raw.items():
            write_atomic(doc_dir / name, content)
        write_atomic(doc_dir / "pages.json", json.dumps({
            "parser": parser, "doc": str(pdf), "seconds": seconds, "page_count": page_count,
            "measured_on": started[:10], "pages": [(p.number, p.text) for p in out.pages]}))
        meta = {"status": "ok", "parser": parser, "doc": str(pdf), "page_count": page_count,
                "pages_returned": len(out.pages), "seconds": round(seconds, 3),
                "seconds_per_page": round(seconds / max(page_count, 1), 4),
                "started": started, "info": out.info, "raw_files": sorted(out.raw)}
    except Exception as e:  # keep going; record the failure
        meta = {"status": "error", "parser": parser, "doc": str(pdf), "page_count": page_count,
                "seconds": round(time.perf_counter() - t0, 3), "started": started,
                "error": f"{type(e).__name__}: {e}", "traceback": traceback.format_exc()[-4000:]}
    write_atomic(doc_dir / "meta.json", json.dumps(meta, indent=1))
    return meta


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--parser", required=True, choices=PARSERS)
    ap.add_argument("--paths", nargs="*", help="PDFs to parse (default: every data/*/*/*.pdf)")
    ap.add_argument("--paths-file", help="text file with one PDF path per line")
    ap.add_argument("--out", default="parsed", help="cache root (default: parsed/)")
    ap.add_argument("--workers", type=int, default=1,
                    help="documents in flight at once (use >1 only for mineru, which batches on its server)")
    ap.add_argument("--limit", type=int, help="stop after N documents (smoke tests)")
    ap.add_argument("--retry-failed", action="store_true")
    ap.add_argument("--largest-first", action="store_true",
                    help="start with the biggest PDFs so the tail of the run isn't one long document")
    args = ap.parse_args(argv)

    if args.paths:
        pdfs = [Path(p) for p in args.paths]
    elif args.paths_file:
        pdfs = [Path(l.strip()) for l in Path(args.paths_file).read_text().splitlines() if l.strip()]
    else:
        pdfs = sorted(DATA_DIR.glob("*/*/*.pdf"))
    if args.largest_first:
        pdfs.sort(key=lambda p: p.stat().st_size, reverse=True)

    root = (REPO_ROOT / args.out if not Path(args.out).is_absolute() else Path(args.out)) / args.parser
    runs = root / "_runs"
    runs.mkdir(parents=True, exist_ok=True)
    todo = []
    for pdf in pdfs:
        st = status_of(root / doc_id_for(pdf))
        if st == "ok" or (st == "error" and not args.retry_failed):
            continue
        todo.append(pdf)
    if args.limit:
        todo = todo[: args.limit]

    # pid suffix: parallel processes started in the same second must not share a run id
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + f"_{os.getpid()}"
    header = {"run_id": run_id, "parser": args.parser, "workers": args.workers,
              "docs_total": len(pdfs), "docs_todo": len(todo), "machine": machine(),
              "versions": versions(), "env": {k: v for k, v in os.environ.items()
                                              if k.startswith(("CAP_SLICE_", "MINERU_", "CUDA_"))}}
    (runs / f"{run_id}_header.json").write_text(json.dumps(header, indent=1))
    print(f"[{run_id}] {args.parser}: {len(todo)} to parse ({len(pdfs) - len(todo)} cached/skipped), "
          f"workers={args.workers}", file=sys.stderr)

    parse = get_full_parser(args.parser)
    log = (runs / f"{run_id}.jsonl").open("a")
    lock = threading.Lock()
    done = ok = pages = 0
    t_run = time.perf_counter()

    def work(pdf: Path) -> dict:
        return parse_one(args.parser, pdf, root / doc_id_for(pdf), parse)

    with GpuMonitor(runs / f"{run_id}_gpu.csv"):
        with ThreadPoolExecutor(max_workers=max(1, args.workers)) as pool:
            futures = {pool.submit(work, pdf): pdf for pdf in todo}
            for fut in as_completed(futures):
                meta = fut.result()
                with lock:
                    done += 1
                    ok += meta["status"] == "ok"
                    pages += meta["page_count"] if meta["status"] == "ok" else 0
                    event = {k: meta.get(k) for k in ("status", "doc", "page_count", "seconds",
                                                      "seconds_per_page", "error")}
                    log.write(json.dumps(event) + "\n")
                    log.flush()
                    elapsed = time.perf_counter() - t_run
                    print(f"[{done}/{len(todo)}] {meta['status']:<5} {meta['seconds']:>8.1f}s "
                          f"{meta['page_count']:>4}p  {Path(meta['doc']).name}"
                          f"  | {pages / max(elapsed, 1e-9):.2f} pages/s overall"
                          + (f"  ERROR {meta['error'][:120]}" if meta["status"] != "ok" else ""),
                          file=sys.stderr)
    log.close()
    wall = time.perf_counter() - t_run
    summary = {**header, "docs_ok": ok, "docs_failed": done - ok, "pages_ok": pages,
               "started_unix": round(time.time() - wall, 1), "ended_unix": round(time.time(), 1),
               "wall_seconds": round(wall, 1), "pages_per_second": round(pages / max(wall, 1e-9), 3)}
    (runs / f"{run_id}_summary.json").write_text(json.dumps(summary, indent=1))
    print(f"done: {ok} ok, {done - ok} failed, {pages} pages in {wall:.0f}s "
          f"= {summary['pages_per_second']} pages/s", file=sys.stderr)
    return 1 if done - ok else 0


if __name__ == "__main__":
    sys.exit(main())
