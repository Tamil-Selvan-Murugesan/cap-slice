"""
Build the vision-model test pack: only the hard pages from the 10-document sample.

Output (<data>/sets/vlm_test_pack/pack/, zipped to <data>/sets/vlm_test_pack/vlm_test_pack.zip):
  pdfs/<doc_id>_<symbol>_<kind>.pdf   subset PDF of the selected pages (pack order)
  images/<doc_id>_p<NNN>.png          each selected page rendered at 200 DPI
  manifest.json                       pages, why each was chosen, what to check
  README.md                           how to run the test and what to report

Page numbers (p<NNN>) are 1-based pages of the ORIGINAL PDF, so model outputs can
be compared against the baseline outputs and eval_set/questions.json directly.
Read-only with respect to cap-slice (SQLite mode=ro).

Run:
  python parsing_eval/sets/build_pack.py
"""
import json
import shutil
import sqlite3
from pathlib import Path

import pymupdf

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # parsing_eval/ (paths.py)
from paths import DB_PATH, PACK, QUESTIONS  # noqa: E402

HERE = Path(__file__).resolve().parent
DPI = 200

# doc_id -> {page: (category, why it is hard, what to check)}
PAGES = {
    719: {
        2: ("scanned_table", "Scanned image, no text layer. P&L with 4 period columns.",
            "Decimals kept (146.49 not 14649); each value on its own row; H2 vs year columns."),
        3: ("scanned_table", "Scanned balance sheet; wrapped labels share rows.",
            "49.06 on '(a) Short term borrowings'; 6,110.35 on 'Other current liabilities'; 8.34 not 'B.34'."),
        4: ("scanned_table", "Scanned cash-flow statement with nested sections.",
            "Section headers kept; negative values keep the sign/brackets as printed; no merged rows."),
    },
    344: {
        1: ("bad_text_layer", "Scan with an old OCR text layer (PaperStream + Acrobat Paper Capture).",
            "Clean words ('Listing Department', 'ISIN'), not the embedded OCR text."),
        3: ("bad_text_layer", "Standalone results; embedded OCR gives 'S,81,695', '{12,917)', 'I'.",
            "5,81,695; (12,917); expense block rows aligned across 6 period columns."),
        6: ("bad_text_layer", "Consolidated results; same layout as page 3, title garbled in text layer.",
            "Title read as CONSOLIDATED; values distinct from the standalone page."),
    },
    310: {
        1: ("bad_text_layer", "Rating letter scan; embedded OCR reads A1+ as 'Al+'.",
            "[ICRA]A1+ (digit one) for Short Term and Commercial Paper; signatory 'Ashish Kumar'."),
    },
    534: {
        26: ("kpi_tiles", "KPI tiles with values, deltas and comparisons in separate text boxes.",
             "Each value paired with its label and comparison (e.g. 19.09 vs 13.45 diluted EPS)."),
        27: ("chart", "Three bar/line charts; all numbers are inside chart images.",
             "Per-year values for Total Income, EBITDA, EBITDA margin, PAT, PAT margin (FY23-FY26)."),
        28: ("chart", "Net-worth bar chart + KPI tiles + callout box.",
             "Net worth by year (21, 33, 49, 72); tiles 72.3 Cr, 0.30x, 29.4 Cr, 18.2x."),
        31: ("chart", "Eight small charts of ratios, units differ per chart (% / times / days / Rs).",
             "Value per year per ratio with the right unit (e.g. ROE FY24 34.81%)."),
    },
    220: {
        20: ("chart", "Two bar charts; text extraction gives an unordered bag of numbers.",
             "Revenue and EBITDA mapped to Jun-25..Jun-26; margins 56.0% / 57.3% attached to the right bars."),
        65: ("chart_and_table", "Table plus bar chart on one slide.",
             "KGD6 59.2 BCFe Q1 FY27, (7.4)% YoY; chart 26.6 / 25.2 / 24.8 MMSCMD by quarter."),
    },
    1: {
        98: ("layout", "Born-digital, 2-up spread; EPS rows and signatory grid get garbled.",
             "Basic/Diluted EPS 32.40 (FY26) and 26.06 (FY25); note '32' separate; Rs symbol (not 'H')."),
    },
    712: {
        7: ("layout", "Born-digital transcript laid out as speaker | text columns.",
            "Each answer attributed to the right speaker (Ashutosh Shukla asks, Mukesh Vasani answers)."),
    },
}


def copy_pages(src, pages_0based):
    """Copy pages into a new PDF, keeping form fields/signature appearances. Some filings
    have broken form-field xrefs (e.g. doc 1); only for those are widgets dropped."""
    for widgets in (True, False):
        sub = pymupdf.open()
        try:
            for p in pages_0based:
                sub.insert_pdf(src, from_page=p, to_page=p, widgets=widgets)
            return sub, widgets
        except Exception:
            sub.close()
    raise RuntimeError(f"could not copy pages from {src.name}")


def main():
    db = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
    db.row_factory = sqlite3.Row
    if PACK.exists():
        shutil.rmtree(PACK)
    PACK.parent.mkdir(parents=True, exist_ok=True)
    (PACK / "pdfs").mkdir(parents=True)
    (PACK / "images").mkdir()

    manifest = {"dpi": DPI, "page_numbering": "1-based pages of the original PDF", "documents": []}
    for doc_id, pages in PAGES.items():
        meta = dict(db.execute(
            """SELECT id, exchange, symbol, curated_kind, curated_period, filing_date,
                      retrieval_title, source_url, ingestion_path, ingestion_sha256
               FROM ingestion_documents WHERE id = ?""", (doc_id,)).fetchone())
        src = pymupdf.open(meta["ingestion_path"])
        stem = f"{doc_id}_{meta['symbol']}_{meta['curated_kind']}"

        sub, _ = copy_pages(src, [p - 1 for p in sorted(pages)])
        entries = []
        for pack_no, page in enumerate(sorted(pages), 1):
            img = f"images/{doc_id}_p{page:03d}.png"
            src[page - 1].get_pixmap(dpi=DPI).save(PACK / img)
            category, why, check = pages[page]
            entries.append({"pdf_page": page, "pack_page": pack_no, "image": img,
                            "category": category, "why_hard": why, "check": check})
        sub.save(PACK / "pdfs" / f"{stem}.pdf", garbage=3, deflate=True)
        sub.close()
        src.close()

        meta.pop("ingestion_path")
        manifest["documents"].append({**meta, "pdf": f"pdfs/{stem}.pdf", "pages": entries})

    (PACK / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False),
                                        encoding="utf-8")
    shutil.copy(HERE / "vlm_test_pack_README.md", PACK / "README.md")
    shutil.copy(QUESTIONS, PACK / "questions.json")
    archive = shutil.make_archive(str(PACK.parent / "vlm_test_pack"), "zip", PACK)

    n_pages = sum(len(d["pages"]) for d in manifest["documents"])
    print(f"{len(manifest['documents'])} documents, {n_pages} pages -> {PACK}")
    print(f"zip -> {archive} ({Path(archive).stat().st_size / 1e6:.1f} MB)")


if __name__ == "__main__":
    main()
