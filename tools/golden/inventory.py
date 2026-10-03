"""Page inventory + stratified, seeded sample of candidate pages for golden facts.

    uv run python tools/golden/inventory.py

Writes data/golden/page_inventory.csv (one row per page of every downloaded
PDF: cheap PyMuPDF features) and data/golden/v2_candidates.csv (sampled pages
per stratum). Documents already in the v1 golden set (compare_docs.csv) are
excluded, so v2 facts come only from documents no parser or chunker was
tuned on. Facts themselves are then written by reading the rendered page
images — never from parser output.
"""

from __future__ import annotations

import csv
import random
import re
from pathlib import Path

import pymupdf

REPO = Path(__file__).resolve().parents[2]
GOLDEN = REPO / "data" / "golden"
SEED = 20261002

NUM = re.compile(r"^\(?-?[\d,]+\.\d{1,2}\)?$|^\(?\d{1,3}(,\d{2,3})+\)?$")
STATEMENT = re.compile(r"(?i)balance sheet as at|statement of profit and loss|cash flow statement|"
                       r"statement of cash flows|statement of changes in equity")
RESULTS = re.compile(r"(?i)quarter ended|half year ended|six months ended|nine months ended")
SEGMENT = re.compile(r"(?i)segment (revenue|results|information|wise)")
CONTINUED = re.compile(r"(?i)\(contd\.?\)|\(continued\)|contd\.")
FOOTNOTE = re.compile(r"(?im)^\s*(\*|#|\(\d\)|note\s*:)")

# stratum -> (number of candidate pages to draw, predicate on a row)
STRATA = {
    "digital_statement": (12, lambda r: r["low_text"] == "0" and r["statement"] == "1"),
    "low_text_numeric": (12, lambda r: r["low_text"] == "1" and r["image_cover"] == "1"),
    "results_columns": (8, lambda r: r["low_text"] == "0" and r["results"] == "1" and int(r["numbers"]) >= 40),
    "segment_or_continued": (8, lambda r: r["low_text"] == "0" and (r["segment"] == "1" or r["continued"] == "1")
                             and int(r["numbers"]) >= 30),
    "slide_numbers": (10, lambda r: r["doc_type"] == "investor_presentation" and int(r["numbers"]) >= 8),
    "concall_qa": (10, lambda r: r["doc_type"] == "concall_transcript" and r["has_question"] == "1"),
    "prose_footnote": (10, lambda r: r["low_text"] == "0" and r["doc_type"] == "annual_report"
                       and r["footnote"] == "1" and int(r["words"]) >= 300),
}


def features(pdf: Path, symbol: str, doc_type: str) -> list[dict]:
    rows = []
    with pymupdf.open(pdf) as doc:
        for i, page in enumerate(doc, 1):
            text = page.get_text()
            words = text.split()
            area = page.rect.width * page.rect.height
            cover = 0.0
            for img in page.get_images():
                for r in page.get_image_rects(img[0]):
                    cover = max(cover, (r & page.rect).get_area() / area)
            rows.append({
                "doc": str(pdf.relative_to(REPO)), "symbol": symbol, "doc_type": doc_type, "page": i,
                "pages": doc.page_count, "chars": len(text.strip()), "words": len(words),
                "numbers": sum(bool(NUM.match(w)) for w in words),
                "low_text": int(len(text.strip()) < 50), "image_cover": int(cover > 0.5),
                "statement": int(bool(STATEMENT.search(text))), "results": int(bool(RESULTS.search(text))),
                "segment": int(bool(SEGMENT.search(text))), "continued": int(bool(CONTINUED.search(text))),
                "footnote": int(bool(FOOTNOTE.search(text))), "has_question": int("?" in text),
            })
    return rows


def main() -> None:
    v1 = {r["path"] for r in csv.DictReader((GOLDEN / "compare_docs.csv").open())}
    rows = []
    for pdf in sorted((REPO / "data").glob("*/*/*.pdf")):
        rows += features(pdf, pdf.parts[-3], pdf.parts[-2].rstrip("s"))
    with (GOLDEN / "page_inventory.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print(f"inventory: {len(rows)} pages, {len({r['doc'] for r in rows})} docs")

    rows = [{k: str(v) for k, v in r.items()} for r in rows if r["doc"] not in v1]
    rng = random.Random(SEED)
    picked, used_pages = [], set()
    for stratum, (n, pred) in STRATA.items():
        pool = [r for r in rows if pred(r) and (r["doc"], r["page"]) not in used_pages]
        # Spread across documents: at most 2 pages per document per stratum.
        rng.shuffle(pool)
        per_doc: dict[str, int] = {}
        chosen = []
        for r in pool:
            if per_doc.get(r["doc"], 0) >= 2:
                continue
            per_doc[r["doc"]] = per_doc.get(r["doc"], 0) + 1
            chosen.append(r)
            if len(chosen) == n:
                break
        for r in chosen:
            used_pages.add((r["doc"], r["page"]))
            picked.append({"stratum": stratum, "doc": r["doc"], "symbol": r["symbol"],
                           "doc_type": r["doc_type"], "page": r["page"], "numbers": r["numbers"],
                           "low_text": r["low_text"]})
        print(f"{stratum:<22} pool {len(pool):>5}  picked {len(chosen)}")
    with (GOLDEN / "v2_candidates.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(picked[0]))
        w.writeheader()
        w.writerows(picked)
    print(f"candidates: {len(picked)} pages from {len({p['doc'] for p in picked})} docs, "
          f"{len({p['symbol'] for p in picked})} companies")


if __name__ == "__main__":
    main()
