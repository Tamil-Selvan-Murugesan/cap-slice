"""Build the GPU benchmark set: a fixed random sample of pages from all PDFs.

    uv run python tools/gpu/make_bench.py            # 200 pages -> data/bench/bench_01..04.pdf

Pages are drawn uniformly at random (seed 20261003) from data/golden/page_inventory.csv,
so their mix (text pages, tables, scans, slides) matches the whole collection —
which is what a cost-per-page projection needs. They're split into 4 PDFs of 50
pages so concurrency can be tested. data/bench/manifest.csv maps every
benchmark page back to its source document and page. Same seed -> same pages on
every machine, so results from different GPUs are comparable.
"""

from __future__ import annotations

import argparse
import csv
import random
from pathlib import Path

import pymupdf

REPO = Path(__file__).resolve().parents[2]
SEED = 20261003


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pages", type=int, default=200)
    ap.add_argument("--files", type=int, default=4)
    ap.add_argument("--out", default="data/bench")
    args = ap.parse_args()

    inv = list(csv.DictReader((REPO / "data/golden/page_inventory.csv").open()))
    sample = random.Random(SEED).sample(inv, args.pages)
    out = REPO / args.out
    out.mkdir(parents=True, exist_ok=True)
    per = -(-args.pages // args.files)
    rows = []
    for i in range(args.files):
        part = sample[i * per:(i + 1) * per]
        if not part:
            break
        bench = pymupdf.open()
        for r in part:
            with pymupdf.open(REPO / r["doc"]) as src:
                bench.insert_pdf(src, from_page=int(r["page"]) - 1, to_page=int(r["page"]) - 1)
            rows.append({"bench_file": f"bench_{i + 1:02d}.pdf", "bench_page": bench.page_count,
                         "doc": r["doc"], "page": r["page"], "low_text": r["low_text"],
                         "numbers": r["numbers"], "doc_type": r["doc_type"]})
        bench.save(out / f"bench_{i + 1:02d}.pdf")
    with (out / "manifest.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    low = sum(r["low_text"] == "1" for r in rows)
    print(f"{len(rows)} pages in {args.files} files -> {out} ({low} low-text pages)")


if __name__ == "__main__":
    main()
