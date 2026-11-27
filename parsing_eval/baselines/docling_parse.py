"""
Parse the 10-document evaluation sample with Docling (layout + TableFormer + RapidOCR).

Same sample, page subsets and output layout as baselines/pymupdf4llm_parse.py so
the two can be compared page by page. Read-only with respect to cap-slice: SQLite
is opened with mode=ro and source PDFs are only read.

Per document (output/<doc_id>_<symbol>_<kind>/):
  document.md    markdown of all parsed pages, each preceded by <!-- page N -->
  pages.jsonl    one row per page: markdown and item-label counts
  layout.jsonl   one row per item: page, label, bbox (top-left origin), heading
                 level, text, table shape
  docling.json   the full lossless DoclingDocument
  meta.json      document metadata from SQLite + timing/memory for this run
Plus output/summary.csv across documents.

OCR mode: Docling's default -- programmatic text is read from the PDF text layer
and OCR runs on bitmap regions only (force_full_page_ocr=False). This matches
pymupdf4llm's default, so the comparison is like for like.

Page numbers are 1-based PDF page indices of the ORIGINAL file. Annual-report
subsets are first copied into a temporary PDF; page numbers are mapped back.

Run:
  python parsing_eval/baselines/docling_parse.py [doc_id ...] [--force-ocr]
  (separate venv: torch CPU + docling + rapidocr; see parsing_eval/requirements.txt)
Outputs: <data>/baselines/docling_output/ (or docling_force_ocr_output/), see paths.py.
"""
import csv
import json
import resource
import sqlite3
import sys
import tempfile
import time
from collections import Counter
from importlib.metadata import version
from pathlib import Path

import pypdfium2 as pdfium
from docling.datamodel.accelerator_options import AcceleratorDevice, AcceleratorOptions
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import (
    PdfPipelineOptions, RapidOcrOptions, TableFormerMode,
)
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling_core.types.doc import DocItem, SectionHeaderItem, TableItem

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # parsing_eval/ (paths.py)
from paths import BASELINES, DB_PATH  # noqa: E402

OUT = BASELINES / "docling_output"
# --force-ocr: ignore the PDF text layer and OCR every page (separate output dir)
FORCE_OCR = "--force-ocr" in sys.argv
if FORCE_OCR:
    OUT = BASELINES / "docling_force_ocr_output"

# Keep identical to baselines/pymupdf4llm_parse.py
SAMPLE = {
    1:   [41, 42, 43, 44, 45, 49, 65, 80, 97, 98, 99, 100, 101,
          131, 138, 139, 140, 141, 143, 168],                  # Reliance AR FY26 (2-up spreads)
    403: [1, 4, 5, 6, 9, 33, 50, 54, 151, 155, 169, 170, 171, 172,
          173, 174, 177, 178, 210, 228, 238, 280, 321],        # Kaynes AR FY26
    219: None, 719: None, 344: None, 220: None,
    534: None, 218: None, 712: None, 310: None,
}


def make_converter():
    opts = PdfPipelineOptions()
    opts.do_ocr = True
    opts.ocr_options = RapidOcrOptions(force_full_page_ocr=FORCE_OCR)  # same engine family as the pymupdf4llm run
    opts.do_table_structure = True
    opts.table_structure_options.mode = TableFormerMode.ACCURATE
    opts.table_structure_options.do_cell_matching = True
    opts.accelerator_options = AcceleratorOptions(num_threads=8, device=AcceleratorDevice.CPU)
    conv = DocumentConverter(format_options={InputFormat.PDF: PdfFormatOption(pipeline_options=opts)})
    conv.initialize_pipeline(InputFormat.PDF)     # load models before timing anything
    return conv


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


def subset_pdf(src, pages_1based, dst):
    """Copy the selected pages into dst; return [original page no. for each new page]."""
    src_pdf = pdfium.PdfDocument(src)
    new = pdfium.PdfDocument.new()
    new.import_pages(src_pdf, [p - 1 for p in pages_1based])
    new.save(dst)
    new.close()
    src_pdf.close()
    return list(pages_1based)


def item_record(doc, item, level, page_map):
    prov = item.prov[0] if item.prov else None
    page = page_map[prov.page_no - 1] if prov else None
    bbox = None
    if prov:
        h = doc.pages[prov.page_no].size.height
        b = prov.bbox.to_top_left_origin(page_height=h)
        bbox = [round(v, 1) for v in (b.l, b.t, b.r, b.b)]
    rec = {
        "page": page,
        "label": str(item.label.value if hasattr(item.label, "value") else item.label),
        "bbox": bbox,
        "tree_level": level,
        "heading_level": item.level if isinstance(item, SectionHeaderItem) else None,
        "text": getattr(item, "text", "") or "",
        "n_prov": len(item.prov),
    }
    if isinstance(item, TableItem):
        rec["text"] = item.export_to_markdown(doc=doc)
        rec["table_rows"] = item.data.num_rows
        rec["table_cols"] = item.data.num_cols
    return rec


def parse_one(conv, db, doc_id, pages_1based):
    meta = load_doc_meta(db, doc_id)
    out_dir = OUT / f"{doc_id}_{meta['symbol']}_{meta['curated_kind']}"
    out_dir.mkdir(parents=True, exist_ok=True)

    src = meta["ingestion_path"]
    pdf_page_count = len(pdfium.PdfDocument(src))
    with tempfile.TemporaryDirectory() as tmp:
        if pages_1based:
            path = str(Path(tmp) / "subset.pdf")
            page_map = subset_pdf(src, pages_1based, path)
        else:
            path = src
            page_map = list(range(1, pdf_page_count + 1))

        t0 = time.perf_counter()
        res = conv.convert(path, raises_on_error=False)
        secs = time.perf_counter() - t0
    doc = res.document

    layout_rows = [item_record(doc, it, lvl, page_map)
                   for it, lvl in doc.iterate_items() if isinstance(it, DocItem)]

    md_parts, page_rows = [], []
    for new_no in sorted(doc.pages):
        orig = page_map[new_no - 1]
        md = doc.export_to_markdown(page_no=new_no)
        md_parts.append(f"<!-- page {orig} -->\n\n{md.strip()}\n")
        page_rows.append({
            "page": orig,
            "chars": len(md),
            "labels": dict(Counter(r["label"] for r in layout_rows if r["page"] == orig)),
            "markdown": md,
        })

    (out_dir / "document.md").write_text("\n".join(md_parts), encoding="utf-8")
    with open(out_dir / "pages.jsonl", "w", encoding="utf-8") as f:
        for r in page_rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    with open(out_dir / "layout.jsonl", "w", encoding="utf-8") as f:
        for r in layout_rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    doc.save_as_json(out_dir / "docling.json")

    n_parsed = len(doc.pages)
    labels = Counter(r["label"] for r in layout_rows)
    errors = [str(e.error_message) for e in (res.errors or [])]
    run = {
        "parser": "docling",
        "docling_version": version("docling"),
        "status": str(res.status),
        "ocr": "RapidOCR, full page" if FORCE_OCR else "RapidOCR, bitmap regions only",
        "table_mode": "accurate",
        "pdf_page_count": pdf_page_count,
        "pages_parsed": [page_map[p - 1] for p in sorted(doc.pages)],
        "seconds": round(secs, 2),
        "seconds_per_page": round(secs / max(n_parsed, 1), 3),
        "peak_rss_mb": round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024),
        "labels": dict(labels),
        "errors": errors,
    }
    (out_dir / "meta.json").write_text(
        json.dumps({"document": meta, "run": run}, indent=2, ensure_ascii=False),
        encoding="utf-8")

    return {
        "doc_id": doc_id, "symbol": meta["symbol"], "kind": meta["curated_kind"],
        "pdf_pages": pdf_page_count, "pages_parsed": n_parsed,
        "seconds": run["seconds"], "s_per_page": run["seconds_per_page"],
        "peak_rss_mb": run["peak_rss_mb"],
        "tables": labels.get("table", 0), "pictures": labels.get("picture", 0),
        "headers": labels.get("section_header", 0) + labels.get("title", 0),
        "md_chars": sum(r["chars"] for r in page_rows), "out_dir": out_dir.name,
        "status": run["status"], "error": "; ".join(errors)[:300],
    }


def main():
    ids = [int(a) for a in sys.argv[1:] if not a.startswith("--")] or list(SAMPLE)
    OUT.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)

    t0 = time.perf_counter()
    conv = make_converter()
    print(f"models loaded in {time.perf_counter() - t0:.1f}s", flush=True)

    rows = []
    for doc_id in ids:
        print(f"[{doc_id}] parsing ...", flush=True)
        try:
            row = parse_one(conv, db, doc_id, SAMPLE.get(doc_id))
        except Exception as e:  # keep going; record the failure
            row = {"doc_id": doc_id, "error": f"{type(e).__name__}: {e}"}
        print(f"[{doc_id}] {row}", flush=True)
        rows.append(row)

    fields = ["doc_id", "symbol", "kind", "pdf_pages", "pages_parsed", "seconds",
              "s_per_page", "peak_rss_mb", "tables", "pictures", "headers",
              "md_chars", "out_dir", "status", "error"]
    summary = OUT / "summary.csv"
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
