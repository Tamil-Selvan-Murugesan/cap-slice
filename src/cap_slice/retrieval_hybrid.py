"""Hybrid search: fuse a keyword (BM25) run and a dense run — round 4 in docs/plan.md.

    uv run cap-slice-retrieval-hybrid BM25_RUN DENSE_RUN --method rrf --out review/retrieval/hybrid/x.jsonl

Inputs are two run files (cap-slice-retrieval-bm25 / cap-slice-retrieval-dense, made with the same
filter setup and --top 100). A chunk is identified by (doc, chunk index), so the same chunk found by
both retrievers is merged. Two standard fusions, as in Qdrant's hybrid queries, with parameters fixed
before the first run (not tuned on the question set):

  rrf   Reciprocal Rank Fusion: score = sum over lists of 1 / (RRF_K + rank), RRF_K = 60. Uses ranks only,
        so BM25 and cosine scales don't matter.
  dbsf  Distribution-Based Score Fusion: in each list, scores are scaled to 0-1 between mean - 3 sd and
        mean + 3 sd (clipped), then summed; a chunk missing from a list adds 0.

Writes the fused top 50 in the scorer's run format, plus <out>.meta.json.
"""

from __future__ import annotations

import argparse
import json
import statistics
from pathlib import Path

RRF_K = 60
TOP = 50


def load(path: Path) -> dict[str, list[dict]]:
    return {r["qid"]: r["results"] for r in map(json.loads, path.read_text().splitlines()) if r}


def rrf(lists: list[list[dict]]) -> dict[tuple, float]:
    out: dict[tuple, float] = {}
    for results in lists:
        for rank, r in enumerate(results, 1):
            key = (r["doc"], r["chunk"])
            out[key] = out.get(key, 0.0) + 1.0 / (RRF_K + rank)
    return out


def dbsf(lists: list[list[dict]]) -> dict[tuple, float]:
    out: dict[tuple, float] = {}
    for results in lists:
        if not results:
            continue
        scores = [r["score"] for r in results]
        mean = statistics.fmean(scores)
        sd = statistics.pstdev(scores) if len(scores) > 1 else 0.0
        lo, hi = mean - 3 * sd, mean + 3 * sd
        for r in results:
            norm = 1.0 if hi == lo else min(1.0, max(0.0, (r["score"] - lo) / (hi - lo)))
            key = (r["doc"], r["chunk"])
            out[key] = out.get(key, 0.0) + norm
    return out


def fuse(a: dict[str, list[dict]], b: dict[str, list[dict]], method: str, top: int = TOP) -> list[dict]:
    lines = []
    for qid in a:
        lists = [a[qid], b.get(qid, [])]
        info = {(r["doc"], r["chunk"]): r for results in lists for r in results}
        scores = (rrf if method == "rrf" else dbsf)(lists)
        ranked = sorted(scores.items(), key=lambda kv: -kv[1])[:top]
        lines.append({"qid": qid, "results": [
            {"doc": d, "chunk": c, "page_start": info[(d, c)]["page_start"],
             "page_end": info[(d, c)]["page_end"], "score": round(s, 6)} for (d, c), s in ranked]})
    return lines


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("bm25", type=Path)
    ap.add_argument("dense", type=Path)
    ap.add_argument("--method", choices=["rrf", "dbsf"], default="rrf")
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args(argv)
    a, b = load(args.bm25), load(args.dense)
    if set(a) != set(b):
        raise SystemExit("the two runs cover different questions")
    lines = fuse(a, b, args.method)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text("\n".join(json.dumps(x) for x in lines) + "\n")
    meta = {"retriever": "hybrid", "method": args.method, "rrf_k": RRF_K if args.method == "rrf" else None,
            "inputs": [str(args.bm25), str(args.dense)],
            "input_meta": [json.loads(p.with_suffix(".meta.json").read_text())
                           for p in (args.bm25, args.dense) if p.with_suffix(".meta.json").exists()],
            "top": TOP}
    args.out.with_suffix(".meta.json").write_text(json.dumps(meta, indent=1))
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
