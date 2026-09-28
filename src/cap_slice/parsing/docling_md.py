"""Option 3: Docling -> Markdown per page.

Docling runs a layout model and TableFormer (table structure, ACCURATE mode)
on every page, and OCR (engine chosen automatically; RapidOCR here) on bitmap
regions. CPU-only PyTorch. Page headers/footers are excluded by Docling's
default content layers, like PyMuPDF4LLM's header=False/footer=False.
"""

from __future__ import annotations

from functools import cache
from pathlib import Path

from cap_slice.parsing import ParsedPage


@cache
def _converter():
    from docling.datamodel.base_models import InputFormat
    from docling.datamodel.pipeline_options import AcceleratorOptions, PdfPipelineOptions
    from docling.document_converter import DocumentConverter, PdfFormatOption

    # Docling as shipped: OCR on, TableFormer ACCURATE, 4 threads. 8 threads was
    # measured slower on this laptop (66 s vs 53 s on the 4-page C2C doc); OCR
    # is ~2/3 of the time there (19 s with do_ocr=False).
    opts = PdfPipelineOptions()
    opts.accelerator_options = AcceleratorOptions(device="cpu")
    return DocumentConverter(format_options={InputFormat.PDF: PdfFormatOption(pipeline_options=opts)})


def parse(path: Path) -> list[ParsedPage]:
    doc = _converter().convert(str(path)).document
    return [ParsedPage(n, doc.export_to_markdown(page_no=n).strip())
            for n in sorted(doc.pages)]
