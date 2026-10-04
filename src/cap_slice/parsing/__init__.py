"""PDF parsers under comparison. Each returns one Markdown-ish string per page.

- ``baseline``: the indexing pipeline's extract.py (PyMuPDF text, low-text pages dropped).
- ``pymupdf_text``: PyMuPDF plain text, with column gaps turned into ``|`` cells
  and ALL-CAPS short lines marked as headings (Option 1).
- ``pymupdf4llm``: PyMuPDF4LLM layout mode, Markdown tables, RapidOCR (Option 2).
- ``docling``: Docling layout model + TableFormer + OCR (Option 3).
- ``mineru``: MinerU2.5-Pro vision-language model via a MinerU VLM server (Option 4).
- ``paddleocr_vl``: PaddleOCR-VL-1.6, layout model + 0.9B VLM on a vLLM server (Option 5).

``get_parser`` returns per-page text only (used by compare_parsers.py).
``get_full_parser`` also returns the parser's raw, lossless output files, which
the batch runner saves next to the per-page text so nothing has to be re-parsed.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

PARSERS = ("baseline", "pymupdf_text", "pymupdf4llm", "docling", "mineru", "paddleocr_vl")


@dataclass
class ParsedPage:
    number: int  # 1-based PDF page number
    text: str


@dataclass
class ParseOutput:
    pages: list[ParsedPage]
    # file name -> content (text or bytes), saved as-is next to pages.json
    raw: dict[str, str | bytes] = field(default_factory=dict)
    # parser-specific facts worth logging (versions, settings, stage timings)
    info: dict = field(default_factory=dict)


def get_parser(name: str) -> Callable[[Path], list[ParsedPage]]:
    if name == "pymupdf_text":
        from cap_slice.parsing.pymupdf_text import parse
    elif name == "pymupdf4llm":
        from cap_slice.parsing.pymupdf4llm_md import parse
    elif name == "docling":
        from cap_slice.parsing.docling_md import parse
    else:
        raise ValueError(f"unknown parser {name!r}")
    return parse


def get_full_parser(name: str) -> Callable[[Path], ParseOutput]:
    if name == "docling":
        from cap_slice.parsing.docling_md import parse_full
        return parse_full
    if name == "pymupdf4llm":
        from cap_slice.parsing.pymupdf4llm_md import parse_full
        return parse_full
    if name == "mineru":
        from cap_slice.parsing.mineru_vlm import parse_full
        return parse_full
    if name == "paddleocr_vl":
        from cap_slice.parsing.paddleocr_vl import parse_full
        return parse_full
    if name == "baseline":
        from cap_slice.extract import extract_pdf

        def parse_baseline(path: Path) -> ParseOutput:
            doc = extract_pdf(path)
            return ParseOutput([ParsedPage(p.number, p.text) for p in doc.pages])
        return parse_baseline
    simple = get_parser(name)
    return lambda path: ParseOutput(simple(path))
