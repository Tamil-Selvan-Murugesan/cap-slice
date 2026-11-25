"""Round 4: rerank a retrieval run's candidates with a Voyage reranker (docs/plan.md, round 4).

    uv run cap-slice-retrieval-rerank review/retrieval/round4/dense-...-question-soft-top100.jsonl --depth 50 100
    uv run cap-slice-retrieval-rerank DENSE.jsonl --union BM25.jsonl --depth 100 --tag hybrid   # hybrid + rerank

For every question, the first `depth` candidates of the run (plus, with --union, the first `depth` of a second run
not already in the list) are scored by the reranker against the question text, and written in reranker order to
review/retrieval/round4/<run>-rerank-<model>-d<depth>.jsonl in the run format the scorer reads.

The reranker sees what was embedded for the chunk (`embed_text` of the corpus: in b2, the context header + heading
path + chunk text), fixed before any run. Scores are cached per (question, document, chunk) in
parsed_advanced/_rerank/<model>__<corpus>.jsonl, so deeper or overlapping candidate lists only pay for new pairs
and an interrupted run resumes. A pair's score does not depend on the other documents in the request.
"""
import argparse
import csv
import json
import os
import time
from pathlib import Path

from .downloader import REPO_ROOT

QUESTIONS = REPO_ROOT / "data" / "golden" / "retrieval_questions.csv"
CHUNKS = REPO_ROOT / "parsed_advanced" / "_chunks"
CACHE = REPO_ROOT / "parsed_advanced" / "_rerank"
OUT = REPO_ROOT / "review" / "retrieval" / "round4"

PRICES = {"rerank-3": 0.05}  # USD per 1M tokens, docs.voyageai.com/docs/pricing (checked 2026-11-24; 200M free)
MAX_REQUEST_TOKENS = 500_000  # API limit 600K: query tokens x documents + document tokens


def load_texts(corpus: str) -> dict[tuple[str, int], str]:
    path = CHUNKS / (f"r2-{corpus}.jsonl" if corpus else "mineru.jsonl")
    out = {}
    for line in path.open():
        c = json.loads(line)
        out[(c["doc"], c.get("parent", c["chunk"]))] = c.get("embed_text", c["text"])
    return out


def read_run(path: Path) -> dict[str, list[dict]]:
    return {r["qid"]: r["results"] for r in map(json.loads, path.open())}


class Cache:
    def __init__(self, path: Path):
        self.path, self.d = path, {}
        if path.exists():
            for line in path.open():
                r = json.loads(line)
                self.d[(r["qid"], r["doc"], r["chunk"])] = r["score"]
        path.parent.mkdir(parents=True, exist_ok=True)
        self.f = path.open("a")

    def add(self, qid, doc, chunk, score):
        self.d[(qid, doc, chunk)] = score
        self.f.write(json.dumps({"qid": qid, "doc": doc, "chunk": chunk, "score": score}) + "\n")
        self.f.flush()


def rerank(client, model, query, docs, ntok):
    """Score docs in requests that stay under the per-request token limit; returns scores in input order."""
    scores, i, used = [None] * len(docs), 0, 0
    qt = ntok([query])[0]
    lens = ntok(docs)
    while i < len(docs):
        j, tot = i, 0
        while j < len(docs) and (tot + lens[j] + qt) <= MAX_REQUEST_TOKENS and j - i < 1000:
            tot += lens[j] + qt
            j += 1
        j = max(j, i + 1)
        for attempt in range(6):
            try:
                r = client.rerank(query, docs[i:j], model=model, truncation=True)
                break
            except Exception:
                if attempt == 5:
                    raise
                time.sleep(2 ** attempt * 5)
        for res in r.results:
            scores[i + res.index] = res.relevance_score
        used += r.total_tokens
        i = j
    return scores, used


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("run", type=Path)
    ap.add_argument("--union", type=Path, help="second run whose candidates are added (hybrid + rerank)")
    ap.add_argument("--depth", type=int, nargs="+", default=[100])
    ap.add_argument("--model", default="rerank-3")
    ap.add_argument("--corpus", default="b2", help="round-2 corpus whose embed_text the reranker sees ('' = baseline)")
    ap.add_argument("--tag", default="", help="name part for the output (default: the run's name)")
    ap.add_argument("--limit", type=int, default=0, help="first N questions only (dry run)")
    ap.add_argument("--out-dir", type=Path, default=OUT)
    ap.add_argument("--questions", type=Path, help="qid,question CSV (default: the 200-question set)")
    args = ap.parse_args(argv)

    import voyageai
    client = voyageai.Client(max_retries=5)
    ntok = lambda ts: [len(t) for t in client.tokenize(ts, model="voyage-4-large")]  # noqa: E731  close enough
    questions = {r["qid"]: r["question"] for r in csv.DictReader((args.questions or QUESTIONS).open())}
    texts = load_texts(args.corpus)
    runs = [read_run(args.run)] + ([read_run(args.union)] if args.union else [])
    cache = Cache(CACHE / f"{args.model}__{args.corpus or 'baseline'}.jsonl")
    qids = [q for q in runs[0] if q in questions][: args.limit or None]
    deepest = max(args.depth)

    used, t0 = 0, time.time()
    for n, qid in enumerate(qids, 1):
        cands = []
        for run in runs:
            seen = {(c["doc"], c["chunk"]) for c in cands}
            cands += [c for c in run.get(qid, [])[:deepest] if (c["doc"], c["chunk"]) not in seen]
        todo = [c for c in cands if (qid, c["doc"], c["chunk"]) not in cache.d]
        if todo:
            sc, u = rerank(client, args.model, questions[qid], [texts[(c["doc"], c["chunk"])] for c in todo], ntok)
            for c, s in zip(todo, sc):
                cache.add(qid, c["doc"], c["chunk"], s)
            used += u
        if n % 20 == 0 or n == len(qids):
            print(f"[{n}/{len(qids)}] {used:,} tokens this run, {time.time() - t0:.0f}s", flush=True)

    args.out_dir.mkdir(parents=True, exist_ok=True)
    base = args.tag or args.run.stem
    for d in args.depth:
        out = args.out_dir / f"{base}-rerank-{args.model}-d{d}{'-dryrun' if args.limit else ''}.jsonl"
        with out.open("w") as f:
            for qid in qids:
                cands = []
                for run in runs:
                    seen = {(c["doc"], c["chunk"]) for c in cands}
                    cands += [c for c in run.get(qid, [])[:d] if (c["doc"], c["chunk"]) not in seen]
                ranked = sorted(cands, key=lambda c: -cache.d[(qid, c["doc"], c["chunk"])])
                f.write(json.dumps({"qid": qid, "results": [
                    {"doc": c["doc"], "chunk": c["chunk"], "page_start": c["page_start"], "page_end": c["page_end"],
                     "score": round(cache.d[(qid, c["doc"], c["chunk"])], 5), "first_stage": c.get("score")}
                    for c in ranked]}) + "\n")
        out.with_suffix(".meta.json").write_text(json.dumps({
            "run": str(args.run.relative_to(REPO_ROOT) if args.run.is_absolute() else args.run),
            "union": str(args.union) if args.union else None, "depth": d, "model": args.model,
            "reranker_sees": f"embed_text of corpus {args.corpus or 'baseline'}", "questions": len(qids),
            "tokens_this_run": used, "usd_this_run": round(used / 1e6 * PRICES.get(args.model, 0), 4),
            "date": time.strftime("%Y-%m-%d")}, indent=1))
        print(f"wrote {out}")


if __name__ == "__main__":
    main()
