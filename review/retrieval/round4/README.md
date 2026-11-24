# Round 4 — reranker (2026-11-24)

**Winner: Voyage `rerank-3` on the top 50 candidates** of b2 dense search with question-based soft filters.
Strict R@10 **0.865 → 0.915** (+10 / −0 questions, sign test p = 0.002), R@1 0.51 → 0.605, MRR@10 0.642 → 0.722,
R@20 0.91 → 0.94. No group of ≥ 15 questions drops; most rise. Hybrid BM25 + dense, re-tested with the reranker,
adds nothing and stays rejected. Round 3 (images) was moved after the answer step
([`../images-precheck.md`](../images-precheck.md)).

## Setup

Held fixed: MinerU advanced pages, b2 chunks (round 2), Voyage 4 Large 2048-dim vectors (restored from R2 with
`tools/restore_vectors_r2.sh`), Qdrant server, the 200 frozen questions. The first stage was re-run to depth 100
(`--top 100`) and reproduces round 2 exactly (question-based soft 0.865, no filter 0.83).

The reranker (`cap-slice-retrieval-rerank`, `src/cap_slice/retrieval_rerank.py`) scores each candidate against the
question text and re-orders them. Fixed before any run:

- it sees what was embedded for the chunk — b2's context header + heading path + chunk text;
- its order replaces the first-stage order (the soft filter's boost is not re-applied; the filter only decides
  which candidates get reranked);
- depths 20 / 50 / 100 from one set of scores (a pair's score doesn't depend on the other documents), cached per
  (question, chunk) in `parsed_advanced/_rerank/` (gitignored).

rerank-3: $0.05 per 1M tokens, 200M free (docs.voyageai.com pricing, checked 2026-11-24). This round used about
**15M tokens** (6.7M for 100 candidates × 200 questions; 3.7M more for the unfiltered candidates; 4.6M more for the
BM25 candidates), so $0 within the free tier. About 0.9 s per question for 100 candidates, sequential.

## Results

| Setup (strict) | R@1 | R@5 | R@10 | R@20 | MRR@10 | lenient R@10 | vs b2 (gained / lost) |
|---|---|---|---|---|---|---|---|
| b2, question-based soft (round 2 winner) | 0.510 | 0.820 | 0.865 | 0.910 | 0.642 | 0.880 | — |
| + rerank top 20 | 0.600 | 0.860 | 0.910 | 0.910 | 0.72 | 0.92 | +8 / −0 (p 0.008) |
| **+ rerank top 50** | **0.605** | **0.865** | **0.915** | **0.940** | **0.722** | **0.920** | **+10 / −0 (p 0.002)** |
| + rerank top 100 | 0.600 | 0.860 | 0.910 | 0.940 | 0.72 | 0.92 | +10 / −1 (p 0.012) |
| hybrid (dense ∪ BM25 top 50) + rerank | 0.600 | 0.850 | 0.910 | 0.940 | 0.72 | 0.92 | +10 / −1 |
| hybrid (top 100 each) + rerank | 0.590 | 0.850 | 0.910 | 0.940 | 0.71 | 0.92 | +11 / −2 |
| b2, no filter | 0.475 | 0.770 | 0.830 | 0.910 | 0.598 | 0.855 | — |
| b2, no filter + rerank top 50 | 0.600 | 0.865 | 0.915 | 0.950 | 0.715 | 0.925 | +18 / −1 vs no filter |

Groups of ≥ 15 questions (strict R@10): b2 → + rerank top 50

| Group | n | b2 | rerank 50 | Group | n | b2 | rerank 50 |
|---|---|---|---|---|---|---|---|
| tables | 63 | 0.95 | **1.00** | concall evidence | 33 | 0.94 | **1.00** |
| prose | 33 | 0.85 | 0.94 | statements | 25 | 0.92 | 0.96 |
| spoken numbers | 16 | 0.88 | 1.00 | decoy years | 63 | 0.89 | 0.94 |
| standalone vs consolidated | 22 | 0.86 | 0.91 | exact wording | 25 | 0.88 | 0.96 |
| multi-page / analytical | 15 | 0.33 | 0.40 | cross-document | 17 | 0.41 | 0.53 |
| charts | 15 | 0.80 | 0.80 | vague | 20 | 0.95 | 0.95 |
| Hero MotoCorp | 54 | 0.85 | 0.89 | Esconet | 21 | 0.81 | 0.90 |

Gained (b2 rank → reranked rank): R013 11→3, R028 14→4, R030 13→2, R050 37→1, R088 26→7, R098 42→10, R156 20→3,
R173 13→7, R179 44→9, R199 12→8. Lost: none (at depth 100: R116 10→12).

## Reading the results

- **The reranker fixes the "just missed" pages.** Round 2 left 9 answers at ranks 11–20 and 8 at 21–50; a
  model that reads the question and the chunk together puts most of them in the top 10, often near the top
  (R050 37 → 1). The right page is now first for 6 questions in 10.
- **Depth 50 is enough.** 20 already gets +8; 100 adds nothing and loses R116. 50 is the setting.
- **After reranking, the filter hardly matters overall.** No filter + rerank (0.915) equals filtered + rerank
  (0.915); the reranker reads company and year from b2's header. The groups differ a little both ways (Hero 0.85 vs
  0.89 filtered; standalone vs consolidated 0.95 vs 0.91), so the filter stays: it is free and keeps wrong-company
  pages out of the candidates.
- **Hybrid stays rejected.** Adding BM25's candidates gives the reranker more to choose from, but it finds nothing
  dense search hadn't already offered (0.91 vs 0.915).
- **What's left: 17 misses** — 9 multi-page, 3 charts, 2 prose, 1 KPI, 1 scanned, 1 statement. For 10 of them the
  answer page is not in the top 50 at all, so a reranker can't reach it. Multi-page questions improved only to 6 of
  15: they need several pages together, which is a job for the answer step (fetch neighbouring chunks, combine), not
  for ranking single chunks. The chart misses are the parser gap in the images pre-check.

## Decision

Adopt rerank-3 on the top 50 after b2 dense search with question-based soft filters. Production per question: one
query embedding, one Qdrant search, one rerank call of 50 chunks (~17K tokens, ≈ $0.0008 at list price). An
open-weights reranker (e.g. bge-reranker-v2-m3) is to be compared later on a GPU pod, as is round 5 (re-check).
