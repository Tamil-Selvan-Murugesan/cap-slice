# Retrieval runs

## Round 1 — Voyage 4 Large (2026-10-19)

Dense search with `voyage-4-large` at 2048 dimensions (`cap-slice-retrieval-dense`), bare chunk text, same
40,593 chunks as BM25, Qdrant server collection `r1__voyage-4-large-2048__baseline` (HNSW m 16 /
ef_construct 128, hnsw_ef 128). Embedding: 105 requests, 10.38M tokens, ~8 min.

| Filter | BM25 R@10 | **Voyage R@1** | **R@5** | **R@10** | **R@20** | **MRR@10** | Lenient R@10 | doc@10 | Voyage vs BM25 (R@10, same filter) |
|---|---|---|---|---|---|---|---|---|---|
| none | 0.41 | 0.31 | 0.56 | 0.68 | 0.76 | 0.42 | 0.71 | 0.86 | +63 / −9 |
| company, hard | 0.47 | 0.30 | 0.60 | 0.67 | 0.79 | 0.43 | 0.71 | 0.85 | +54 / −14 |
| company, soft | 0.47 | 0.33 | 0.61 | 0.69 | 0.81 | 0.45 | 0.74 | 0.89 | +57 / −11 |
| question-based, hard | 0.66 | 0.39 | 0.71 | 0.78 | 0.83 | 0.52 | 0.81 | 0.92 | +33 / −9 |
| **question-based, soft** | 0.65 | **0.40** | **0.73** | **0.81** | **0.86** | **0.54** | 0.83 | 0.95 | +37 / −5 |
| question-based + next year, hard | 0.61 | 0.34 | 0.66 | 0.74 | 0.82 | 0.47 | 0.78 | 0.89 | +40 / −14 |
| question-based + next year, soft | 0.61 | 0.36 | 0.69 | 0.78 | 0.86 | 0.50 | 0.81 | 0.92 | +41 / −8 |
| answer key, hard (*upper bound*) | 0.73 | 0.48 | 0.80 | 0.83 | 0.87 | 0.61 | 0.85 | 0.96 | +29 / −8 |
| answer key, soft (*upper bound*) | 0.72 | 0.48 | 0.81 | 0.86 | 0.90 | 0.62 | 0.88 | 0.98 | +34 / −6 |

All Voyage-vs-BM25 differences p ≤ 0.001 (sign test). Within Voyage: question-based soft beats hard +6 / −0
(p = 0.03) and beats company-soft +26 / −4; the company filter alone does nothing for dense search
(+4 / −5 vs no filter) — the embedding already finds the right company. HNSW returns the same top 10 as
exact search for all 200 questions (`…-exact`). Gap to the answer-key upper bound: 0.81 vs 0.86.

By group (question-based soft, strict R@10, BM25 → Voyage): tables 0.78 → 0.94, concall 0.61 → 0.88,
statements 0.56 → 0.80, scanned pages 0.50 → 0.80, charts 0.67 → 0.80, prose 0.73 → 0.79, KPI tiles
0.83 → 0.83; vague questions 0.50 → 0.85, paraphrased 0.69 → 0.86. No group of ≥ 15 questions gets worse.
Unchanged and still the weakest: **multi-page and analytical questions 0.13** (2 of 15 each) — single-chunk
retrieval rarely brings back every page a comparison needs.

## Hybrid BM25 + Voyage (2026-10-19)

RRF (k 60) and DBSF fusion of BM25 and Voyage runs with the same filters: **worse than Voyage alone** in
every production setup (question-based soft: dense 0.81, RRF 0.74, DBSF 0.77). Helps prose and exact-wording
questions, hurts tables, concall and scanned pages; not adopted. Details: `hybrid/README.md`.

## Keyword baseline

Scored against `data/golden/retrieval_questions.csv` (200 questions) with `cap-slice-retrieval-score`.
Each run: `<name>.jsonl` (ranked results per question), `<name>.meta.json` (how it was made),
`<name>.score.md` / `.score.json` (metrics overall and per group, misses, paired comparison).

| Run | Filter | Strict R@1 | R@5 | R@10 | R@20 | MRR@10 | Lenient R@10 | doc@10 |
|---|---|---|---|---|---|---|---|---|
| `bm25-mineru_advanced` | none | 0.17 | 0.35 | 0.41 | 0.54 | 0.24 | 0.46 | 0.74 |
| `bm25-mineru_advanced-company` | company, hard | 0.20 | 0.39 | 0.47 | 0.62 | 0.28 | 0.53 | 0.82 |
| `…-company-soft` | company, soft | 0.20 | 0.39 | 0.47 | 0.61 | 0.28 | 0.52 | 0.81 |
| `…-question` | **question-based** (company + year + doc type), hard | 0.30 | 0.58 | **0.66** | 0.74 | 0.41 | 0.69 | 0.94 |
| `…-question-soft` | question-based, soft | 0.30 | 0.57 | 0.65 | 0.72 | 0.41 | 0.69 | 0.94 |
| `…-question_next` | question-based + next fiscal year, hard | 0.29 | 0.53 | 0.61 | 0.71 | 0.39 | 0.67 | 0.93 |
| `…-question_next-soft` | question-based + next fiscal year, soft | 0.29 | 0.52 | 0.61 | 0.70 | 0.38 | 0.67 | 0.93 |
| `…-answer_key` | answer key, hard (*upper bound*) | 0.40 | 0.69 | 0.73 | 0.81 | 0.51 | 0.77 | 0.99 |
| `…-answer_key-soft` | answer key, soft (*upper bound*) | 0.39 | 0.67 | 0.72 | 0.79 | 0.50 | 0.76 | 0.99 |
| *before the chunker fixes (2026-10-17)* | none / company | 0.14 / 0.19 | 0.33 / 0.39 | 0.42 / 0.49 | 0.54 / 0.64 | 0.22 / 0.28 | 0.47 / 0.54 | 0.76 / 0.82 |

All on MinerU advanced → page_clean → structured_chunk (after fixes S13–S21), 40,593 chunks.

**Filters (2026-10-19).** Question-based filters come from `query_reader.read()` (sees only the question;
`review/query_reader/`). Against the company filter at R@10: question-based hard **+38 / −1** (p < 0.001),
soft +36 / −1, next-year +29 / −1, answer key +53 / −1. Soft multiplies a chunk's score by 1.5 per matching
field (fixed before the run, not tuned), which at three fields is close to a hard filter. Keeping the next
fiscal year as well rescues 7 questions whose answer sits in the following year's filing, but doubles the
pool and loses more to look-alike pages. Caveats: the reader's rules were corrected once on this set (three
general phrasings, `review/query_reader/README.md`), and these questions name a period more often than real
users might — the gap to the answer key (0.66 vs 0.73) is the reader's cost here.

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
# filter setups: --filter company|question|question_next|answer_key [--soft]
uv run cap-slice-retrieval-bm25 --parser mineru --cache parsed_advanced --filter question --out review/retrieval/bm25-mineru_advanced-question.jsonl
```

The chunk corpus is cached at `parsed_advanced/_chunks/mineru.jsonl` (gitignored, ~47 MB) and is the
input for embedding runs. Any retriever can be scored by writing the same JSONL format.
