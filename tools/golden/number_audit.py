"""Manual audit of number_check.py's "changed" numbers: a seeded sample, each shown as a crop of the page.

    uv run python tools/golden/number_audit.py review/number_fidelity --per-parser 15

For each parser, draws a seeded random sample from flagged.csv. For every sampled number it finds the
printed number on the PDF page (text-layer position), renders that line of the page at 200 dpi and
writes labelled contact sheets (audit_sheet_<n>.png) plus audit_sample.csv with an empty `verdict`
column. A person then looks at each crop and fills in one of:

  misread          the page prints a number the parser got wrong (digit changed, decimal moved, swapped)
  chart_estimate   the parser wrote a value printed nowhere on the page; the "nearest printed number" is
                   only a chart axis tick — the parser estimated a data value from the chart's shape
  text_layer_gap   the parser's number IS printed on the page; the PDF's text layer lacks or garbles it
                   (false alarm of the automatic check)
  unclear          can't tell from the image

misread + chart_estimate = real parser errors; their share is the precision of the "changed" count.
"""

from __future__ import annotations

import argparse
import csv
import random
from pathlib import Path

import pymupdf

SEED = 20261006


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("dir")
    ap.add_argument("--per-parser", type=int, default=15)
    ap.add_argument("--parsers", nargs="*", default=["parsed_advanced/mineru", "parsed/paddleocr_vl"])
    args = ap.parse_args()
    d = Path(args.dir)
    rows = list(csv.DictReader((d / "flagged.csv").open()))
    rng = random.Random(SEED)
    sample = []
    for p in args.parsers:
        mine = [r for r in rows if r["parser"] == p]
        sample += rng.sample(mine, min(args.per_parser, len(mine)))
    tiles = []
    for k, r in enumerate(sample, 1):
        with pymupdf.open(r["doc"]) as pdf:
            page = pdf[int(r["page"]) - 1]
            hits = page.search_for(r["printed"])
            if hits:
                h = hits[0]
                clip = pymupdf.Rect(page.rect.x0, h.y0 - 14, page.rect.x1, h.y1 + 14)
                hl = pymupdf.Rect(h.x0 - 2, h.y0 - 2, h.x1 + 2, h.y1 + 2)
                page.draw_rect(hl, color=(1, 0, 0), width=1.2)  # in memory only; the file is not saved
            else:
                clip = page.rect
            pix = page.get_pixmap(dpi=200, clip=clip)
        tiles.append((k, r, pix, bool(hits)))
        r["id"] = k
        r["found_on_page"] = "yes" if hits else "no"
        r["verdict"] = ""
        r["note"] = ""
    # contact sheets: 6 crops per sheet, each captioned with what the parser wrote vs the text layer
    width = 1600
    for s in range(0, len(tiles), 6):
        chunk = tiles[s:s + 6]
        heights = [int(p.height * min(1.0, width / p.width)) + 34 for _, _, p, _ in chunk]
        doc = pymupdf.open()
        pg = doc.new_page(width=width, height=sum(heights) + 10)
        y = 5
        for (k, r, pix, found), h in zip(chunk, heights):
            name = "MinerU advanced" if "advanced" in r["parser"] else r["parser"].split("/")[-1]
            pg.insert_text((6, y + 22), f"#{k}  {name} wrote {r['parser_wrote']}   |   text layer: {r['printed']}"
                           f"   ({r['doc'][5:]} p{r['page']}){'' if found else '  [printed number not located]'}",
                           fontsize=15)
            scale = min(1.0, width / pix.width)
            pg.insert_image(pymupdf.Rect(0, y + 30, pix.width * scale, y + 30 + pix.height * scale), pixmap=pix)
            y += h
        doc[0].get_pixmap(dpi=72).save(d / f"audit_sheet_{s // 6 + 1}.png")
    with (d / "audit_sample.csv").open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["id", "parser", "doc", "page", "doc_type", "parser_wrote", "printed",
                                           "found_on_page", "verdict", "note"])
        w.writeheader()
        w.writerows(sample)
    print(f"{len(sample)} sampled; sheets and audit_sample.csv in {d}")


if __name__ == "__main__":
    main()
