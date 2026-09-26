"""PDF parsers under comparison. Each returns one Markdown-ish string per page.

- ``pymupdf_text``: PyMuPDF plain text, with column gaps turned into ``|`` cells
  and ALL-CAPS short lines marked as headings (Option 1).
- ``pymupdf4llm``: PyMuPDF4LLM layout mode, Markdown tables, RapidOCR (Option 2).
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable


@dataclass
class ParsedPage:
    number: int  # 1-based PDF page number
    text: str


def get_parser(name: str) -> Callable[[Path], list[ParsedPage]]:
    if name == "pymupdf_text":
        from cap_slice.parsing.pymupdf_text import parse
    elif name == "pymupdf4llm":
        from cap_slice.parsing.pymupdf4llm_md import parse
    else:
        raise ValueError(f"unknown parser {name!r}")
    return parse
