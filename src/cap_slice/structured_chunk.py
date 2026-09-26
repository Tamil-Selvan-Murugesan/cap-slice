"""Structure-aware chunking over Markdown-ish pages (shared by every parser).

Compared with chunk.py (the baseline):
- Line breaks are kept, so a table row stays one line.
- Running headers/footers (lines repeated on most pages) are dropped, except
  lines that state units ("amounts are in INR lakhs"), which are context.
- A ``#`` heading starts a new chunk and is carried as the chunk's section.
- Tables are atomic: never mixed with prose, never split mid-row. A table too
  big for one chunk is split by rows with its header rows repeated. The short
  text just before a table (title, units line) is copied in as its caption.
- A table that continues at the top of the next page with the same number of
  columns is merged, so rows on page 2 keep the header from page 1.
- Prose overlap starts at a sentence boundary and never enters a table.
"""

from __future__ import annotations

import collections
import re
from dataclasses import dataclass, field

from cap_slice.parsing import ParsedPage

TEXT_WORDS = 400       # target size of a prose chunk
TABLE_WORDS = 450      # tables larger than this are split by rows
OVERLAP_WORDS = 50     # prose overlap, trimmed to whole sentences
CAPTION_WORDS = 60     # max size of the text copied in front of a table
MIN_TEXT_WORDS = 80    # smaller prose chunks are merged into the next one
MIN_TABLE_ROWS = 3     # "tables" with fewer rows are treated as text
UNIT_HINT = re.compile(r"(?i)amounts? (are )?in|in (inr|rs\.?|₹)|lakhs|crores?|\bmn\b|million")
SEPARATOR = re.compile(r"^\|?\s*:?-{3,}")


@dataclass
class Block:
    kind: str  # heading | table | text
    lines: list[str]
    page: int
    end_page: int = 0

    @property
    def text(self) -> str:
        return "\n".join(self.lines)

    def words(self) -> int:
        return len(self.text.split())


@dataclass
class StructuredChunk:
    index: int
    kind: str  # text | table
    text: str
    section: str
    page_start: int
    page_end: int
    notes: list[str] = field(default_factory=list)


def _normalise(line: str) -> str:
    # Inline markup from parsers: <sup>, <u>, <mark> tags, bold (**) and the
    # strikethrough (~~) PyMuPDF4LLM puts around low-confidence OCR characters.
    line = re.sub(r"</?(sup|sub|u|mark|b|i)>", "", line)
    line = line.replace("<br>", " ").replace("**", "").replace("~~", "")
    return re.sub(r"[ \t]+", " ", line).rstrip()


_FRAGMENT_SPLIT = re.compile(r"\s*\|\s*|\s{2,}|(?<=[.:])\s+")


def _key(fragment: str) -> str:
    return re.sub(r"[^a-z]+", "", fragment.lower())


EDGE_TOP, EDGE_BOTTOM = 8, 4  # lines at the top/bottom of a page checked for boilerplate


def _edge_lines(page: ParsedPage) -> list[str]:
    lines = [_normalise(l) for l in page.text.splitlines() if l.strip()]
    return lines[:EDGE_TOP] + lines[-EDGE_BOTTOM:]


def _boilerplate(pages: list[ParsedPage]) -> set[str]:
    """Text fragments near the top/bottom of the page that repeat on at least
    half the pages (running headers, letterheads, footers). Fragments rather
    than lines, because parsers join or split the same letterhead differently
    from page to page. Only page edges are considered, so repeated words inside
    tables (e.g. "Promoter") are never treated as boilerplate."""
    if len(pages) < 3:
        return set()
    seen = collections.Counter()
    for p in pages:
        seen.update({_key(f) for l in _edge_lines(p) for f in _FRAGMENT_SPLIT.split(l)
                     if len(_key(f)) >= 3})
    limit = max(3, len(pages) // 2)
    return {f for f, n in seen.items() if n >= limit}


def _is_boilerplate(line: str, drop: set[str]) -> bool:
    # Table rows are data even at a page edge (tables often run to the bottom).
    if not drop or UNIT_HINT.search(line) or line.lstrip().startswith("|"):
        return False
    rest = [f for f in _FRAGMENT_SPLIT.split(line) if _key(f) and _key(f) not in drop]
    return len("".join(_key(f) for f in rest)) < 5


def _blocks(pages: list[ParsedPage]) -> list[Block]:
    drop = _boilerplate(pages)
    blocks: list[Block] = []
    for page in pages:
        page_blocks: list[Block] = []
        edges = set(_edge_lines(page))
        for raw in page.text.splitlines():
            line = _normalise(raw)
            if not line.strip():
                if page_blocks and page_blocks[-1].kind == "text":
                    page_blocks.append(Block("text", [], page.number))  # paragraph break
                continue
            if (line in edges and _is_boilerplate(line, drop)) or re.fullmatch(r"\s*\d{1,4}\s*", line):
                continue
            s = line.strip()
            kind = "table" if s.startswith("|") else "heading" if s.startswith("#") else "text"
            if kind == "heading":
                page_blocks.append(Block("heading", [s.lstrip("#").strip()], page.number))
            elif page_blocks and page_blocks[-1].kind == kind and page_blocks[-1].lines:
                page_blocks[-1].lines.append(s)
            else:
                page_blocks.append(Block(kind, [s], page.number))
        page_blocks = [b for b in page_blocks if b.lines and any(l.strip() for l in b.lines)]
        # Table continued from the previous page: same column count -> merge.
        if (page_blocks and blocks and page_blocks[0].kind == "table"
                and blocks[-1].kind == "table"
                and _ncols(page_blocks[0]) == _ncols(blocks[-1])):
            cont = page_blocks.pop(0)
            blocks[-1].lines += [l for l in cont.lines if not SEPARATOR.match(l)]
            blocks[-1].end_page = page.number
        blocks += page_blocks
    for b in blocks:
        b.end_page = b.end_page or b.page
    return blocks


def _ncols(table: Block) -> int:
    return max(l.count("|") for l in table.lines) - 1


def _header_rows(table: Block) -> list[str]:
    """Rows to repeat when a table is split: up to and including the MD separator."""
    for i, l in enumerate(table.lines[:4]):
        if SEPARATOR.match(l):
            return table.lines[:i + 1]
    # No separator (Option 1): repeat leading rows until the first one with a number.
    head = []
    for l in table.lines[:3]:
        if re.search(r"\d[\d,]*\.\d\d|\d{1,3}(,\d{2,3})+", l):
            break
        head.append(l)
    return head


def _sentence_tail(text: str, max_words: int) -> str:
    sentences = re.split(r"(?<=[.?!])\s+", text.strip())
    tail: list[str] = []
    for s in reversed(sentences):
        if len(" ".join(tail + [s]).split()) > max_words:
            break
        tail.insert(0, s)
    return " ".join(tail)


def chunk_structured(pages: list[ParsedPage]) -> list[StructuredChunk]:
    chunks: list[StructuredChunk] = []
    section = ""
    buf: list[Block] = []  # pending prose
    carry = ""             # overlap text for the next prose chunk

    def emit(kind: str, text: str, first: int, last: int, notes: list[str] | None = None) -> None:
        body = (f"## {section}\n" if section else "") + text.strip()
        chunks.append(StructuredChunk(len(chunks), kind, body, section, first, last, notes or []))

    def flush_text() -> None:
        nonlocal buf, carry
        if not buf:
            return
        text = "\n\n".join(b.text for b in buf)
        emit("text", (carry + "\n\n" if carry else "") + text,
             buf[0].page, buf[-1].end_page, ["starts with overlap"] if carry else [])
        carry = _sentence_tail(text, OVERLAP_WORDS)
        buf = []

    for i, b in enumerate(_blocks(pages)):
        if b.kind == "heading":
            if sum(x.words() for x in buf) >= 50:
                flush_text()
                carry = ""
            elif buf:
                # Chunk too small to close: keep the heading as text so it isn't lost.
                buf.append(Block("text", [f"## {b.lines[0]}"], b.page))
            section = b.lines[0]
            continue
        if b.kind == "text":
            if buf and sum(x.words() for x in buf) + b.words() > TEXT_WORDS:
                flush_text()
            buf.append(b)
            continue
        if len([l for l in b.lines if not SEPARATOR.match(l)]) < MIN_TABLE_ROWS:
            b = Block("text", b.lines, b.page, b.end_page)  # too small to stand alone
            if buf and sum(x.words() for x in buf) + b.words() > TEXT_WORDS:
                flush_text()
            buf.append(b)
            continue
        # Table: caption = the short text right before it (title, units line).
        caption = buf[-1].text if buf and buf[-1].words() <= CAPTION_WORDS else ""
        flush_text()
        carry = ""
        head = _header_rows(b)
        rows = b.lines[len(head):]
        notes = [f"table continues across pages {b.page}-{b.end_page}"] if b.end_page != b.page else []
        if b.words() <= TABLE_WORDS:
            emit("table", (caption + "\n\n" if caption else "") + b.text, b.page, b.end_page, notes)
            continue
        part: list[str] = []
        parts: list[list[str]] = []
        for r in rows:
            if part and len(" ".join(head + part + [r]).split()) > TABLE_WORDS:
                parts.append(part)
                part = []
            part.append(r)
        parts.append(part)
        for n, part in enumerate(parts, 1):
            emit("table", (caption + "\n\n" if caption else "") + "\n".join(head + part),
                 b.page, b.end_page, notes + [f"table part {n}/{len(parts)}, header rows repeated"])
    flush_text()
    return _merge_small(chunks)


def _merge_small(chunks: list[StructuredChunk]) -> list[StructuredChunk]:
    """Fold prose chunks under MIN_TEXT_WORDS into the next prose chunk."""
    out: list[StructuredChunk] = []
    pending: StructuredChunk | None = None
    for c in chunks:
        if pending is not None:
            if c.kind == "text" and c.page_start - pending.page_end <= 1:
                # Drop the repeated "## section" line only when both share the section.
                same = c.section and c.section == pending.section and c.text.startswith("## ")
                body = c.text.split("\n", 1)[1] if same else c.text
                c = StructuredChunk(0, "text", pending.text + "\n\n" + body, c.section,
                                    pending.page_start, c.page_end, pending.notes + c.notes)
            else:
                out.append(pending)
            pending = None
        if c.kind == "text" and len(c.text.split()) < MIN_TEXT_WORDS:
            pending = c
            continue
        out.append(c)
    if pending is not None:
        out.append(pending)
    for i, c in enumerate(out):
        c.index = i
    return out
