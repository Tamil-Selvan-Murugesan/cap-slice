"""
Parse the 10-document evaluation sample with pymupdf4llm (layout mode + RapidOCR).

Read-only with respect to cap-slice: SQLite is opened with mode=ro and source
PDFs are only read. Everything is written under <data>/baselines/pymupdf4llm_output/ (see paths.py).

Per document (output/<doc_id>_<symbol>_<kind>/):
  document.md   markdown of all parsed pages, each preceded by <!-- page N -->
  pages.jsonl   one row per page: markdown, whether OCR ran, box-class counts
  layout.jsonl  one row per layout box: page, class, bbox, heading level, text,
                table shape -- the raw material for designing the chunker
  meta.json     document metadata from SQLite + timing/memory for this run
Plus output/summary.csv across documents.

Page numbers are 1-based PDF page indices (not printed page numbers).

Run:
  python parsing_eval/baselines/pymupdf4llm_parse.py [doc_id ...]
  (needs pymupdf4llm + pymupdf-layout + rapidocr; see parsing_eval/requirements.txt)
"""
import csv
import json
import resource
import sqlite3
import sys
import time
from collections import Counter
from importlib.metadata import version
from pathlib import Path

import pymupdf
import pymupdf4llm  # noqa: F401  (activates pymupdf.layout)
from pymupdf4llm.helpers import document_layout as dl

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # parsing_eval/ (paths.py)
from paths import BASELINES, DB_PATH  # noqa: E402

OUT = BASELINES / "pymupdf4llm_output"

# doc_id -> 1-based pages to parse (None = whole document).
# Annual reports are subsets: highlights/letter/MD&A, OCR-flagged pages,
# primary statements, notes and segment pages.
SAMPLE = {
    1:   [41, 42, 43, 44, 45, 49, 65, 80, 97, 98, 99, 100, 101,
          131, 138, 139, 140, 141, 143, 168],                  # Reliance AR FY26 (2-up spreads)
    403: [1, 4, 5, 6, 9, 33, 50, 54, 151, 155, 169, 170, 171, 172,
          173, 174, 177, 178, 210, 228, 238, 280, 321],        # Kaynes AR FY26
    219: None,   # Reliance financial results (1 page)
    719: None,   # AIMTRON audited results (scanned, 12 pages)
    344: None,   # Dixon quarterly results (6 pages)
    220: None,   # Reliance investor presentation (77 pages)
    534: None,   # ADISOFT investor presentation (35 pages)
    218: None,   # Reliance call transcript (32 pages)
    712: None,   # AIMTRON call transcript (27 pages)
    310: None,   # Dixon credit rating (1 page)
}

TEXT_CLASSES = {"text", "title", "section-header", "list-item", "footnote",
                "caption", "page-header", "page-footer", "code"}


def load_doc_meta(db, doc_id):
    db.row_factory = sqlite3.Row
    r = db.execute(
        """SELECT id, exchange, symbol, curated_kind, curated_period, filing_date,
                  reporting_period, retrieval_title, source_url, ingestion_path,
                  ingestion_sha256
           FROM ingestion_documents WHERE id = ?""", (doc_id,)).fetchone()
    if r is None:
        raise SystemExit(f"document {doc_id} is not in ingestion_documents")
    return dict(r)


def box_text(box):
    """Plain text of one layout box."""
    if box.boxclass == "table" and box.table:
        return box.table.get("markdown") or ""
    if box.textlines:
        return dl.text_to_text(box.textlines).strip()
    return ""


def box_record(page_no, idx, box):
    rec = {
        "page": page_no,
        "box": idx,
        "class": box.boxclass,
        "bbox": [round(v, 1) for v in (box.x0, box.y0, box.x1, box.y1)],
        "header_level": box.header_level or None,
        "max_fontsize": box.max_fontsize,
        "text": box_text(box),
    }
    if box.boxclass == "table" and box.table:
        rec["table_rows"] = box.table.get("row_count")
        rec["table_cols"] = box.table.get("col_count")
    return rec


def parse_one(db, doc_id, pages_1based):
    meta = load_doc_meta(db, doc_id)
    out_dir = OUT / f"{doc_id}_{meta['symbol']}_{meta['curated_kind']}"
    out_dir.mkdir(parents=True, exist_ok=True)

    doc = pymupdf.open(meta["ingestion_path"])
    total_pages = doc.page_count
    pages0 = None if pages_1based is None else [p - 1 for p in pages_1based]

    # Wrap the OCR engine so we know exactly which pages were OCR'd
    # (pymupdf4llm does not set PageLayout.full_ocred).
    engine = dl.select_ocr_function()
    ocr_pages = []

    def recording_ocr(page, **kw):
        ocr_pages.append(page.number + 1)
        return engine(page, **kw)

    t0 = time.perf_counter()
    parsed = dl.parse_document(doc, filename=Path(meta["ingestion_path"]).name,
                               pages=pages0, ocr_function=recording_ocr if engine else None)
    page_md = parsed.to_markdown(page_chunks=True)
    secs = time.perf_counter() - t0

    ocr_set = set(ocr_pages)
    md_parts, page_rows, layout_rows = [], [], []
    for pl, chunk in zip(parsed.pages, page_md):
        n = pl.page_number
        md = chunk["text"]
        md_parts.append(f"<!-- page {n} -->\n\n{md.strip()}\n")
        page_rows.append({
            "page": n,
            "ocr_applied": n in ocr_set,
            "chars": len(md),
            "box_classes": dict(Counter(b.boxclass for b in pl.boxes)),
            "markdown": md,
        })
        layout_rows.extend(box_record(n, i, b) for i, b in enumerate(pl.boxes))

    (out_dir / "document.md").write_text("\n".join(md_parts), encoding="utf-8")
    with open(out_dir / "pages.jsonl", "w", encoding="utf-8") as f:
        for r in page_rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    with open(out_dir / "layout.jsonl", "w", encoding="utf-8") as f:
        for r in layout_rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    n_parsed = len(parsed.pages)
    classes = Counter(r["class"] for r in layout_rows)
    run = {
        "parser": "pymupdf4llm",
        "pymupdf4llm_version": version("pymupdf4llm"),
        "layout_mode": True,
        "ocr_engine": getattr(engine, "__module__", None),
        "pdf_page_count": total_pages,
        "pages_parsed": [p.page_number for p in parsed.pages],
        "pages_ocr_applied": sorted(ocr_set),
        "seconds": round(secs, 2),
        "seconds_per_page": round(secs / max(n_parsed, 1), 3),
        "peak_rss_mb": round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024),
        "box_classes": dict(classes),
    }
    (out_dir / "meta.json").write_text(
        json.dumps({"document": meta, "run": run}, indent=2, ensure_ascii=False),
        encoding="utf-8")
    doc.close()

    return {
        "doc_id": doc_id, "symbol": meta["symbol"], "kind": meta["curated_kind"],
        "pdf_pages": total_pages, "pages_parsed": n_parsed,
        "ocr_pages": len(ocr_set), "seconds": run["seconds"],
        "s_per_page": run["seconds_per_page"], "peak_rss_mb": run["peak_rss_mb"],
        "tables": classes.get("table", 0), "pictures": classes.get("picture", 0),
        "headers": classes.get("section-header", 0) + classes.get("title", 0),
        "md_chars": sum(r["chars"] for r in page_rows), "out_dir": out_dir.name,
        "error": "",
    }


def main():
    ids = [int(a) for a in sys.argv[1:]] or list(SAMPLE)
    OUT.mkdir(parents=True, exist_ok=True)
    pymupdf.TOOLS.mupdf_display_errors(False)
    db = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)

    rows = []
    for doc_id in ids:
        print(f"[{doc_id}] parsing ...", flush=True)
        try:
            row = parse_one(db, doc_id, SAMPLE.get(doc_id))
        except Exception as e:  # keep going; record the failure
            row = {"doc_id": doc_id, "error": f"{type(e).__name__}: {e}"}
        print(f"[{doc_id}] {row}", flush=True)
        rows.append(row)

    fields = ["doc_id", "symbol", "kind", "pdf_pages", "pages_parsed", "ocr_pages",
              "seconds", "s_per_page", "peak_rss_mb", "tables", "pictures",
              "headers", "md_chars", "out_dir", "error"]
    summary = OUT / "summary.csv"
    # merge with an existing summary so single-document reruns don't drop rows
    existing = {}
    if summary.exists():
        with open(summary, newline="", encoding="utf-8") as f:
            existing = {int(r["doc_id"]): r for r in csv.DictReader(f)}
    for r in rows:
        existing[int(r["doc_id"])] = r
    with open(summary, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        for doc_id in sorted(existing):
            w.writerow(existing[doc_id])
    print(f"summary -> {summary}")


if __name__ == "__main__":
    main()
