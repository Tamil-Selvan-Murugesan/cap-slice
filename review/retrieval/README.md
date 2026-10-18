# Retrieval runs

Scored against `data/golden/retrieval_questions.csv` (200 questions) with `cap-slice-retrieval-score`.
Each run: `<name>.jsonl` (ranked results per question), `<name>.meta.json` (how it was made),
`<name>.score.md` / `.score.json` (metrics overall and per group, misses, paired comparison).

| Run | Corpus | Strict R@1 | R@5 | R@10 | R@20 | MRR@10 | Lenient R@10 | doc@10 |
|---|---|---|---|---|---|---|---|---|
| `bm25-mineru_advanced` | MinerU advanced, page_clean + structured_chunk (after fixes S13–S21), 40,593 chunks | 0.17 | 0.35 | 0.41 | 0.54 | 0.24 | 0.46 | 0.74 |
| `bm25-mineru_advanced-company` | same, search limited to the question's company | 0.20 | 0.39 | 0.47 | 0.62 | 0.28 | 0.53 | 0.82 |
| *before the chunker fixes (2026-10-17)* | 40,767 chunks | 0.14 / 0.19 | 0.33 / 0.39 | 0.42 / 0.49 | 0.54 / 0.64 | 0.22 / 0.28 | 0.47 / 0.54 | 0.76 / 0.82 |

**Chunker fixes S13–S21 (2026-10-18):** top-1 up (0.14 → 0.17, 0.19 → 0.20), top-10 flat within noise
(+2/−6 and +5/−9 questions, sign test p = 0.29 and 0.42). The losses are questions moving across the
top-10 line (rank 9–10 → 11–15) plus one lucky hit removed (R188 had matched the policy text that the old
chunker mislabelled with the next note's heading). Keyword search barely uses section labels and table
context, which is most of what the fixes change; the golden sets did improve (MinerU advanced v2+v3 L4
227 → 235, Paddle 236 → 243, no fact worse).

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
