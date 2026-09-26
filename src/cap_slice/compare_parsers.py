"""Compare parsing options on the golden documents and facts.

    uv run cap-slice-compare                       # all options, all golden docs
    uv run cap-slice-compare --option pymupdf4llm --doc c2c_allotment

For every option x document it writes, under review/<option>/<doc>/:
  parsed.md  - the parser's raw output per page, before any cleaning/chunking
  chunks.md  - every chunk exactly as it would be embedded
and review/COMPARISON.md with timings, token counts and fact scores.

Fact levels (data/golden/parse_facts.csv; values read off page images):
  L1 value appears in some chunk
  L2 label and value on the same line, <= 80 chars apart (row kept together)
  L3 L2 + the column's period/header text and the unit in that same chunk
  L4 L3 + value sits under the right column header (tables with | cells only)
For question/answer and prose facts L2 = question/subject and answer in one chunk,
and L3/L4 equal L2.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
import textwrap
import time
from dataclasses import dataclass
from pathlib import Path

from cap_slice.downloader import REPO_ROOT

GOLDEN = REPO_ROOT / "data" / "golden"
REVIEW = REPO_ROOT / "review"
OPTIONS = {
    "baseline": "Current pipeline (extract.py + chunk.py)",
    "pymupdf_text": "Option 1: PyMuPDF text, line-preserving cleaning + structured chunker",
    "pymupdf4llm": "Option 2: PyMuPDF4LLM (layout + RapidOCR) + structured chunker",
}
MIN_TEXT = 50  # chars; below this a page counts as having no text


@dataclass
class OutChunk:
    index: int
    kind: str
    text: str
    section: str
    page_start: int
    page_end: int
    notes: list[str]


def run_option(option: str, pdf: Path, cache: Path | None = None,
               reparse: bool = False) -> tuple[list[tuple[int, str]], list[OutChunk], float]:
    start = time.perf_counter()
    if option == "baseline":
        from cap_slice.chunk import chunk_pages
        from cap_slice.extract import extract_pdf
        doc = extract_pdf(pdf)
        parsed = [(p.number, p.text) for p in doc.pages]
        chunks = [OutChunk(c.index, "text", c.text, "", c.page_start, c.page_end, [])
                  for c in chunk_pages(doc.pages)]
    else:
        from cap_slice.parsing import ParsedPage, get_parser
        from cap_slice.structured_chunk import chunk_structured
        # Parsing is the slow part (PyMuPDF4LLM + OCR: ~16 min for one report),
        # so the raw parse is cached and chunking changes re-use it.
        if cache and cache.exists() and not reparse:
            saved = json.loads(cache.read_text())
            pages = [ParsedPage(n, t) for n, t in saved["pages"]]
            start -= saved["seconds"]
        else:
            pages = get_parser(option)(pdf)
            if cache:
                cache.parent.mkdir(parents=True, exist_ok=True)
                cache.write_text(json.dumps({"seconds": time.perf_counter() - start,
                                             "pages": [(p.number, p.text) for p in pages]}))
        parsed = [(p.number, p.text) for p in pages]
        chunks = [OutChunk(c.index, c.kind, c.text, c.section, c.page_start, c.page_end, c.notes)
                  for c in chunk_structured(pages)]
    return parsed, chunks, time.perf_counter() - start


# ---------- scoring ----------

def _flat(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip().lower()


def _value_re(value: str) -> re.Pattern:
    if re.search(r"[A-Za-z]", value):
        return re.compile(re.escape(value).replace(r"\ ", r"\s+"), re.I)
    return re.compile(r"(?<![\d.,])" + re.escape(value) + r"(?![\d.,]*\d)")


def _cells(line: str) -> list[str]:
    return [c.strip() for c in line.strip().strip("|").split("|") if c.strip()]


def score_fact(fact: dict, chunks: list[OutChunk]) -> tuple[int, int | None]:
    """Return (level 0-4, index of the best chunk)."""
    vre = _value_re(fact["value"])
    label = _flat(fact["label"])
    best, where = 0, None
    for c in chunks:
        if not vre.search(c.text):
            continue
        level = 1
        if fact["kind"] != "table":
            if label in _flat(c.text):
                level = 4
        else:
            for line in c.text.splitlines():
                fl = _flat(line)
                m, i = vre.search(fl), fl.find(label)
                if not m or i < 0 or not (0 <= m.start() - (i + len(label)) <= 80):
                    continue
                level = max(level, 2)
                ctx, unit = _flat(fact["context"]), _flat(fact["unit"])
                body = _flat(c.text)
                if ctx in body and (not unit or unit in body):
                    level = max(level, 3)
                    row = _cells(line)
                    vcell = next((k for k, cell in enumerate(row) if vre.search(cell)), None)
                    for hl in c.text.splitlines():
                        if "|" in hl and ctx in _flat(hl) and hl != line:
                            head = _cells(hl)
                            hcell = next((k for k, cell in enumerate(head) if ctx in _flat(cell)), None)
                            if (vcell is not None and hcell is not None
                                    and len(row) - vcell == len(head) - hcell):
                                level = 4
                            break
        if level > best:
            best, where = level, c.index
    return best, where


# ---------- review files ----------

def write_parsed(path: Path, title: str, parsed: list[tuple[int, str]]) -> None:
    out = [f"# Parsed output: {title}\n",
           "Raw parser output per page, before cleaning and chunking.\n"]
    for n, text in parsed:
        out.append(f"\n---\n\n<!-- page {n} -->\n**Page {n}**" +
                   (" · ⚠ no text" if len(text.strip()) < MIN_TEXT else "") + "\n")
        out.append(text if text.strip() else "_(empty)_")
    path.write_text("\n".join(out) + "\n")


def write_chunks(path: Path, title: str, pdf: Path, chunks: list[OutChunk],
                 tokens: list[int], fact_hits: dict[int, list[str]]) -> None:
    out = [f"# Chunks: {title}\n", f"- PDF: `{pdf.relative_to(REPO_ROOT)}` (page numbers = PDF viewer pages)",
           f"- {len(chunks)} chunks, {sum(tokens):,} tokens "
           f"({sum(1 for c in chunks if c.kind == 'table')} table chunks)",
           "- Text inside each block is exactly what would be embedded.\n"]
    for c, t in zip(chunks, tokens):
        meta = [c.kind, f"pages {c.page_start}–{c.page_end}", f"{len(c.text.split())} words",
                f"{t} tokens"] + c.notes
        if c.index in fact_hits:
            meta.append("golden facts: " + ", ".join(fact_hits[c.index]))
        out.append(f"### Chunk {c.index}\n\n_{' · '.join(meta)}_\n")
        body = c.text if c.kind == "table" else "\n".join(
            textwrap.fill(p, 110) if not p.lstrip().startswith("|") else p
            for p in c.text.split("\n"))
        out.append("```text\n" + body + "\n```\n")
    path.write_text("\n".join(out))


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--option", action="append", choices=list(OPTIONS))
    ap.add_argument("--doc", action="append")
    ap.add_argument("--reparse", action="store_true",
                    help="ignore cached parser output (review/<option>/<doc>/parsed.json)")
    args = ap.parse_args(argv)

    import voyageai
    tok = voyageai.Client(api_key="local-tokenizer-only")  # count_tokens runs locally

    docs = list(csv.DictReader((GOLDEN / "compare_docs.csv").open()))
    docs = [d for d in docs if not args.doc or d["key"] in args.doc]
    facts = list(csv.DictReader((GOLDEN / "parse_facts.csv").open()))
    results_path = REVIEW / "results.json"
    results = json.loads(results_path.read_text()) if results_path.exists() else {}

    from cap_slice.extract import extract_pdf
    for opt in args.option or list(OPTIONS):
        for d in docs:
            pdf = REPO_ROOT / d["path"]
            print(f"{opt:<13} {d['key']:<14} ...", end=" ", flush=True, file=sys.stderr)
            parsed, chunks, secs = run_option(opt, pdf, REVIEW / opt / d["key"] / "parsed.json",
                                              args.reparse)
            tokens = [tok.count_tokens([c.text], model="voyage-finance-2") for c in chunks]
            no_layer = set(extract_pdf(pdf).scanned_pages)
            page_count = extract_pdf(pdf).page_count
            with_text = {n for n, t in parsed if len(t.strip()) >= MIN_TEXT}
            doc_facts = [f for f in facts if f["doc"] == d["key"]]
            scores, hits = {}, {}
            for f in doc_facts:
                level, where = score_fact(f, chunks)
                scores[f["id"]] = level
                if where is not None:
                    hits.setdefault(where, []).append(f"{f['id']} (L{level})")
            outdir = REVIEW / opt / d["key"]
            outdir.mkdir(parents=True, exist_ok=True)
            title = f"{OPTIONS[opt]} — {d['key']}"
            write_parsed(outdir / "parsed.md", title, parsed)
            write_chunks(outdir / "chunks.md", title, pdf, chunks, tokens, hits)
            results.setdefault(opt, {})[d["key"]] = {
                "seconds": round(secs, 1), "pages": page_count,
                "pages_without_text": page_count - len(with_text),
                "text_layer_missing": len(no_layer),
                "recovered_by_ocr": len(no_layer & with_text),
                "chunks": len(chunks), "table_chunks": sum(c.kind == "table" for c in chunks),
                "tokens": sum(tokens), "max_chunk_tokens": max(tokens, default=0),
                "multi_page_chunks": sum(c.page_end - c.page_start >= 2 for c in chunks),
                "facts": scores,
            }
            print(f"{secs:6.1f}s  {len(chunks)} chunks  facts {scores}", file=sys.stderr)
            results_path.write_text(json.dumps(results, indent=1))
    write_comparison(results, docs_all=list(csv.DictReader((GOLDEN / "compare_docs.csv").open())),
                     facts=facts)
    return 0


def write_comparison(results: dict, docs_all: list[dict], facts: list[dict]) -> None:
    opts = [o for o in OPTIONS if o in results]
    out = ["# Parser comparison\n",
           "Generated by `uv run cap-slice-compare`. Scoring levels are defined in "
           "`src/cap_slice/compare_parsers.py`; facts are in `data/golden/parse_facts.csv`.\n",
           "## Fact scores (28 facts; higher is better)\n",
           "| Fact | Doc | p. | Label → value | " + " | ".join(opts) + " |",
           "|---|---|---|---|" + "---|" * len(opts)]
    for f in facts:
        cells = []
        for o in opts:
            lv = results[o].get(f["doc"], {}).get("facts", {}).get(f["id"])
            cells.append("—" if lv is None else ("❌ 0" if lv == 0 else f"L{lv}"))
        out.append(f"| {f['id']} | {f['doc']} | {f['page']} | {f['label']} → {f['value']}"
                   + (f" ({f['context']})" if f["context"] else "") + " | " + " | ".join(cells) + " |")
    out.append("\n| Summary | " + " | ".join(opts) + " |\n|---|" + "---|" * len(opts))
    for lv in (1, 2, 3, 4):
        row = []
        for o in opts:
            vals = [v for d in results[o].values() for v in d["facts"].values()]
            row.append(f"{sum(v >= lv for v in vals)}/{len(vals)}")
        out.append(f"| ≥ L{lv} | " + " | ".join(row) + " |")
    out.append("\n## Per document\n")
    out.append("| Doc | Metric | " + " | ".join(opts) + " |\n|---|---|" + "---|" * len(opts))
    for d in docs_all:
        for m in ("seconds", "pages_without_text", "recovered_by_ocr", "chunks", "table_chunks",
                  "tokens", "max_chunk_tokens", "multi_page_chunks"):
            vals = [str(results[o].get(d["key"], {}).get(m, "—")) for o in opts]
            out.append(f"| {d['key']} | {m} | " + " | ".join(vals) + " |")
    (REVIEW / "COMPARISON.md").write_text("\n".join(out) + "\n")


if __name__ == "__main__":
    sys.exit(main())
