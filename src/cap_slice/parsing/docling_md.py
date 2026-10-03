"""Option 3: Docling -> Markdown per page (plus the lossless Docling JSON).

Docling runs a layout model and TableFormer (table structure, ACCURATE mode)
on every page, and OCR (engine chosen automatically; RapidOCR here) on bitmap
regions. Page headers/footers are excluded by Docling's default content
layers, like PyMuPDF4LLM's header=False/footer=False.

Device: ``CAP_SLICE_DEVICE`` (default ``cpu``; ``cuda`` or ``auto`` on a GPU).
Batch sizes: ``CAP_SLICE_DOCLING_BATCH`` sets Docling's OCR/layout/table batch
sizes (default 4, Docling's own default) — larger values help on a GPU.
"""

from __future__ import annotations

import json
import os
import os
from functools import cache
from pathlib import Path

from cap_slice.parsing import ParsedPage, ParseOutput


@cache
def _converter(device: str, batch: int):
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
    if device != "cpu":
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


def parse_full(path: Path) -> ParseOutput:
    device, batch = _settings()
    result = _converter(device, batch).convert(str(path))
    doc = result.document
    pages = [ParsedPage(n, doc.export_to_markdown(page_no=n).strip()) for n in sorted(doc.pages)]
    timings = {k: round(sum(v.times), 3) for k, v in (getattr(result, "timings", None) or {}).items()}
    return ParseOutput(pages, raw={"docling.json": json.dumps(doc.export_to_dict())},
                       info={"device": device, "batch_size": batch, "stage_seconds": timings})


def parse(path: Path) -> list[ParsedPage]:
    return parse_full(path).pages
