"""Extract text from downloaded PDFs, page by page."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

import pymupdf

# Pages with less text than this are treated as scanned images (no text layer).
MIN_PAGE_CHARS = 50


@dataclass
class Page:
    number: int  # 1-based, as printed in a PDF viewer
    text: str


@dataclass
class ExtractedDoc:
    pages: list[Page]  # pages with usable text only
    page_count: int
    scanned_pages: list[int]  # 1-based numbers of pages with no text layer

    @property
    def needs_ocr(self) -> bool:
        return self.page_count > 0 and len(self.scanned_pages) / self.page_count > 0.5


def clean(text: str) -> str:
    text = text.replace("\x00", "")
    text = re.sub(r"-\n(?=[a-z])", "", text)  # re-join hyphenated line breaks
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def extract_pdf(path: Path) -> ExtractedDoc:
    pages, scanned = [], []
    with pymupdf.open(path) as doc:
        for i, page in enumerate(doc, 1):
            text = clean(page.get_text("text", sort=True))
            if len(text) < MIN_PAGE_CHARS:
                scanned.append(i)
            else:
                pages.append(Page(i, text))
        return ExtractedDoc(pages, doc.page_count, scanned)
