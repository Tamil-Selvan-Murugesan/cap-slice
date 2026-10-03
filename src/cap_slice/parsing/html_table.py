"""Convert an HTML table to a Markdown pipe table.

Merged cells are expanded onto a grid: a ``colspan``/``rowspan`` cell's text is
repeated in every grid position it covers. That keeps every row the same width,
so a value and its column header line up when counted from the right — which is
what structure_chunk.py and the golden-set scorer rely on — and a grouped
header like "As at March 31, 2024" spanning two sub-columns stays above both.
Header rows (``<th>`` or ``<thead>``) are followed by the ``|---|`` separator.
"""

from __future__ import annotations

import re
from html.parser import HTMLParser


class _Collector(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.rows: list[list[tuple[str, int, int, bool]]] = []  # (text, colspan, rowspan, is_th)
        self.header_rows: set[int] = set()
        self._in_thead = False
        self._cell: list[str] | None = None
        self._attrs: tuple[int, int, bool] = (1, 1, False)

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "thead":
            self._in_thead = True
        elif tag == "tr":
            self.rows.append([])
            if self._in_thead:
                self.header_rows.add(len(self.rows) - 1)
        elif tag in ("td", "th"):
            if not self.rows:
                self.rows.append([])
            self._cell = []
            self._attrs = (_int(a.get("colspan")), _int(a.get("rowspan")), tag == "th")
        elif tag == "br" and self._cell is not None:
            self._cell.append(" ")

    def handle_endtag(self, tag):
        if tag == "thead":
            self._in_thead = False
        elif tag in ("td", "th") and self._cell is not None:
            text = re.sub(r"\s+", " ", "".join(self._cell)).strip().replace("|", "/")
            self.rows[-1].append((text, *self._attrs))
            self._cell = None

    def handle_data(self, data):
        if self._cell is not None:
            self._cell.append(data)


def _int(v) -> int:
    try:
        return max(1, int(v))
    except (TypeError, ValueError):
        return 1


def html_table_to_markdown(html: str) -> str:
    c = _Collector()
    c.feed(html or "")
    grid: list[list[str | None]] = []
    th_rows: set[int] = set(c.header_rows)
    for r, row in enumerate(c.rows):
        while len(grid) <= r:
            grid.append([])
        col = 0
        for text, colspan, rowspan, is_th in row:
            while col < len(grid[r]) and grid[r][col] is not None:
                col += 1  # skip positions filled by a rowspan from above
            for dr in range(rowspan):
                while len(grid) <= r + dr:
                    grid.append([])
                line = grid[r + dr]
                for dc in range(colspan):
                    while len(line) <= col + dc:
                        line.append(None)
                    line[col + dc] = text
            if is_th:
                th_rows.add(r)
            col += colspan
    width = max((len(r) for r in grid), default=0)
    if not width:
        return ""
    lines = []
    header_end = max(th_rows) if th_rows else -1
    for r, row in enumerate(grid):
        cells = [(x or "") for x in row] + [""] * (width - len(row))
        lines.append("| " + " | ".join(cells) + " |")
        if r == header_end:
            lines.append("|" + "---|" * width)
    return "\n".join(lines)
