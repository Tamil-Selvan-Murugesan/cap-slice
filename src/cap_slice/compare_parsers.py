"""Compare parsing options on the golden documents and facts.

    uv run cap-slice-compare                       # all options, all golden docs
    uv run cap-slice-compare --option pymupdf4llm --doc c2c_allotment

For every option x document it writes, under review/<option>/<doc>/:
  parsed.md  - the parser's raw output per page, before any cleaning/chunking
  chunks.md  - every chunk exactly as it would be embedded
and review/COMPARISON.md with timings, token counts and fact scores.

Fact levels (data/golden/parse_facts.csv; values read off page images). Only
chunks whose page range covers the fact's page count; the best chunk wins.
  L1 value appears in a chunk covering the fact's page
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
    "docling": "Option 3: Docling (layout + TableFormer + OCR) + structured chunker",
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


@dataclass
class Timing:
    parse_seconds: float     # parser only (from the cache when not re-parsed)
    chunk_seconds: float
    peak_rss_mb: float | None  # peak resident memory of the process while parsing
    rss_growth_mb: float | None  # peak minus memory at parse start (the parser's own share)
    measured_on: str         # date the parse time was measured
    cached: bool


class _PeakMemory:
    """Sample this process's resident memory in a background thread."""

    def __init__(self, interval: float = 0.2) -> None:
        import psutil
        import threading
        self._proc, self._interval = psutil.Process(), interval
        self.peak = 0
        self._stop = threading.Event()
        self._thread = threading.Thread(target=self._run, daemon=True)

    def _run(self) -> None:
        while not self._stop.is_set():
            self.peak = max(self.peak, self._proc.memory_info().rss)
            self._stop.wait(self._interval)

    def __enter__(self) -> "_PeakMemory":
        self.start = self._proc.memory_info().rss
        self._thread.start()
        return self

    def __exit__(self, *exc) -> None:
        self._stop.set()
        self._thread.join()
        self.peak = max(self.peak, self._proc.memory_info().rss)


def run_option(option: str, pdf: Path, cache: Path | None = None,
               reparse: bool = False) -> tuple[list[tuple[int, str]], list[OutChunk], Timing]:
    today = time.strftime("%Y-%m-%d")
    if option == "baseline":
        from cap_slice.chunk import chunk_pages
        from cap_slice.extract import extract_pdf
        with _PeakMemory() as mem:
            t0 = time.perf_counter()
            doc = extract_pdf(pdf)
            parse_s = time.perf_counter() - t0
        parsed = [(p.number, p.text) for p in doc.pages]
        t0 = time.perf_counter()
        chunks = [OutChunk(c.index, "text", c.text, "", c.page_start, c.page_end, [])
                  for c in chunk_pages(doc.pages)]
        timing = Timing(parse_s, time.perf_counter() - t0, mem.peak / 2**20,
                        (mem.peak - mem.start) / 2**20, today, False)
    else:
        from cap_slice.parsing import ParsedPage, get_parser
        from cap_slice.structured_chunk import chunk_structured
        # Parsing is the slow part (PyMuPDF4LLM + OCR: ~16 min for one report),
        # so the raw parse is cached with its measured time; chunking changes re-use it.
        if cache and cache.exists() and not reparse:
            saved = json.loads(cache.read_text())
            pages = [ParsedPage(n, t) for n, t in saved["pages"]]
            parse_s, peak, growth, when, cached = (
                saved["seconds"], saved.get("peak_rss_mb"), saved.get("rss_growth_mb"),
                saved.get("measured_on", "2026-09-26"), True)
        else:
            with _PeakMemory() as mem:
                t0 = time.perf_counter()
                pages = get_parser(option)(pdf)
                parse_s = time.perf_counter() - t0
            peak, growth, when, cached = (mem.peak / 2**20, (mem.peak - mem.start) / 2**20,
                                          today, False)
            if cache:
                cache.parent.mkdir(parents=True, exist_ok=True)
                cache.write_text(json.dumps({"seconds": parse_s, "peak_rss_mb": peak,
                                             "rss_growth_mb": growth,
                                             "measured_on": when,
                                             "pages": [(p.number, p.text) for p in pages]}))
        parsed = [(p.number, p.text) for p in pages]
        t0 = time.perf_counter()
        chunks = [OutChunk(c.index, c.kind, c.text, c.section, c.page_start, c.page_end, c.notes)
                  for c in chunk_structured(pages)]
        timing = Timing(parse_s, time.perf_counter() - t0, peak, growth, when, cached)
    return parsed, chunks, timing


# ---------- scoring ----------

def _flat(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip().lower()


def _value_re(value: str) -> re.Pattern:
    if re.search(r"[A-Za-z]", value):
        return re.compile(re.escape(value).replace(r"\ ", r"\s+"), re.I)
    return re.compile(r"(?<![\d.,])" + re.escape(value) + r"(?![\d.,]*\d)")


def _cells(line: str) -> list[str]:
    return [c.strip() for c in line.strip().strip("|").split("|") if c.strip()]


def score_fact(fact: dict, chunks: list[OutChunk], any_page: bool = False) -> tuple[int, int | None]:
    """Return (level 0-4, index of the best chunk).

    Every chunk of the document that covers the fact's page is tested and the
    best level any single chunk reaches wins (ties keep the earliest chunk).
    This assumes perfect retrieval: it measures whether the information
    survived parsing and chunking, not whether search would find it.
    ``any_page=True`` drops the page restriction (the value may then match an
    unrelated occurrence elsewhere, e.g. a directors' report quoting the P&L).
    """
    vre = _value_re(fact["value"])
    label = _flat(fact["label"])
    page = int(fact["page"])
    best, where = 0, None
    for c in chunks:
        if not any_page and not (c.page_start <= page <= c.page_end):
            continue
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
            parsed, chunks, tm = run_option(opt, pdf, REVIEW / opt / d["key"] / "parsed.json",
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
                "seconds": round(tm.parse_seconds, 1), "pages": page_count,
                "seconds_per_page": round(tm.parse_seconds / page_count, 3),
                "chunk_seconds": round(tm.chunk_seconds, 2),
                "peak_rss_mb": None if tm.peak_rss_mb is None else round(tm.peak_rss_mb),
                "rss_growth_mb": None if tm.rss_growth_mb is None else round(tm.rss_growth_mb),
                "parse_measured_on": tm.measured_on, "parse_cached": tm.cached,
                "pages_without_text": page_count - len(with_text),
                "text_layer_missing": len(no_layer),
                "recovered_by_ocr": len(no_layer & with_text),
                "chunks": len(chunks), "table_chunks": sum(c.kind == "table" for c in chunks),
                "tokens": sum(tokens), "max_chunk_tokens": max(tokens, default=0),
                "multi_page_chunks": sum(c.page_end - c.page_start >= 2 for c in chunks),
                "facts": scores,
            }
            print(f"{tm.parse_seconds:6.1f}s{' (cached)' if tm.cached else ''}  "
                  f"{len(chunks)} chunks  facts {scores}", file=sys.stderr)
            results["_machine"] = _machine()
            results_path.write_text(json.dumps(results, indent=1))
    write_comparison(results, docs_all=list(csv.DictReader((GOLDEN / "compare_docs.csv").open())),
                     facts=facts)
    return 0


def _machine() -> str:
    import os
    import platform
    import psutil
    cpu = platform.processor() or "cpu"
    try:
        cpu = next(l.split(":", 1)[1].strip() for l in open("/proc/cpuinfo")
                   if l.startswith("model name"))
    except Exception:
        pass
    return (f"{cpu}, {os.cpu_count()} logical CPUs, "
            f"{psutil.virtual_memory().total / 2**30:.0f} GB RAM visible, no GPU used")


CORPUS_PAGES = 12_980  # all 228 downloaded PDFs


def _latency_section(results: dict, opts: list[str], docs_all: list[dict]) -> list[str]:
    out = ["\n## Latency (parsing only, CPU)\n",
           f"Machine: {results.get('_machine', 'unknown')}. Parse time excludes chunking "
           "and token counting. Times are wall-clock for one run, not averaged.\n",
           "| Doc | Pages | " + " | ".join(f"{o} s (s/page)" for o in opts) + " |",
           "|---|---|" + "---|" * len(opts)]
    tot_s = {o: 0.0 for o in opts}
    tot_p = 0
    for d in docs_all:
        pages = next((results[o][d["key"]]["pages"] for o in opts if d["key"] in results[o]), None)
        if pages is None:
            continue
        tot_p += pages
        cells = []
        for o in opts:
            r = results[o].get(d["key"])
            if not r:
                cells.append("—")
                continue
            tot_s[o] += r["seconds"]
            cells.append(f"{r['seconds']:,.1f} ({r['seconds'] / r['pages']:.2f})")
        out.append(f"| {d['key']} | {pages} | " + " | ".join(cells) + " |")
    out.append(f"| **Total** | **{tot_p}** | " + " | ".join(
        f"**{tot_s[o]:,.0f} s = {tot_s[o] / 60:.1f} min ({tot_s[o] / tot_p:.2f})**" for o in opts) + " |")
    out.append(f"| Projected: all {CORPUS_PAGES:,} pages | | " + " | ".join(
        _duration(tot_s[o] / tot_p * CORPUS_PAGES) for o in opts) + " |")
    low = sum(r.get("text_layer_missing", 0) for r in results.get("baseline", {}).values()
              if isinstance(r, dict))
    out.append(f"\nProjection scales the golden docs' average s/page. The golden docs are OCR-heavy "
               f"({low} of {tot_p} pages = {low / max(tot_p, 1):.0%} low-text, vs 441 of "
               f"{CORPUS_PAGES:,} = 3.4% across the collection), so options that OCR are likely "
               "*over*-estimated.\n")
    out.append("| Memory while parsing | " + " | ".join(opts) + " |\n|---|" + "---|" * len(opts))
    for label, key in (("Peak process memory (MB)", "peak_rss_mb"),
                       ("Growth during parse (MB)", "rss_growth_mb")):
        vals = []
        for o in opts:
            xs = [r.get(key) for r in results[o].values() if isinstance(r, dict) and r.get(key) is not None]
            vals.append(f"{max(xs):,}" if xs else "not measured")
        out.append(f"| {label} (max over docs) | " + " | ".join(vals) + " |")
    measured = {o: sorted({r.get("parse_measured_on", "?") for r in results[o].values()
                           if isinstance(r, dict)}) for o in opts}
    out.append("\nParse times measured on: " + "; ".join(f"{o} {', '.join(v)}" for o, v in measured.items())
               + ". Options run in one process share memory, so the peak includes earlier "
               "options' loaded models; growth is the fairer per-parser figure.\n")
    return out


def _duration(seconds: float) -> str:
    return f"{seconds / 3600:.1f} h" if seconds >= 3600 else f"{seconds / 60:.0f} min"


def write_comparison(results: dict, docs_all: list[dict], facts: list[dict]) -> None:
    opts = [o for o in OPTIONS if o in results]  # "_machine" is not an option
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
            vals = [v for d in results[o].values() if isinstance(d, dict) for v in d["facts"].values()]
            row.append(f"{sum(v >= lv for v in vals)}/{len(vals)}")
        out.append(f"| ≥ L{lv} | " + " | ".join(row) + " |")
    out += _latency_section(results, opts, docs_all)
    out.append("\n## Per document\n")
    out.append("| Doc | Metric | " + " | ".join(opts) + " |\n|---|---|" + "---|" * len(opts))
    for d in docs_all:
        for m in ("seconds", "seconds_per_page", "pages_without_text", "recovered_by_ocr", "chunks", "table_chunks",
                  "tokens", "max_chunk_tokens", "multi_page_chunks"):
            vals = [str(results[o].get(d["key"], {}).get(m, "—")) for o in opts]
            out.append(f"| {d['key']} | {m} | " + " | ".join(vals) + " |")
    (REVIEW / "COMPARISON.md").write_text("\n".join(out) + "\n")


if __name__ == "__main__":
    sys.exit(main())
