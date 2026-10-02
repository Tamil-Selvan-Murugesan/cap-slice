"""Extract the real intermediate outputs of PyMuPDF4LLM and Docling for one page.

    uv run python tools/explainer_video/extract.py OUT_DIR

Page: E2E FY2022-23 annual report, PDF page 123 (scanned balance sheet).
Writes OUT_DIR/page.png (150 dpi) and OUT_DIR/data.json with everything the
video draws: OCR line boxes, PyMuPDF4LLM layout boxes, Docling layout regions,
Docling table cells, and each parser's Markdown. All coordinates are PDF
points (612 x 792, top-left origin).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

# Use the same OCR package as the measured Option 2 run (rapidocr_onnxruntime):
# PyMuPDF4LLM prefers `rapidocr` when importable (bugs_resolved.md P6).
sys.modules["rapidocr"] = None  # type: ignore[assignment]

import numpy as np  # noqa: E402
import pymupdf  # noqa: E402

REPO = Path(__file__).resolve().parents[2]
PDF = REPO / "data/E2E/annual_reports/2023-09-21_FY2022-23.pdf"
PAGE = 123
DPI = 150


def main(out: Path) -> None:
    out.mkdir(parents=True, exist_ok=True)
    doc = pymupdf.open(PDF)
    page = doc[PAGE - 1]
    pix = page.get_pixmap(dpi=DPI)
    pix.save(out / "page.png")
    scale = 72 / DPI
    data: dict = {"page": PAGE, "size": [page.rect.width, page.rect.height],
                  "text_layer_chars": len(page.get_text().strip()),
                  "images": len(page.get_images())}

    # --- PyMuPDF4LLM step 2: OCR decision ---
    from pymupdf4llm.ocr.analyze_page import analyze_page
    dec = analyze_page(page)
    data["ocr_decision"] = {"needs_ocr": bool(dec["needs_ocr"]), "reason": dec.get("reason"),
                            "probability": round(float(dec.get("probability") or 0), 3)}

    # --- PyMuPDF4LLM step 3: RapidOCR (detection boxes + recognised text) ---
    from rapidocr_onnxruntime import RapidOCR
    img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.h, pix.w, pix.n)[:, :, :3]
    result, _ = RapidOCR()(img)
    data["ocr_lines"] = [{"box": [[x * scale, y * scale] for x, y in box], "text": text,
                          "score": round(float(score), 3)} for box, text, score in (result or [])]

    # --- PyMuPDF4LLM steps 4-5: layout boxes + Markdown ---
    import pymupdf4llm
    chunk = pymupdf4llm.to_markdown(str(PDF), pages=[PAGE - 1], page_chunks=True,
                                    header=False, footer=False, use_ocr=True)[0]
    data["p4l_boxes"] = [{"cls": b.get("class"), "bbox": list(b.get("bbox"))}
                         for b in chunk.get("page_boxes", [])]
    data["p4l_markdown"] = chunk["text"]

    # --- Docling: layout regions, OCR'd cells, table structure, Markdown ---
    # Docling's own OCR needs the `rapidocr` package blocked above for PyMuPDF4LLM.
    del sys.modules["rapidocr"]
    from docling.datamodel.base_models import InputFormat
    from docling.datamodel.pipeline_options import AcceleratorOptions, PdfPipelineOptions
    from docling.document_converter import DocumentConverter, PdfFormatOption
    opts = PdfPipelineOptions()
    opts.accelerator_options = AcceleratorOptions(device="cpu")
    conv = DocumentConverter(format_options={InputFormat.PDF: PdfFormatOption(pipeline_options=opts)})
    res = conv.convert(str(PDF), page_range=(PAGE, PAGE))
    pg = res.pages[0]
    data["dl_regions"] = []
    for c in pg.predictions.layout.clusters:
        ocr_cells = [x for x in c.cells if getattr(x, "from_ocr", False)]
        data["dl_regions"].append({"label": c.label.value, "bbox": list(c.bbox.as_tuple()),
                                   "confidence": round(float(c.confidence), 3),
                                   "ocr_cells": [list(x.rect.to_bounding_box().as_tuple())
                                                 for x in ocr_cells]})
    tables = list(pg.predictions.tablestructure.table_map.values())
    data["dl_tables"] = [{"rows": t.num_rows, "cols": t.num_cols, "bbox": list(t.cluster.bbox.as_tuple()),
                          "cells": [{"bbox": list(c.bbox.as_tuple()), "row": c.start_row_offset_idx,
                                     "col": c.start_col_offset_idx, "text": c.text,
                                     "header": bool(c.column_header)} for c in t.table_cells]}
                         for t in tables]
    data["dl_markdown"] = res.document.export_to_markdown(page_no=PAGE)
    (out / "data.json").write_text(json.dumps(data, indent=1))
    print("ocr lines", len(data["ocr_lines"]), "| p4l boxes", len(data["p4l_boxes"]),
          "| dl regions", len(data["dl_regions"]), "| dl tables",
          [(t["rows"], t["cols"], len(t["cells"])) for t in data["dl_tables"]],
          "| dl ocr cells", sum(len(r["ocr_cells"]) for r in data["dl_regions"]))


if __name__ == "__main__":
    main(Path(sys.argv[1]))
