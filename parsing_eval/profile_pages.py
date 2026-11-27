"""
Cheap per-page profile of every selected PDF (no OCR, no layout model).

Writes <data>/page_profile/pages.csv (see paths.py) with one row per page:
  doc_id, symbol, kind, filing_date, pdf_page, pdf_pages, chars, invisible_frac,
  image_cov, n_drawings, n_numbers, page_class

page_class (first rule that matches):
  scanned_old_ocr   >= 50% of text is invisible (render mode 3) over a large image
  scanned_no_text   < 50 visible chars and an image covering >= 50% of the page
  chart_or_graphic  presentation page with large images or many vector drawings
  table_dense       many numbers on the page (financial statements, results tables)
  text              everything else (prose: transcripts, MD&A, letters)
Read-only with respect to cap-slice (SQLite mode=ro).
"""
import csv
import re
import sqlite3
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import pymupdf

from paths import DB_PATH, PROFILE as OUT
NUM = re.compile(r"\(?-?\d[\d,]*\.?\d*\)?")


def classify(kind, chars, invisible_frac, image_cov, n_drawings, n_numbers):
    if invisible_frac >= 0.5 and image_cov >= 0.5:
        return "scanned_old_ocr"
    if chars < 50 and image_cov >= 0.5:
        return "scanned_no_text"
    if kind == "investor_presentation" and (image_cov >= 0.3 or n_drawings >= 40):
        return "chart_or_graphic"
    if n_numbers >= 80:
        return "table_dense"
    return "text"


def profile(doc):
    pymupdf.TOOLS.mupdf_display_errors(False)
    rows = []
    try:
        d = pymupdf.open(doc["path"])
    except Exception as e:
        print(f"open failed {doc['doc_id']}: {e}", file=sys.stderr)
        return rows
    for p in d:
        try:
            spans = p.get_texttrace()
            vis = sum(len(s["chars"]) for s in spans if s["type"] != 3)
            inv = sum(len(s["chars"]) for s in spans if s["type"] == 3)
            text = p.get_text()
            area = abs(p.rect) or 1
            image_cov = min(1.0, sum(abs(pymupdf.Rect(b["bbox"]) & p.rect)
                                     for b in p.get_image_info()) / area)
            n_draw = len(p.get_drawings())
            n_num = len(NUM.findall(text))
        except Exception as e:
            print(f"page failed {doc['doc_id']} p{p.number + 1}: {e}", file=sys.stderr)
            continue
        chars = vis + inv
        inv_frac = inv / chars if chars else 0.0
        rows.append({
            **{k: doc[k] for k in ("doc_id", "symbol", "kind", "filing_date")},
            "pdf_page": p.number + 1, "pdf_pages": d.page_count,
            "chars": vis, "invisible_frac": round(inv_frac, 2),
            "image_cov": round(image_cov, 2), "n_drawings": n_draw, "n_numbers": n_num,
            "page_class": classify(doc["kind"], vis, inv_frac, image_cov, n_draw, n_num),
        })
    d.close()
    return rows


def main():
    db = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
    docs = [dict(zip(("doc_id", "symbol", "kind", "filing_date", "path"), r)) for r in db.execute(
        """SELECT id, symbol, curated_kind, filing_date, ingestion_path
           FROM ingestion_documents WHERE ingestion_format = 'pdf' ORDER BY id""")]
    rows = []
    with ProcessPoolExecutor() as ex:
        for r in ex.map(profile, docs, chunksize=4):
            rows.extend(r)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print(f"{len(docs)} PDFs, {len(rows)} pages -> {OUT}")


if __name__ == "__main__":
    main()
