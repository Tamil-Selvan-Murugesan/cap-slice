"""Option 2: PyMuPDF4LLM in layout mode -> Markdown per page.

Layout mode (pymupdf-layout, an ONNX model) classifies page regions; tables
come out as Markdown tables. Pages without a text layer are OCR'd with
RapidOCR (onnxruntime, CPU). No PyTorch needed.
"""

from __future__ import annotations

from pathlib import Path

import pymupdf4llm

from cap_slice.parsing import ParsedPage


def parse(path: Path) -> list[ParsedPage]:
    chunks = pymupdf4llm.to_markdown(
        str(path), page_chunks=True, header=False, footer=False,
        use_ocr=True, show_progress=False,
    )
    return [ParsedPage(c["metadata"]["page_number"], c["text"].strip()) for c in chunks]
