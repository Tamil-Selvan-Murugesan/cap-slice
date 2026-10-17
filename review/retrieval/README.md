# Retrieval runs

Scored against `data/golden/retrieval_questions.csv` (200 questions) with `cap-slice-retrieval-score`.
Each run: `<name>.jsonl` (ranked results per question), `<name>.meta.json` (how it was made),
`<name>.score.md` / `.score.json` (metrics overall and per group, misses, paired comparison).

| Run | Corpus | Strict R@1 | R@5 | R@10 | R@20 | MRR@10 | Lenient R@10 | doc@10 |
|---|---|---|---|---|---|---|---|---|
| `bm25-mineru_advanced` | MinerU advanced, page_clean + structured_chunk, 40,767 chunks | 0.14 | 0.33 | 0.42 | 0.54 | 0.22 | 0.47 | 0.76 |
| `bm25-mineru_advanced-company` | same, search limited to the question's company | 0.19 | 0.39 | 0.49 | 0.64 | 0.28 | 0.54 | 0.82 |

2026-10-17. BM25 keyword baseline (no embeddings) — an end-to-end check of the scorer and the keyword
half of the hybrid-search round in `docs/plan.md`; not a tuned retriever. The company filter wins 13
questions and loses none at R@10 (sign test p < 0.001). doc@10 far above R@10 means the right report
is usually found but not the right page. Multi-page questions are almost never fully found (2 of 15).

Reproduce:

```bash
uv run cap-slice-retrieval-bm25 --parser mineru --cache parsed_advanced --out review/retrieval/bm25-mineru_advanced.jsonl
uv run cap-slice-retrieval-bm25 --parser mineru --cache parsed_advanced --out review/retrieval/bm25-mineru_advanced-company.jsonl --filter-company
uv run cap-slice-retrieval-score review/retrieval/bm25-mineru_advanced-company.jsonl --compare review/retrieval/bm25-mineru_advanced.jsonl
```

The chunk corpus is cached at `parsed_advanced/_chunks/mineru.jsonl` (gitignored, ~47 MB) and is the
input for embedding runs. Any retriever can be scored by writing the same JSONL format.
