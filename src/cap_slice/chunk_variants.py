"""Round-2 chunking variants (docs/plan.md, Retrieval experiments, round 2).

    uv run cap-slice-chunk-variants build b1          # -> parsed_advanced/_chunks/r2-b1.jsonl
    uv run cap-slice-chunk-variants build all
    uv run cap-slice-chunk-variants sample d --n 20   # print random chunks to read before embedding

Every variant starts from the round-1 baseline (MinerU advanced -> page_clean -> structured_chunk at tag
chunker-baseline-2026-10-18) and changes one thing. Each record has `text` (what a search returns, and
what the golden scorer and an answer step see) and `embed_text` (what gets embedded); `parent` is the
returned chunk's id within its document, so search can return each parent once.

  b1  context header: "<company> · <document> <period>" line before the chunk; returns the chunk.
  b2  b1 + statement scope (standalone / consolidated, from the latest heading naming a statement set;
      annual reports and results only) + heading path: the chunk's section line becomes
      "<top-level heading> › <section>" (the top-level "#" heading seen within 2 pages, usually the
      running page title). Returns the chunk with that path.
  c   table chunks (not concall speaker tables) are embedded as a descriptor built by rules: caption
      lines, column headers, row labels, no values. The full table is returned. Prose unchanged.
  d   per-type splits. Concalls: speaker turns (speaker tables `| Name: | speech |` and `Name: speech`
      lines) grouped as opening remarks (<= TEXT_WORDS) and one exchange per chunk (moderator hand-over,
      question, answers, follow-ups until the next moderator turn; long exchanges split at turns, later
      parts repeat the opening question). Decks: one slide (page) per chunk. Other documents unchanged.
      Transcripts with no moderator turns keep their baseline chunks.
  e   small-to-big: each baseline chunk is cut into pieces (prose ~PIECE_WORDS words with the section
      line; tables: caption + header + PIECE_ROWS rows); pieces are embedded and searched, and each
      piece returns its parent baseline chunk.

All rules were fixed before any round-2 retrieval run and are not tuned on the question set.
"""

from __future__ import annotations

import argparse
import csv
import json
import random
import re
from pathlib import Path

from cap_slice.downloader import REPO_ROOT

CACHE = REPO_ROOT / "parsed_advanced"
PARSER = "mineru"
CHUNKS = CACHE / "_chunks"
VARIANTS = ("b1", "b2", "c", "d", "e", "b2s")  # b2s: b2 on the S22-fixed chunker (2026-11-25)

TEXT_WORDS = 400       # same prose target as the baseline chunker
EXCHANGE_WORDS = 500   # longer concall exchanges are split at speaker turns
QUESTION_WORDS = 100   # repeated opening question in later parts of an exchange
SLIDE_WORDS = 700      # longer slides keep their baseline chunks
PIECE_WORDS = 150      # small-to-big prose piece
PIECE_ROWS = 5         # small-to-big table piece
SMALL = 180            # chunks up to this size are a single piece

SPEAKER = re.compile(r"^([A-Z][A-Za-z.'’\- ]{1,48}?)\s*[:：]\s*(.*)$")
MODERATOR = re.compile(r"(?i)^(moderator|operator)\b")
NOT_SPEAKER = re.compile(r"(?i)^(note|notes|disclaimer|participants?|management|date|time|sub|subject|ref|"
                         r"source|website|email|e-mail|cin|registered office|tel|fax|phone)$")


# ---------------------------------------------------------------- baseline with context

def _cleaned(path: Path) -> tuple[str, list]:
    from cap_slice.page_clean import clean_pages
    from cap_slice.parsing import ParsedPage
    doc = "data/" + str(path.parent.relative_to(CACHE / PARSER)) + ".pdf"
    pages, _ = clean_pages(json.loads(path.read_text())["pages"], REPO_ROOT / doc)
    return doc, [ParsedPage(n, t) for n, t in pages]


def documents():
    for f in sorted((CACHE / PARSER).glob("*/*/*/pages.json")):
        yield _cleaned(f)


def base_chunks() -> list[dict]:
    """The baseline corpus plus the chunker's context fields (parent heading, scope). Cached; its text,
    sections and pages must equal the frozen round-1 corpus (checked)."""
    out = CHUNKS / "r2-ctx.jsonl"
    if out.exists():
        return [json.loads(l) for l in out.open()]
    from cap_slice.structured_chunk import chunk_structured
    rows = []
    for doc, pages in documents():
        for c in chunk_structured(pages):
            rows.append({"doc": doc, "chunk": c.index, "kind": c.kind, "section": c.section,
                         "page_start": c.page_start, "page_end": c.page_end, "text": c.text,
                         "parent_heading": c.parent, "scope": c.scope})
    frozen = [json.loads(l) for l in (CHUNKS / "mineru.jsonl").open()]
    keys = ("doc", "chunk", "kind", "section", "page_start", "page_end", "text")
    if len(frozen) != len(rows) or any({k: a[k] for k in keys} != b for a, b in zip(rows, frozen)):
        raise SystemExit("rebuilt baseline differs from parsed_advanced/_chunks/mineru.jsonl")
    _write(out, rows)
    return rows


def base_chunks_s22() -> list[dict]:
    """Baseline with the S22 fix: concall transcripts chunked in transcript mode (speaker tables -> turns).
    Every other document must come out exactly as in base_chunks() (checked)."""
    out = CHUNKS / "r2-ctx-s22.jsonl"
    if out.exists():
        return [json.loads(l) for l in out.open()]
    from cap_slice.structured_chunk import chunk_structured
    old = base_chunks()
    rows = []
    for doc, pages in documents():
        for c in chunk_structured(pages, transcript="/concall_transcripts/" in doc):
            rows.append({"doc": doc, "chunk": c.index, "kind": c.kind, "section": c.section,
                         "page_start": c.page_start, "page_end": c.page_end, "text": c.text,
                         "parent_heading": c.parent, "scope": c.scope})
    same = lambda rs: [r for r in rs if "/concall_transcripts/" not in r["doc"]]  # noqa: E731
    if same(rows) != same(old):
        raise SystemExit("S22 rebuild changed documents other than concall transcripts")
    _write(out, rows)
    return rows


def _write(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(r) + "\n" for r in rows))


# ---------------------------------------------------------------- headers (b1, b2)

def doc_info() -> dict[str, dict]:
    from cap_slice.periods import documents as docs, load_overrides, normalise_doc, sme_symbols
    matrix = {r["url"]: r for r in csv.DictReader((REPO_ROOT / "data" / "document_availability_matrix.csv").open())}
    ov, sme = load_overrides(), sme_symbols()
    out = {}
    for r in docs():
        n = normalise_doc(r["path"], r["doc_type"], r["period_label"], r["filed_date"], ov, r["symbol"] in sme)
        out[r["path"]] = {"company": matrix.get(r["url"], {}).get("company", r["symbol"]),
                          "doc_type": r["doc_type"], "label": r["period_label"], "period": n["period"]}
    return out


def header(info: dict, scope: str = "") -> str:
    dt, label, period = info["doc_type"], info["label"], info["period"]
    month = re.sub(r"\s*\(.*\)$", "", label)  # "Nov 2025 (a)" -> "Nov 2025"
    on = f" (on {period})" if period else ""
    what = {"annual_report": f"Annual report {label}",
            "periodic_results": f"Financial results {period or label}",
            "concall_transcript": f"Earnings call transcript, {month}{on}",
            "investor_presentation": f"Investor presentation, {month}{on}"}[dt]
    parts = [info["company"], what] + ([f"{scope.capitalize()} financial statements"] if scope else [])
    return " · ".join(parts)


def _norm(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", s.lower())


def heading_path(c: dict) -> str:
    parent, sec = c["parent_heading"], c["section"]
    if not parent:
        return sec
    if not sec:
        return parent
    p, s = _norm(parent), _norm(sec)
    return sec if (p in s or s in p) else f"{parent} › {sec}"


def variant_b(chunks: list[dict], path: bool) -> list[dict]:
    info = doc_info()
    out = []
    for c in chunks:
        i = info[c["doc"]]
        scope = c["scope"] if path and i["doc_type"] in ("annual_report", "periodic_results") else ""
        text = c["text"]
        if path:
            hp = heading_path(c)
            if c["section"] and text.startswith(f"## {c['section']}\n"):
                text = f"## {hp}\n" + text[len(f"## {c['section']}\n"):]
            elif hp:
                text = f"## {hp}\n" + text
        out.append(_rec(c, text=text, embed_text=header(i, scope) + "\n" + text))
    return out


def _rec(c: dict, **kw) -> dict:
    r = {k: c[k] for k in ("doc", "chunk", "kind", "section", "page_start", "page_end", "text")}
    r.update(kw)
    r.setdefault("embed_text", r["text"])
    r.setdefault("parent", r["chunk"])
    return r


# ---------------------------------------------------------------- table descriptors (c)

def _cells(row: str) -> list[str]:
    return [x.strip() for x in row.strip().strip("|").split("|")]


def speaker_table(text: str) -> bool:
    rows = [l for l in text.splitlines() if l.startswith("|") and not re.match(r"^\|?\s*:?-{3,}", l)]
    named = sum(1 for r in rows if (cs := _cells(r)) and cs[0].endswith(":"))
    return bool(rows) and named >= max(1, len(rows) // 2)


def descriptor(text: str) -> str:
    from cap_slice.structured_chunk import NUMERIC_CELL, SEPARATOR
    lines = text.splitlines()
    first = next((i for i, l in enumerate(lines) if l.startswith("|")), len(lines))
    pre = [l for l in lines[:first] if l.strip()]
    rows = [l for l in lines[first:] if l.startswith("|")]
    sep = next((i for i, l in enumerate(rows[:4]) if SEPARATOR.match(l)), None)
    head = rows[:sep] if sep is not None else rows[:1]
    body = rows[sep + 1:] if sep is not None else rows[1:]
    cols, seen = [], set()
    for r in head:
        for x in _cells(r):
            if x and x not in seen:
                seen.add(x)
                cols.append(x)
    labels, seen = [], set()
    for r in body:
        lab = next((x for x in _cells(r) if x and not NUMERIC_CELL.fullmatch(x)), "")
        if lab and lab not in seen and not SEPARATOR.match(r):
            seen.add(lab)
            labels.append(lab)
    if not cols and not labels:
        return text
    return "\n".join(pre + ([f"Columns: {' | '.join(cols)}"] if cols else [])
                     + ([f"Rows: {'; '.join(labels)}"] if labels else []))


def variant_c(chunks: list[dict]) -> list[dict]:
    out = []
    for c in chunks:
        if c["kind"] == "table" and "/concall_transcripts/" not in c["doc"] and not speaker_table(c["text"]):
            out.append(_rec(c, embed_text=descriptor(c["text"])))
        else:
            out.append(_rec(c))
    return out


# ---------------------------------------------------------------- per-type splits (d)

def _page_lines(pages) -> list[tuple[int, str]]:
    """Cleaned lines per page with running headers/footers and bare page numbers dropped (the
    baseline chunker's own rules)."""
    from cap_slice.structured_chunk import _boilerplate, _edge_lines, _is_boilerplate, _normalise
    drop = _boilerplate(pages)
    out = []
    for p in pages:
        edges = set(_edge_lines(p))
        for raw in p.text.splitlines():
            line = _normalise(raw)
            if not line.strip() or re.fullmatch(r"\s*\d{1,4}\s*", line):
                continue
            if line in edges and _is_boilerplate(line, drop):
                continue
            out.append((p.number, line.strip()))
    return out


def _speaker(cell: str) -> str | None:
    name = cell.strip().rstrip(":：").strip()
    if not name or len(name.split()) > 6 or re.search(r"\d", name) or NOT_SPEAKER.match(name):
        return None
    return name


def turns(pages) -> list[dict]:
    from cap_slice.structured_chunk import SEPARATOR
    out: list[dict] = []
    for page, line in _page_lines(pages):
        name, said = None, line
        if line.startswith("|"):
            if SEPARATOR.match(line):
                continue
            cs = _cells(line)
            if len(cs) >= 2 and cs[0].endswith((":", "：")):
                name, said = _speaker(cs[0]), " ".join(x for x in cs[1:] if x)
                if name is None:
                    said = line
            elif cs and not cs[0]:
                said = " ".join(x for x in cs[1:] if x)
        elif not line.startswith("#"):
            m = SPEAKER.match(line)
            if m and _speaker(m.group(1)):
                name, said = _speaker(m.group(1)), m.group(2)
        else:
            said = line.lstrip("#").strip()
        if name is not None:
            out.append({"speaker": name, "text": said.strip(), "first": page, "last": page})
        elif out:
            out[-1]["text"] += ("\n" if out[-1]["text"] else "") + said
            out[-1]["last"] = page
        else:
            out.append({"speaker": "", "text": said, "first": page, "last": page})
    return [t for t in out if t["text"].strip() or t["speaker"]]


def _words(s: str) -> int:
    return len(s.split())


def _split_long(prefix: str, text: str, limit: int) -> list[str]:
    """Split one long turn at sentence ends into pieces of <= limit words, each with the prefix."""
    sents = re.split(r"(?<=[.!?])\s+", text)
    parts, cur = [], []
    for s in sents:
        if cur and _words(" ".join(cur + [s])) > limit:
            parts.append(" ".join(cur))
            cur = []
        cur.append(s)
    if cur:
        parts.append(" ".join(cur))
    return [prefix + p for p in parts]


def _turn_text(t: dict) -> str:
    return (f"{t['speaker']}: " if t["speaker"] else "") + t["text"]


def _pack(units: list[tuple[str, int, int]], limit: int, lead: str = "") -> list[tuple[str, int, int]]:
    """Pack (text, first, last) units in order into chunks of <= limit words; `lead` is repeated at the
    start of every chunk after the first."""
    out, cur = [], []
    for u in units:
        if cur and _words("\n".join(x[0] for x in cur) + " " + u[0]) > limit:
            out.append(cur)
            cur = [(lead, u[1], u[1])] if lead else []
        cur.append(u)
    if cur:
        out.append(cur)
    return [("\n".join(x[0] for x in g if x[0]), min(x[1] for x in g), max(x[2] for x in g)) for g in out]


def concall_chunks(doc: str, pages) -> list[dict] | None:
    ts = turns(pages)
    # An exchange starts where the moderator hands over to a questioner ("the next question is from…");
    # other moderator turns stay inside the exchange (parsers sometimes put "Moderator" on an answer).
    mods = [i for i, t in enumerate(ts) if MODERATOR.match(t["speaker"]) and "question" in t["text"].lower()]
    qa = mods[0] if mods else None
    if len(mods) < 2 or qa is None:
        return None

    def units(group: list[dict], limit: int) -> list[tuple[str, int, int]]:
        u = []
        for t in group:
            txt = _turn_text(t)
            if _words(txt) > limit:
                u += [(p, t["first"], t["last"]) for p in _split_long(f"{t['speaker']}: " if t["speaker"] else "",
                                                                      t["text"], limit)]
            else:
                u.append((txt, t["first"], t["last"]))
        return u

    out = []
    for text, a, b in _pack(units(ts[:qa], TEXT_WORDS), TEXT_WORDS):
        out.append(("Opening remarks", text, a, b))
    bounds = [i for i in mods if i >= qa] + [len(ts)]
    for s, e in zip(bounds, bounds[1:]):
        group = ts[s:e]
        asker = next((t for t in group if not MODERATOR.match(t["speaker"]) and t["speaker"]), None)
        sec = f"Q&A: {asker['speaker']}" if asker else "Q&A"
        lead = ""
        if asker:
            q = asker["text"].split()
            lead = f"(Question) {asker['speaker']}: " + " ".join(q[:QUESTION_WORDS]) + (" …" if len(q) > QUESTION_WORDS else "")
        for text, a, b in _pack(units(group, EXCHANGE_WORDS), EXCHANGE_WORDS, lead):
            out.append((sec, text, a, b))
    return [{"doc": doc, "chunk": i, "kind": "text", "section": sec, "page_start": a, "page_end": b,
             "text": f"## {sec}\n{text}"} for i, (sec, text, a, b) in enumerate(out) if text.strip()]


def deck_chunks(doc: str, pages, base: list[dict]) -> list[dict]:
    by_page: dict[int, list[str]] = {}
    for page, line in _page_lines(pages):
        by_page.setdefault(page, []).append("## " + line.lstrip("#").strip() if line.startswith("#") else line)
    out = []
    for page in sorted(by_page):
        lines = by_page[page]
        text = "\n".join(lines)
        if _words(text) < 3:
            continue
        if _words(text) > SLIDE_WORDS:
            out += [dict(c) for c in base if c["page_start"] == page]
            continue
        first = next((l[3:] for l in lines if l.startswith("## ")), "")
        out.append({"doc": doc, "chunk": 0, "kind": "text", "section": first, "page_start": page,
                    "page_end": page, "text": text})
    for i, c in enumerate(out):
        c["chunk"] = i
    return out


def variant_d(chunks: list[dict]) -> tuple[list[dict], dict]:
    by_doc: dict[str, list[dict]] = {}
    for c in chunks:
        by_doc.setdefault(c["doc"], []).append(c)
    stats = {"concall_split": 0, "concall_fallback": [], "decks": 0}
    out = []
    for doc, pages in documents():
        base = by_doc.get(doc, [])
        new = None
        if "/concall_transcripts/" in doc:
            new = concall_chunks(doc, pages)
            if new is None:
                stats["concall_fallback"].append(doc)
            else:
                stats["concall_split"] += 1
        elif "/investor_presentations/" in doc:
            new = deck_chunks(doc, pages, base)
            stats["decks"] += 1
        out += [_rec(c) for c in (new if new is not None else base)]
    return out, stats


# ---------------------------------------------------------------- small-to-big (e)

def pieces(c: dict) -> list[str]:
    text = c["text"]
    if _words(text) <= SMALL:
        return [text]
    lines = text.splitlines()
    if c["kind"] == "table":
        from cap_slice.structured_chunk import SEPARATOR
        first = next((i for i, l in enumerate(lines) if l.startswith("|")), len(lines))
        pre, rows = lines[:first], [l for l in lines[first:] if l.strip()]
        sep = next((i for i, l in enumerate(rows[:4]) if SEPARATOR.match(l)), None)
        head = rows[:sep + 1] if sep is not None else rows[:1]
        body = rows[len(head):]
        if not body:
            return [text]
        return ["\n".join(pre + head + body[i:i + PIECE_ROWS]) for i in range(0, len(body), PIECE_ROWS)]
    sec = lines[0] if lines and lines[0].startswith("## ") else ""
    body = "\n".join(lines[1:] if sec else lines)
    sents = [s for s in re.split(r"(?<=[.!?])\s+|\n+", body) if s.strip()]
    out, cur = [], []
    for s in sents:
        if cur and _words(" ".join(cur + [s])) > PIECE_WORDS:
            out.append(cur)
            cur = []
        cur.append(s)
    if cur:
        out.append(cur)
    return [(sec + "\n" if sec else "") + " ".join(g) for g in out]


def variant_e(chunks: list[dict]) -> list[dict]:
    out = []
    for c in chunks:
        for p in pieces(c):
            out.append({**_rec(c), "chunk": len(out), "embed_text": p, "parent": c["chunk"]})
    return out


# ---------------------------------------------------------------- CLI

def build(variant: str) -> Path:
    base = base_chunks_s22() if variant == "b2s" else base_chunks()
    stats = {}
    if variant in ("b1", "b2", "b2s"):
        rows = variant_b(base, path=variant != "b1")
    elif variant == "c":
        rows = variant_c(base)
    elif variant == "d":
        rows, stats = variant_d(base)
    elif variant == "e":
        rows = variant_e(base)
    else:
        raise SystemExit(f"unknown variant {variant}")
    out = CHUNKS / f"r2-{variant}.jsonl"
    _write(out, rows)
    words = sum(_words(r["embed_text"]) for r in rows)
    print(f"{variant}: {len(rows):,} records ({len({(r['doc'], r['parent']) for r in rows}):,} returned units), "
          f"{words:,} embedded words -> {out.relative_to(REPO_ROOT)}"
          + (f"; concalls split {stats['concall_split']}, kept baseline {len(stats['concall_fallback'])}, decks {stats['decks']}"
             if stats else ""))
    for d in stats.get("concall_fallback", []):
        print("   baseline kept:", d)
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build")
    b.add_argument("variant", choices=VARIANTS + ("all",))
    s = sub.add_parser("sample")
    s.add_argument("variant", choices=VARIANTS)
    s.add_argument("--n", type=int, default=20)
    s.add_argument("--seed", type=int, default=2)
    s.add_argument("--where", default="", help="only records whose doc path contains this")
    s.add_argument("--changed", action="store_true", help="only records whose embed_text differs from text")
    args = ap.parse_args(argv)
    if args.cmd == "build":
        for v in (VARIANTS if args.variant == "all" else (args.variant,)):
            build(v)
        return 0
    rows = [json.loads(l) for l in (CHUNKS / f"r2-{args.variant}.jsonl").open()]
    rows = [r for r in rows if args.where in r["doc"] and (not args.changed or r["embed_text"] != r["text"])]
    for r in random.Random(args.seed).sample(rows, min(args.n, len(rows))):
        print(f"===== {r['doc']} #{r['chunk']} (parent {r['parent']}) p{r['page_start']}-{r['page_end']} {r['kind']}")
        print("--- embedded:\n" + r["embed_text"][:1500])
        if r["embed_text"] != r["text"]:
            print("--- returned:\n" + r["text"][:600])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
