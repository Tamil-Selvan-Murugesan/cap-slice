"""Option 1: PyMuPDF plain text, keeping line structure.

``get_text(sort=True)`` lays text out roughly as on the page, with runs of
spaces between table columns. Instead of collapsing those (as the baseline
does), a gap of 3+ spaces becomes a ``|`` cell boundary, so each table row
stays one line with its cells separated. No OCR.
"""

from __future__ import annotations

import re
from pathlib import Path

import pymupdf

from cap_slice.parsing import ParsedPage

COLUMN_GAP = re.compile(r"\s{3,}")


def _line(line: str) -> str:
    line = line.strip()
    cells = [re.sub(r"\s+", " ", c) for c in COLUMN_GAP.split(line) if c]
    # A table row: 2+ cells, a number in some cell after the first, and no cell
    # that is a run of prose (two-column transcripts and designed pages also
    # have wide gaps, but their "cells" are sentences, not values).
    if (len(cells) >= 2 and any(re.search(r"\d", c) for c in cells[1:])
            and max(len(c.split()) for c in cells) <= 25):
        return "| " + " | ".join(cells) + " |"
    if len(cells) >= 2:
        line = " ".join(cells)
    line = re.sub(r"\s+", " ", line)
    words = line.split()
    # Short ALL-CAPS lines are almost always section titles in filings.
    if 1 < len(words) <= 12 and line.upper() == line and re.search(r"[A-Z]{3}", line):
        return f"## {line}"
    return line


def _absorb_row_labels(lines: list[str]) -> list[str]:
    """Short label lines between table rows ("Current assets") are table rows too.

    Without this, every sub-heading inside a financial statement splits the
    table into pieces and only the first piece keeps the column headers.
    """
    rows = [i for i, l in enumerate(lines) if l.startswith("| ")]
    out = list(lines)
    for i, l in enumerate(lines):
        if not l or l.startswith("| ") or len(l.lstrip("# ").split()) > 8 or l.rstrip().endswith("."):
            continue
        above = any(0 < i - r <= 3 for r in rows)
        below = any(0 < r - i <= 3 for r in rows)
        if above and below:
            out[i] = "| " + l.lstrip("# ") + " |"
    # Blank lines inside a table would split it into separate blocks.
    return [l for i, l in enumerate(out)
            if l or not (0 < i < len(out) - 1 and out[i - 1].startswith("| ")
                         and out[i + 1].startswith("| "))]


def parse(path: Path) -> list[ParsedPage]:
    pages = []
    with pymupdf.open(path) as doc:
        for i, page in enumerate(doc, 1):
            raw = page.get_text("text", sort=True).replace("\x00", "")
            raw = re.sub(r"-\n(?=[a-z])", "", raw)
            lines = _absorb_row_labels([_line(l) if l.strip() else "" for l in raw.splitlines()])
            text = re.sub(r"\n{3,}", "\n\n", "\n".join(lines)).strip()
            pages.append(ParsedPage(i, text))
    return pages
