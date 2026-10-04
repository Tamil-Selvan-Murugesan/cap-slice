"""Option 3: Docling -> Markdown per page (plus the lossless Docling JSON).

Docling runs a layout model and TableFormer (table structure, ACCURATE mode)
on every page, and OCR (engine chosen automatically; RapidOCR here) on bitmap
regions. Page headers/footers are excluded by Docling's default content
layers, like PyMuPDF4LLM's header=False/footer=False.

Device: ``CAP_SLICE_DEVICE`` (default ``cpu``; ``cuda`` or ``auto`` on a GPU).
Batch sizes: ``CAP_SLICE_DOCLING_BATCH`` sets Docling's OCR/layout/table batch
sizes (default 4, Docling's own default) — larger values help on a GPU.

OCR routing: ``CAP_SLICE_DOCLING_OCR`` = ``auto`` (default) | ``on`` | ``off``.
Docling 2.130 has no page-level "digital vs scanned" switch: with OCR on it OCRs
every layout region overlapping a bitmap *or a vector shape* — every ruled table
on a digital page — so OCR was 90-97 % of its time. ``auto`` classifies each
page with PyMuPDF (instant) and converts runs of consecutive pages with the same
route: OCR on for pages with < ``CAP_SLICE_DOCLING_MIN_CHARS`` (50, as extract.py)
characters of text or >= ``CAP_SLICE_DOCLING_SCAN_COVERAGE`` (0.75) of the page
covered by images; OCR off (the PDF's own text) for the rest. Cost: text inside
pictures on digital pages is not read. ``on`` = Docling as shipped (the runs up
to the 2026-10-04 tune).
"""

from __future__ import annotations

import json
import os
from functools import cache
from pathlib import Path

from cap_slice.parsing import ParsedPage, ParseOutput


@cache
def _converter(device: str, batch: int, ocr: bool = True):
    from docling.datamodel.base_models import InputFormat
    from docling.datamodel.pipeline_options import AcceleratorOptions, PdfPipelineOptions
    from docling.datamodel.settings import settings
    from docling.document_converter import DocumentConverter, PdfFormatOption

    settings.debug.profile_pipeline_timings = True  # per-stage seconds in meta.json

    # Docling as shipped: OCR on, TableFormer ACCURATE, 4 threads. On the laptop
    # 8 threads was measured slower (66 s vs 53 s on the 4-page C2C doc); OCR
    # was ~2/3 of the time there (19 s with do_ocr=False).
    opts = PdfPipelineOptions()
    opts.accelerator_options = AcceleratorOptions(device=device)
    opts.do_ocr = ocr
    if ocr and device != "cpu":
        # OCR on GPU: RapidOCR configures ONNX Runtime with an EXHAUSTIVE cuDNN
        # algorithm search, re-run for every new image shape — and OCR crops come in
        # every shape, so it searched more than it read (4 pages: 105 s on the GPU vs
        # 23.5 s on CPU, RunPod RTX 5090). DEFAULT skips the search.
        from docling.datamodel.pipeline_options import RapidOcrOptions
        opts.ocr_options = RapidOcrOptions(rapidocr_params={
            "EngineConfig.onnxruntime.cuda_ep_cfg.cudnn_conv_algo_search":
                os.environ.get("CAP_SLICE_OCR_ALGO_SEARCH", "DEFAULT")})
    opts.ocr_batch_size = opts.layout_batch_size = opts.table_batch_size = batch
    return DocumentConverter(format_options={InputFormat.PDF: PdfFormatOption(pipeline_options=opts)})


def _settings() -> tuple[str, int]:
    return os.environ.get("CAP_SLICE_DEVICE", "cpu"), int(os.environ.get("CAP_SLICE_DOCLING_BATCH", "4"))


def ocr_pages(path: Path) -> list[bool]:
    """Per page (in order): True = needs OCR (little/no text layer, or mostly image)."""
    import pymupdf
    min_chars = int(os.environ.get("CAP_SLICE_DOCLING_MIN_CHARS", "50"))
    coverage = float(os.environ.get("CAP_SLICE_DOCLING_SCAN_COVERAGE", "0.75"))
    need = []
    with pymupdf.open(path) as doc:
        for page in doc:
            area = abs(page.rect) or 1.0
            img = sum(abs(pymupdf.Rect(i["bbox"]) & page.rect) for i in page.get_image_info())
            need.append(len(page.get_text().strip()) < min_chars or img / area >= coverage)
    return need


def _runs(flags: list[bool]) -> list[tuple[int, int, bool]]:
    """Consecutive pages with the same route: (first, last, ocr), 1-based inclusive."""
    runs: list[tuple[int, int, bool]] = []
    for i, f in enumerate(flags, 1):
        if runs and runs[-1][2] == f:
            runs[-1] = (runs[-1][0], i, f)
        else:
            runs.append((i, i, f))
    return runs


def parse_full(path: Path) -> ParseOutput:
    device, batch = _settings()
    mode = os.environ.get("CAP_SLICE_DOCLING_OCR", "auto")
    if mode in ("on", "off"):
        import pymupdf
        with pymupdf.open(path) as d:
            n = d.page_count
        runs = [(1, n, mode == "on")]
    else:
        runs = _runs(ocr_pages(path))
    pages: list[ParsedPage] = []
    timings: dict[str, float] = {}
    docs = []
    for first, last, ocr in runs:
        result = _converter(device, batch, ocr).convert(str(path), page_range=(first, last))
        doc = result.document
        pages += [ParsedPage(n, doc.export_to_markdown(page_no=n).strip()) for n in sorted(doc.pages)]
        for k, v in (getattr(result, "timings", None) or {}).items():
            timings[k] = round(timings.get(k, 0.0) + sum(v.times), 3)
        docs.append({"first_page": first, "last_page": last, "ocr": ocr, "doc": doc.export_to_dict()})
    # one run (whole document, one route) keeps the plain Docling JSON as before
    raw = json.dumps(docs[0]["doc"] if len(docs) == 1 else {"runs": docs})
    ocr_list = [p for f, l, o in runs if o for p in range(f, l + 1)]
    return ParseOutput(pages, raw={"docling.json": raw},
                       info={"device": device, "batch_size": batch, "stage_seconds": timings,
                             "ocr_mode": mode, "ocr_pages": ocr_list, "runs": len(runs)})


def parse(path: Path) -> list[ParsedPage]:
    return parse_full(path).pages
