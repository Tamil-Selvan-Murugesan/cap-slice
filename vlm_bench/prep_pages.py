"""Render PDF pages to PNG once, at a fixed DPI, so all models see identical input.

Rendering is CPU work you already do in production, so it is timed separately here
and excluded from model throughput.

Two modes:

  # Benchmark set (recommended): render exactly the pages listed in a manifest built by
  # parsing_eval/sets/build_sample.py. Keeps its page_id (<doc_id>_p<NNN>) and
  # all other fields, and fills in "path", "w", "h".
  python prep_pages.py --from-manifest /workspace/data/bench_set/manifest.jsonl \
      --out-dir /workspace/data/pages --dpi 200
  python prep_pages.py --from-manifest /workspace/data/bench_set/warmup.jsonl \
      --out-dir /workspace/data/pages --dpi 200

  # Whole PDFs: every page of every PDF under --pdf-dir (page_id = <stem>__p<NNNN>, 0-based)
  python prep_pages.py --pdf-dir /workspace/data/pdfs --out-dir /workspace/data/pages --dpi 200
"""
import argparse
import json
import os
import time
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import pymupdf


def render_pdf(args):
    pdf_path, out_dir, dpi = args
    rows = []
    stem = Path(pdf_path).stem
    with pymupdf.open(pdf_path) as doc:
        for i, page in enumerate(doc):
            page_id = f"{stem}__p{i:04d}"
            out = Path(out_dir) / f"{page_id}.png"
            pix = page.get_pixmap(dpi=dpi)
            pix.save(out)
            rows.append({"page_id": page_id, "pdf": str(pdf_path), "page_no": i,
                         "path": str(out.resolve()), "w": pix.width, "h": pix.height})
    return rows


def render_listed(args):
    """Render the manifest rows of one PDF; row["page_no"] is the index in that PDF."""
    pdf_path, rows, out_dir, dpi = args
    out_rows = []
    with pymupdf.open(pdf_path) as doc:
        for r in rows:
            out = Path(out_dir) / f"{r['page_id']}.png"
            pix = doc[r["page_no"]].get_pixmap(dpi=dpi)
            pix.save(out)
            out_rows.append({**r, "pdf": str(pdf_path), "path": str(out.resolve()),
                             "w": pix.width, "h": pix.height, "dpi": dpi})
    return out_rows


def main():
    ap = argparse.ArgumentParser()
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--pdf-dir")
    src.add_argument("--from-manifest", help="manifest.jsonl from build_sample.py")
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--dpi", type=int, default=200)
    ap.add_argument("--workers", type=int, default=os.cpu_count())
    ap.add_argument("--manifest", default=None,
                    help="output manifest; default: <out-dir>/<input manifest name> "
                         "or <out-dir>/manifest.jsonl")
    a = ap.parse_args()

    Path(a.out_dir).mkdir(parents=True, exist_ok=True)
    t0 = time.perf_counter()
    rows = []
    if a.from_manifest:
        src_manifest = Path(a.from_manifest)
        by_pdf = defaultdict(list)
        for line in src_manifest.read_text().splitlines():
            if line.strip():
                r = json.loads(line)
                by_pdf[str((src_manifest.parent / r["pdf"]).resolve())].append(r)
        jobs = [(pdf, rs, a.out_dir, a.dpi) for pdf, rs in by_pdf.items()]
        with ProcessPoolExecutor(a.workers) as ex:
            for r in ex.map(render_listed, jobs):
                rows.extend(r)
        n_pdfs = len(by_pdf)
        default_name = src_manifest.name
    else:
        pdfs = sorted(Path(a.pdf_dir).rglob("*.pdf"))
        with ProcessPoolExecutor(a.workers) as ex:
            for r in ex.map(render_pdf, [(str(p), a.out_dir, a.dpi) for p in pdfs]):
                rows.extend(r)
        n_pdfs = len(pdfs)
        default_name = "manifest.jsonl"
    dt = time.perf_counter() - t0

    manifest = a.manifest or str(Path(a.out_dir) / default_name)
    with open(manifest, "w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    print(f"{n_pdfs} PDFs -> {len(rows)} pages in {dt:.1f}s "
          f"({len(rows)/dt:.1f} pages/s on {a.workers} procs @ {a.dpi} DPI)")
    print(f"manifest: {manifest}")


if __name__ == "__main__":
    main()
