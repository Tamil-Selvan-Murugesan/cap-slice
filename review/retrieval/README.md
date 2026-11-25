# Retrieval runs

## Query expansion (2026-11-25)

Claude Sonnet 5.5 splits multi-fact questions into sub-queries; each runs the production pipeline; the lists are
merged **round-robin** (adopted provisionally): R@10 0.915 → **0.93** (+3 / −0), multi-page questions with all pages
in the top 10 5 → 8 of 14. Reranking the union against the original question undoes the gain (the reranker prefers
pages about the whole question). [`expand/README.md`](expand/README.md). S22 (concall chunks as turns):
[`s22/README.md`](s22/README.md).

## Round 4 — reranker (2026-11-24)

**Voyage rerank-3 on the top 50 adopted.** After b2 dense search with question-based soft filters: strict R@10
**0.865 → 0.915** (+10 / −0, p = 0.002), R@1 0.51 → 0.605, MRR@10 0.642 → 0.722; no group down, tables and concall
evidence at 1.00. Depth 20 gives +8, 100 adds nothing. With the reranker, no filter (0.915) equals filtered.
Hybrid BM25 + dense + rerank adds nothing (0.91). 17 misses left, 9 multi-page; 10 of the 17 are not in the top 50.
~15M rerank tokens (free tier). [`round4/README.md`](round4/README.md).

**Images pre-check (2026-11-24):** round 3 (images) moved after the answer step and round 4 (reranker) runs
next. Only 4–5 image questions still miss, and 3 of the 4 chart misses are a parsing gap: the values are printed
as text in the PDF, but MinerU dropped the chart (and its own picture descriptions don't hold them).
[`images-precheck.md`](images-precheck.md).

## Round 2 — chunking (2026-11-24)

**b2 adopted**: a context header (company · document · period · standalone/consolidated) and the heading path are
embedded with every chunk; the returned text is unchanged. Strict R@10 with question-based soft filters
**0.805 → 0.865** (+13 / −1 questions, sign test p = 0.002), no filter 0.675 → 0.830, no group of ≥ 15 questions
down. Header only (b1) 0.860; table descriptors (c) 0.750, concall exchanges + one slide per chunk (d) 0.790,
small-to-big (e) 0.800 — not adopted. The header and the filters fix the same problem (look-alike pages from
other years or the other statement set): with b2 the soft filter adds 0.035 instead of 0.13. Details, all runs
and backups: [`round2/README.md`](round2/README.md); tables: [`round2/results.md`](round2/results.md).

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

## Round 1 — Nemotron 3 Embed 8B, BF16 (2026-10-19)

`nvidia/Nemotron-3-Embed-8B-BF16`, self-hosted on RunPod behind an OpenAI-compatible `/v1/embeddings`
(`cap-slice-retrieval-dense --provider openai`), `dimensions` 2048 (= the first 2048 of its native 4096,
renormalised — checked against a 4096 request), prompts `passage: ` / `query: ` added by the runner because
the server ignores `input_type`. 1,271 requests, 10.88M tokens, ~21 min. Checked before the pod was
released: 30 random chunks and 10 questions re-embedded one at a time match the stored vectors (cosine
≥ 0.9999; a one-row-shifted control gives 0.50); identical texts ≥ 0.9995; questions without the `query: `
prompt score R@10 0.52 instead of 0.59. Collection `r1__nemotron-3-embed-8b-bf16-2048__baseline`; HNSW top 10
identical to exact search.

| Filter | BM25 | Voyage 4 Large | **Nemotron 3 Embed 8B** | Nemotron vs Voyage (R@10) |
|---|---|---|---|---|
| none | 0.41 | **0.68** | 0.59 | +14 / −30 (p = 0.02) |
| company, hard | 0.47 | **0.67** | 0.63 | +17 / −25 |
| company, soft | 0.47 | **0.69** | 0.63 | +12 / −25 (p = 0.05) |
| question-based, hard | 0.66 | **0.78** | 0.76 | +11 / −14 |
| question-based, soft | 0.65 | **0.81** | 0.76 | +6 / −15 (p = 0.08) |
| question-based + next year, soft | 0.61 | **0.78** | 0.70 | +8 / −22 (p = 0.02) |
| answer key, soft (*upper bound*) | 0.72 | **0.86** | 0.81 | +5 / −14 |

Nemotron, question-based soft: R@1 0.38, R@5 0.67, R@20 0.81, MRR@10 0.50. By group (strict R@10, Voyage →
Nemotron): ties on prose 0.79, charts 0.80, scanned pages 0.80, vague questions 0.85, APAR 0.83, C2C 0.89;
Nemotron better on exact-wording questions 0.84 → 0.92 and multi-page / analytical 0.13 → 0.20 (2 → 3 of 15);
worse on tables 0.94 → 0.87, concall 0.88 → 0.79, statements 0.80 → 0.72, KPI tiles 0.83 → 0.67, paraphrased
questions 0.86 → 0.78, and E2E 0.81 → 0.63 (43 questions). **Voyage 4 Large wins round 1**; filters narrow
the gap (no filter −0.09, question-based −0.05). Nemotron's native 4096 dimensions were not run.

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
