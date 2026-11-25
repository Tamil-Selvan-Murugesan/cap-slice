"""Structure-aware chunking over Markdown-ish pages (shared by every parser).

Compared with chunk.py (the baseline):
- Line breaks are kept, so a table row stays one line.
- Running headers/footers (lines repeated on most pages) are dropped, except
  lines that state units ("amounts are in INR lakhs"), which are context.
- A ``#`` heading starts a new chunk and is carried as the chunk's section.
- Tables are atomic: never mixed with prose, never split mid-row. A table too
  big for one chunk is split by rows with its header rows repeated. The short
  text just before a table (title, units line) is copied in as its caption,
  and the latest units statement ("amounts in INR lakhs") — of the section, or
  of the page across sub-headings — is always
  included, even when other text sits between it and the table.
- A table that continues at the top of the next page with the same number of
  columns is merged, so rows on page 2 keep the header from page 1 — unless the
  new table opens with a different header of its own (then it is a new table).
- Prose overlap starts at a sentence boundary and never enters a table.

Fixes S13–S21 (2026-10-18, bugs_resolved.md): short edge lines are kept unless they
match a repeated header; a heading with only a line or two under it is not
carried onto the next page; consecutive headings are joined and prose keeps the
section it started in; a units line after the tables on a page reaches them;
captions stay on the table's page; split tables repeat the active subsection row
and don't leave a one-row tail; different tables on consecutive pages aren't merged.
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
    level: int = 0  # headings: number of # marks the parser gave it

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
    # Context kept for round-2 variants (docs/plan.md); not part of `text`, so the baseline is unchanged:
    parent: str = ""  # latest top-level (#) heading within PARENT_PAGES pages, e.g. a running page title
    scope: str = ""   # "standalone" / "consolidated" from a heading naming a statement set, within PARENT_PAGES


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
    frags = [f for f in _FRAGMENT_SPLIT.split(line) if _key(f)]
    # Only a line that contains a repeated fragment can be boilerplate; a line with few letters
    # ("SEC/2511/2017") is not boilerplate just because it is short (fix S13).
    if not any(_key(f) in drop for f in frags):
        return False
    rest = [f for f in frags if _key(f) not in drop]
    return len("".join(_key(f) for f in rest)) < 5


_SPEAKER_NAME = re.compile(r"^[A-Z][A-Za-z.'’\- ]{1,48}?\s*$")  # 'Management :' too
_NOT_SPEAKER = re.compile(r"(?i)^(note|notes|disclaimer|date|time|sub|subject|ref|"  # 'Management:' is a speaker
                          r"particulars|total|source|registered office|cin|website|email|phone|tel|fax)\b")


def _speaker_name(cell: str) -> str | None:
    """'Nish Kakran:' -> 'Nish Kakran' if it looks like a speaker label (<= 6 words, no digits)."""
    c = cell.strip()
    if not c.endswith((":", "：")):
        return None
    name = c.rstrip(":：").strip()
    if not name or len(name.split()) > 6 or re.search(r"\d", name) or _NOT_SPEAKER.match(name) \
            or not _SPEAKER_NAME.match(name):
        return None
    return name


def _transcript_line(s: str) -> str | None:
    """S22: MinerU renders many concall transcripts as two-column speaker tables ('| Name: | speech |') and marks
    some speaker labels as headings ('## Name:'). Turn those back into plain turns ('Name: speech'); continuation
    rows ('| | more speech |') become text; separator rows are dropped (None). Other lines are returned as is."""
    if s.startswith("|"):
        if SEPARATOR.match(s):
            return None
        cs = _cells(s)
        if len(cs) >= 2 and _speaker_name(cs[0]):
            return f"{_speaker_name(cs[0])}: " + " ".join(x for x in cs[1:] if x)
        if len(cs) >= 2 and not cs[0]:
            return " ".join(x for x in cs[1:] if x)
        return s
    if s.startswith("#"):
        h = s.lstrip("#").strip()
        name = _speaker_name(h)
        if name is None and ":" in h:  # '## Name: speech' on one line
            head, _, rest = h.partition(":")
            if _speaker_name(head + ":"):
                return f"{_speaker_name(head + ':')}: {rest.strip()}"
        return f"{name}:" if name else s
    return s


def _blocks(pages: list[ParsedPage], transcript: bool = False) -> list[Block]:
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
            if transcript:
                s = _transcript_line(s)
                if not s or not s.strip(" |"):
                    continue
            kind = "table" if s.startswith("|") else "heading" if s.startswith("#") else "text"
            if kind == "heading":
                page_blocks.append(Block("heading", [s.lstrip("#").strip()], page.number,
                                         level=len(s) - len(s.lstrip("#"))))
            elif page_blocks and page_blocks[-1].kind == kind and page_blocks[-1].lines:
                page_blocks[-1].lines.append(s)
            else:
                page_blocks.append(Block(kind, [s], page.number))
        page_blocks = [b for b in page_blocks if b.lines and any(l.strip() for l in b.lines)]
        # Table continued from the previous page: same column count -> merge, unless the new
        # table opens with a header of its own that differs from the previous table's (fix S20).
        if (page_blocks and blocks and page_blocks[0].kind == "table"
                and blocks[-1].kind == "table"
                and _ncols(page_blocks[0]) == _ncols(blocks[-1])):
            new_head, old_head = _own_header(page_blocks[0]), _own_header(blocks[-1])
            if new_head is None or _same_rows(new_head, old_head):
                cont = page_blocks.pop(0)
                skip = (len(new_head) + (_sep_header(cont) is not None)) if new_head else 0
                body = cont.lines[skip:]  # drop a repeated header
                blocks[-1].lines += [l for l in body if not SEPARATOR.match(l)]
                blocks[-1].end_page = page.number
        blocks += page_blocks
    for b in blocks:
        b.end_page = b.end_page or b.page
    return blocks


def _ncols(table: Block) -> int:
    return max(l.count("|") for l in table.lines) - 1


def _sep_header(table: Block) -> list[str] | None:
    """Header rows above a Markdown separator in the first 4 lines, or None."""
    for i, l in enumerate(table.lines[:4]):
        if SEPARATOR.match(l):
            return table.lines[:i]
    return None


AMOUNT = re.compile(r"\d[\d,]*\.\d\d|\d{1,3}(,\d{2,3})+")
YEAR = re.compile(r"\b(19|20)\d\d\b")


def _own_header(table: Block) -> list[str] | None:
    """The table's header rows if it visibly opens with one, else None (a bare continuation).
    With a Markdown separator: the rows above it. Without one: the leading rows before the first
    amount, if they include a title row repeated across all cells or a row of period headers
    (years in two or more cells) — a continued table starts with data, not with those."""
    head = _sep_header(table)
    if head is not None:
        # Rows with amounts above a separator are data, not a header: some parsers put a separator
        # under the first row of a continued table ("| Net Profit Margin (%) | 12.44 |").
        return None if any(AMOUNT.search(l) for l in head) else head
    lead = []
    for l in table.lines[:4]:
        if AMOUNT.search(l):
            break
        lead.append(l)
    if any(_uniform(l) or sum(bool(YEAR.search(c)) for c in _cells(l)) >= 2 for l in lead):
        return lead
    return None


def _same_rows(a: list[str] | None, b: list[str] | None) -> bool:
    norm = lambda rows: [re.sub(r"[^a-z0-9]+", "", r.lower()) for r in rows or []]  # noqa: E731
    return norm(a) == norm(b)


def _cells(row: str) -> list[str]:
    return [c.strip() for c in row.strip().strip("|").split("|")]


NUMERIC_CELL = re.compile(r"[\s(\-–−]*(?:₹|rs\.?|inr)?\s*\d[\d,]*(?:\.\d+)?\s*%?[)\s]*", re.I)


def _uniform(row: str) -> bool:
    """A group row: every non-empty cell repeats the same text ("Income | Income | Income")."""
    cells = [c for c in _cells(row) if c]
    return len(cells) > 1 and len(set(cells)) == 1


def _is_label_row(row: str) -> bool:
    """A subsection row inside a table: a label and no values ("Segment Results - % to Revenue")."""
    cells = _cells(row)
    if not cells or not re.search(r"[A-Za-z]", cells[0]):
        return False
    return not any(NUMERIC_CELL.fullmatch(c) for c in cells[1:] if c)


def _header_rows(table: Block) -> list[str]:
    """Rows to repeat when a table is split: up to and including the MD separator."""
    head = _sep_header(table)
    if head is not None:
        return table.lines[:len(head) + 1]
    # No separator (Option 1, some MinerU/Paddle tables): repeat leading rows until the first one
    # with an amount, or a group row after the first ("I. EQUITY | I. EQUITY | ..."). Up to 4 rows,
    # so a units row + group header + date row all repeat (fix S18).
    head = []
    for k, l in enumerate(table.lines[:4]):
        if AMOUNT.search(l) or (k and _uniform(l)):
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


WEAK_HEADING_WORDS = 30  # a heading followed by less than this on its page is not carried to the next page
HEADING_RUN = 3          # consecutive headings joined into one section ("Human Capital / 519")


def _units_line(b: Block, max_words: int = 25) -> str | None:
    return next((l for l in reversed(b.lines) if UNIT_HINT.search(l) and len(l.split()) <= max_words), None)


PARENT_PAGES = 2       # a top-level heading labels chunks up to this many pages after it was last seen
PARENT_WORDS = 12      # longer "#" lines are mis-marked sentences, not titles
SCOPE = re.compile(r"(?i)\b(standalone|consolidated)\b.{0,40}\b(financial (statements|results)|balance sheet|"
                   r"statement of (profit|cash|changes)|cash flow)")


def chunk_structured(pages: list[ParsedPage], transcript: bool = False) -> list[StructuredChunk]:
    """transcript=True: concall transcripts — speaker tables and speaker headings become plain turns (fix S22)."""
    chunks: list[StructuredChunk] = []
    top, top_page, scope, scope_page = "", 0, "", 0   # round-2 context only; never changes text
    buf_ctx = ("", "")
    section = ""
    run: list[str] = []    # consecutive headings with no content between them
    section_page = 0
    section_words = 0      # words of content after the current heading, on the heading's page
    page = 0
    buf: list[Block] = []  # pending prose
    buf_section = ""       # section active when the pending prose started
    carry = ""             # overlap text for the next prose chunk
    units = ""             # latest units statement (kept across headings on the same page)
    units_page = 0

    def emit(kind: str, text: str, first: int, last: int, notes: list[str] | None = None,
             sec: str | None = None, ctx: tuple[str, str] | None = None) -> None:
        sec = section if sec is None else sec
        body = (f"## {sec}\n" if sec else "") + text.strip()
        parent, sc = ctx if ctx is not None else _ctx()
        chunks.append(StructuredChunk(len(chunks), kind, body, sec, first, last, notes or [], parent, sc))

    def _ctx() -> tuple[str, str]:
        return ((top if top and page - top_page <= PARENT_PAGES else ""),
                (scope if scope and page - scope_page <= PARENT_PAGES else ""))

    def flush_text() -> None:
        nonlocal buf, carry
        if not buf:
            return
        text = "\n\n".join(b.text for b in buf)
        # The section is the one active when the text started, not the latest heading (fix S15).
        # A heading kept as text has no end_page of its own; the chunk ends on its last real page
        # (fix S21: 451 chunks had page_end 0 and covered no page at all).
        emit("text", (carry + "\n\n" if carry else "") + text,
             buf[0].page, max(x.end_page or x.page for x in buf), ["starts with overlap"] if carry else [],
             buf_section, buf_ctx)
        carry = _sentence_tail(text, OVERLAP_WORDS)
        buf = []

    def add_text(b: Block) -> None:
        nonlocal buf_section, buf_ctx
        if buf and sum(x.words() for x in buf) + b.words() > TEXT_WORDS:
            flush_text()
        if not buf:
            buf_section = section
            buf_ctx = _ctx()
        buf.append(b)

    blocks = _blocks(pages, transcript)
    for i, b in enumerate(blocks):
        if b.page != page:
            # New page: a heading that only had a line or two under it on its own page (a
            # signatory's name, a KPI value marked as a heading) does not label the next page (fix S14).
            if section and section_page < b.page and 0 < section_words < WEAK_HEADING_WORDS:
                section, run = "", []
            page = b.page
        if b.kind == "heading":
            h = b.lines[0]
            if SCOPE.search(h):
                scope, scope_page = SCOPE.search(h).group(1).lower(), b.page
            if b.level == 1 and len(h.split()) <= PARENT_WORDS:
                top, top_page = h, b.page
            if sum(x.words() for x in buf) >= 50:
                flush_text()
                carry = ""
            elif buf:
                # Chunk too small to close: keep the heading as text so it isn't lost.
                buf.append(Block("text", [f"## {h}"], b.page))
            # Headings in a row with nothing between them belong together ("Human Capital", "519");
            # joining them keeps a KPI value that a parser marked as a heading (fix S15).
            prev = blocks[i - 1] if i else None
            run = (run if prev is not None and prev.kind == "heading" and prev.page == b.page else [])
            run = (run + [h])[-HEADING_RUN:]
            section, section_page, section_words = " / ".join(run), b.page, 0
            # A units statement ("Amount in crores of INR") covers the rest of its page even when a
            # parser marks a sub-table title ("B. Other Equity") as a heading (fix S10).
            if b.page != units_page:
                units = ""
            continue
        if b.page == section_page:
            section_words += b.words()
        if b.kind == "text":
            found = _units_line(b)
            if found:
                units, units_page = found, b.end_page or b.page
            add_text(b)
            continue
        if len([l for l in b.lines if not SEPARATOR.match(l)]) < MIN_TABLE_ROWS:
            add_text(Block("text", b.lines, b.page, b.end_page))  # too small to stand alone
            continue
        # Caption: the short text blocks right before the table (title, units line) on the
        # table's own page (fix S17: not the previous page's signature block), up to CAPTION_WORDS,
        # plus the section's units statement.
        cap_blocks: list[str] = []
        for x in reversed(buf):
            if x.page != b.page or x.words() + sum(len(c.split()) for c in cap_blocks) > CAPTION_WORDS:
                break
            cap_blocks.insert(0, x.text)
        caption = "\n".join(c for c in cap_blocks if c.strip())
        table_units = units
        if not (units and units_page == b.page):
            # A units line printed after the tables on the same page ("Figures in Rs Crore" under a
            # row of charts) applies to them too (fix S16).
            for x in blocks[i + 1:]:
                if x.page != b.end_page:
                    break
                u = _units_line(x, 12) if x.kind == "text" else None
                if u:
                    table_units = u
                    break
        if table_units and table_units not in caption:
            caption = (table_units + "\n" + caption).strip()
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
        label = None  # latest subsection row ("Segment contribution - as % to total revenue")
        for r in rows:
            if part and len(" ".join(head + part + [r]).split()) > TABLE_WORDS:
                moved = [part.pop()] if len(part) > 1 and _is_label_row(part[-1]) else []
                parts.append(part)
                # A part that starts mid-subsection repeats the subsection row (fix S19).
                part = moved or ([label] if label and not _is_label_row(r) else [])
            if _is_label_row(r):
                label = r
            part.append(r)
        parts.append(part)
        # Don't leave a tiny tail (one or two rows) on its own if it fits with the part before.
        if len(parts) > 1 and len(parts[-1]) < 3 and \
                len(" ".join(head + parts[-2] + parts[-1]).split()) <= TABLE_WORDS * 1.3:
            tail = parts.pop()
            if tail and _is_label_row(tail[0]) and tail[0] in parts[-1]:
                tail = tail[1:]  # the repeated subsection row is already there
            parts[-1] += tail
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
                # The merged chunk starts with the pending one, so it keeps that section.
                c = StructuredChunk(0, "text", pending.text + "\n\n" + body, pending.section or c.section,
                                    pending.page_start, c.page_end, pending.notes + c.notes,
                                    pending.parent, pending.scope)
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
