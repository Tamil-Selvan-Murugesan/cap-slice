"""Keyword (BM25) baseline retriever for the retrieval question set — no embeddings, no API calls.

    uv run cap-slice-retrieval-bm25 --parser mineru --cache parsed_advanced --out review/retrieval/bm25.jsonl
    uv run cap-slice-retrieval-bm25 ... --filter-company    # search only the question's company
    uv run cap-slice-retrieval-bm25 ... --filter question_next --soft

Filters (docs/plan.md, Filters): `company` (the question's company), `question` (company + fiscal years +
doc type from query_reader.read(), which sees only the question), `question_next` (the same, also keeping
the following fiscal year), `answer_key` (the gold document's own metadata: an upper bound, never a
production number). Hard (default) searches only the documents the filter keeps; --soft searches
everything and multiplies a chunk's score by SOFT_BOOST for each filter field its document matches.
SOFT_BOOST was fixed before the first run and is not tuned on the question set.

Builds the chunk corpus the experiments use (every document in the cache -> page_clean.py ->
structured_chunk.py; the same path as cap-slice-score --clean), ranks chunks for each question with
BM25 and writes a run file for cap-slice-retrieval-score. The corpus is cached as JSONL (--chunks,
default <cache>/_chunks/<parser>.jsonl, gitignored) and reused by later runs, including embedding runs.

It serves two purposes: an end-to-end check of the scorer, and the keyword half of round 4 (hybrid
search) in docs/plan.md.
"""

from __future__ import annotations

import argparse
import collections
import json
import math
import re
from pathlib import Path

from cap_slice.downloader import REPO_ROOT
from cap_slice.retrieval_score import load_questions

TOKEN = re.compile(r"[a-z]+|\d[\d,]*(?:\.\d+)?")
SOFT_BOOST = 1.5
STOP = set("a an and are as at be by did do does for from has have how in is it its of on or the to "
           "was what when where which who why with".split())


def tokens(text: str) -> list[str]:
    out = []
    for t in TOKEN.findall(text.lower()):
        t = t.rstrip(",").replace(",", "")
        if t and t not in STOP:
            out.append(t)
    return out


def build_corpus(cache: Path, parser: str) -> list[dict]:
    from cap_slice.page_clean import clean_pages
    from cap_slice.parsing import ParsedPage
    from cap_slice.structured_chunk import chunk_structured

    chunks = []
    for f in sorted((cache / parser).glob("*/*/*/pages.json")):
        doc = "data/" + str(f.parent.relative_to(cache / parser)) + ".pdf"
        pages, _ = clean_pages(json.loads(f.read_text())["pages"], REPO_ROOT / doc)
        for c in chunk_structured([ParsedPage(n, t) for n, t in pages]):
            chunks.append({"doc": doc, "chunk": c.index, "kind": c.kind, "section": c.section,
                           "page_start": c.page_start, "page_end": c.page_end, "text": c.text})
    return chunks


def load_or_build(path: Path, cache: Path, parser: str) -> list[dict]:
    if path.exists():
        return [json.loads(l) for l in path.read_text().splitlines() if l.strip()]
    chunks = build_corpus(cache, parser)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(json.dumps(c) for c in chunks) + "\n")
    return chunks


class BM25:
    def __init__(self, docs: list[list[str]], k1: float = 1.2, b: float = 0.75):
        self.k1, self.b = k1, b
        self.len = [len(d) for d in docs]
        self.avg = sum(self.len) / len(docs)
        self.post = collections.defaultdict(list)
        for i, d in enumerate(docs):
            for t, tf in collections.Counter(d).items():
                self.post[t].append((i, tf))
        n = len(docs)
        self.idf = {t: math.log(1 + (n - len(p) + 0.5) / (len(p) + 0.5)) for t, p in self.post.items()}

    def search(self, query: list[str], allowed: set[int] | None = None) -> dict[int, float]:
        scores = collections.defaultdict(float)
        for t in set(query):
            for i, tf in self.post.get(t, ()):
                if allowed is None or i in allowed:
                    norm = tf + self.k1 * (1 - self.b + self.b * self.len[i] / self.avg)
                    scores[i] += self.idf[t] * tf * (self.k1 + 1) / norm
        return scores


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--parser", default="mineru")
    ap.add_argument("--cache", type=Path, default=Path("parsed_advanced"))
    ap.add_argument("--out", type=Path, default=Path("review/retrieval/bm25.jsonl"))
    ap.add_argument("--chunks", type=Path, help="corpus cache (default <cache>/_chunks/<parser>.jsonl, gitignored)")
    ap.add_argument("--top", type=int, default=50)
    ap.add_argument("--filter-company", action="store_true", help="same as --filter company")
    ap.add_argument("--filter", choices=["none", "company", "question", "question_next", "answer_key"], default="none")
    ap.add_argument("--soft", action="store_true", help="boost matching documents instead of excluding the rest")
    args = ap.parse_args(argv)
    if args.filter_company:
        args.filter = "company"

    chunks_path = args.chunks or args.cache / "_chunks" / f"{args.parser}.jsonl"
    chunks = load_or_build(chunks_path, args.cache, args.parser)
    index = BM25([tokens(c["section"] + "\n" + c["text"]) for c in chunks])
    meta = {}
    if args.filter != "none":
        from cap_slice.query_reader import answer_key_filter, doc_meta, keeps, read
        meta = doc_meta()
    fields = {"none": (), "company": ("symbol",), "question": ("symbol", "year", "doc_type"),
              "question_next": ("symbol", "year", "doc_type"), "answer_key": ("symbol", "year", "doc_type")}[args.filter]
    nxt = args.filter == "question_next"

    lines = []
    for q in load_questions():
        if args.filter == "none":
            scores = index.search(tokens(q["question"]))
        else:
            f = answer_key_filter(q, meta) if args.filter == "answer_key" else read(q["question"])
            docs = {c["doc"] for c in chunks}
            if args.soft:
                matched = {d: sum(keeps(f, meta[d], (fld,), nxt) for fld in fields) for d in docs}
                scores = {i: s * SOFT_BOOST ** matched[chunks[i]["doc"]]
                          for i, s in index.search(tokens(q["question"])).items()}
            else:
                kept = {d for d in docs if keeps(f, meta[d], fields, nxt)}
                allowed = {i for i, c in enumerate(chunks) if c["doc"] in kept}
                scores = index.search(tokens(q["question"]), allowed)
        top = sorted(scores.items(), key=lambda kv: -kv[1])[:args.top]
        lines.append(json.dumps({"qid": q["qid"], "results": [
            {"doc": chunks[i]["doc"], "chunk": chunks[i]["chunk"], "page_start": chunks[i]["page_start"],
             "page_end": chunks[i]["page_end"], "score": round(s, 4)} for i, s in top]}))
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text("\n".join(lines) + "\n")
    meta = {"retriever": "bm25", "parser": args.parser, "cache": str(args.cache), "chunks": str(chunks_path),
            "n_chunks": len(chunks), "documents": len({c["doc"] for c in chunks}),
            "filter": args.filter, "soft": args.soft, "soft_boost": SOFT_BOOST if args.soft else None,
            "top": args.top}
    args.out.with_suffix(".meta.json").write_text(json.dumps(meta, indent=1))
    print(f"{len(chunks)} chunks from {meta['documents']} documents; wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
