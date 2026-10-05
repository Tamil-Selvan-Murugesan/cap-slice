"""Golden v3 candidates: seeded random pages from "hard" pools, rendered as labelled thumbnail sheets.

    uv run python tools/golden/v3_candidates.py --out /tmp/v3          # sheets + candidates.csv

v3 targets what v1/v2 under-sample: charts, scanned pages with content, complex tables and other hard
layouts. Pages come only from documents that are in neither v1 nor v2 (nor v2's skipped list) and that
were not used in the parser side-by-side review, so no parser output for them has been looked at.
Pages are then picked *by eye* from the sheets (purposive: the hard ones), and every value is read off a
high-resolution render of the page, never from a parser.
"""

from __future__ import annotations

import argparse
import csv
import random
from pathlib import Path

import pymupdf

GOLDEN = Path("data/golden")
SEED = 20261005
EXCLUDE_EXTRA = {  # documents shown in the parser side-by-side review (2026-10-05)
    "data/APARINDS/investor_presentations/Jun-2021.pdf",
    "data/E2E/annual_reports/2023-09-21_FY2022-23.pdf",
    "data/ESCONET/periodic_results/2025-11-14_H1-FY26-half-yearly-SME.pdf",
}


def f(r: dict, k: str) -> float:
    return float(r[k] or 0)


POOLS = {
    # image-only pages that are not slide decks: scanned statements, letters, forms
    "scan_doc": lambda r: r["low_text"] == "1" and r["doc_type"] != "investor_presentation",
    # image-only slides: charts or tables pasted as pictures, KPI tiles
    "scan_slide": lambda r: r["low_text"] == "1" and r["doc_type"] == "investor_presentation",
    # slides with a moderate count of numbers: most vector charts and data-label slides live here
    "slide_numbers": lambda r: r["doc_type"] == "investor_presentation" and 10 <= f(r, "numbers") <= 80,
    # very dense pages: big statements, multi-column notes
    "dense_table": lambda r: f(r, "numbers") >= 120,
    # continued tables and segment tables
    "continued_segment": lambda r: (r["continued"] == "1" or r["segment"] == "1") and f(r, "numbers") >= 30,
}


PREFIX = {"scan_doc": "sdoc", "scan_slide": "sslide", "slide_numbers": "slide", "dense_table": "dense",
          "continued_segment": "conti"}


def excluded() -> set[str]:
    out = set(EXCLUDE_EXTRA)
    out |= {r["path"] for r in csv.DictReader((GOLDEN / "v2_facts.csv").open())}
    out |= {r["path"] for r in csv.DictReader((GOLDEN / "v2_skipped.csv").open())}
    out |= {r["path"] for r in csv.DictReader((GOLDEN / "compare_docs.csv").open())}
    return out


def sheet(rows: list[dict], out: Path, cols: int = 5, thumb_w: int = 300) -> None:
    """Render rows as a grid of labelled thumbnails into one PNG."""
    tiles = []
    for r in rows:
        with pymupdf.open(r["doc"]) as doc:
            page = doc[int(r["page"]) - 1]
            pix = page.get_pixmap(matrix=pymupdf.Matrix(thumb_w / page.rect.width, thumb_w / page.rect.width))
            tiles.append((r["cand_id"], pix))
    th = max(p.height for _, p in tiles) + 22
    rows_n = (len(tiles) + cols - 1) // cols
    canvas = pymupdf.open()
    pg = canvas.new_page(width=cols * (thumb_w + 8), height=rows_n * th)
    for i, (cid, pix) in enumerate(tiles):
        x, y = (i % cols) * (thumb_w + 8), (i // cols) * th
        pg.insert_image(pymupdf.Rect(x, y + 20, x + pix.width, y + 20 + pix.height), pixmap=pix)
        pg.insert_text((x + 2, y + 15), cid, fontsize=13)
    canvas[0].get_pixmap(dpi=72).save(out)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--per-pool", type=int, default=20)
    args = ap.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    skip = excluded()
    rows = [r for r in csv.DictReader((GOLDEN / "page_inventory.csv").open()) if r["doc"] not in skip]
    rng = random.Random(SEED)
    picked = []
    for name, test in POOLS.items():
        pool = [r for r in rows if test(r)]
        rng.shuffle(pool)
        chosen, per_doc = [], {}
        for r in pool:  # at most 2 pages per document per pool, for spread
            if per_doc.get(r["doc"], 0) >= 2:
                continue
            per_doc[r["doc"]] = per_doc.get(r["doc"], 0) + 1
            chosen.append({**r, "pool": name, "cand_id": f"{PREFIX[name]}{len(chosen) + 1:02d}"})
            if len(chosen) == args.per_pool:
                break
        sheet(chosen, out / f"sheet_{name}.png")
        picked += chosen
        print(f"{name}: {len(pool)} pages in pool, {len(chosen)} drawn")
    with (out / "candidates.csv").open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["cand_id", "pool", "doc", "page", "doc_type", "numbers", "low_text", "image_cover"])
        w.writeheader()
        for r in picked:
            w.writerow({k: r[k] for k in w.fieldnames})


if __name__ == "__main__":
    main()
