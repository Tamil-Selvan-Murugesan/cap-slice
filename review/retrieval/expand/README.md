# Multi-query expansion (2026-11-25)

**Update 2026-11-25: confirmed on the fresh question set** (`review/retrieval/fresh/`): 50 unseen questions, every
page per fact keyed; B finds 13 of 14 multi-page questions vs 11, R@10 0.90 → 0.94 (+2 / −0). Pooled +5 / −0.
B is adopted.

**Result: round-robin merge (B) adopted provisionally.** Multi-page questions answered with all pages in the top 10:
**5 → 8 of 14**; strict R@10 **0.915 → 0.93** (+3 / −0, sign test p = 0.25), R@1 unchanged (0.62), no group of ≥ 15
questions drops. Three wins is too few to be sure; the fresh question set (more multi-page questions) decides.

## What it does

`cap-slice-query-expand` (`src/cap_slice/query_expand.py`). Every question goes once to **Claude Sonnet 5.5**
(`claude-sonnet-5-5`, effort medium, structured JSON output, server-side refusal fallback on — never triggered:
every plan was answered by Sonnet 5.5). The prompt, fixed before any run (hash `05b1e0cac1d0`, stored with each
plan), asks whether one search can find everything the answer needs; if not, it returns 2–4 self-contained
sub-queries, one fact each, naming company, period and scope. Plans are committed in `plans.jsonl` because the model
can't be made deterministic.

- Single-search questions keep the production results unchanged (b2s, question-based soft filter, rerank-3 top 50).
- Each sub-query runs through the same production pipeline (question-reader soft filter → dense top 100 → rerank-3
  top 50 against the sub-query).
- The original's list and the sub-query lists are merged three ways, fixed in advance:
  **A** union reranked against the original question; **B** round-robin (best of each list in turn, original
  first); **C** reciprocal rank fusion (k = 60).

Planner: 35 of 200 questions flagged multi, 77 sub-queries; it caught 12 of the 14 multi-page questions (missed
R161, R198). The other 23 flagged questions ask for two facts that sit on one page (e.g. a year and its comparative).
Cost: 142K input + 18K output tokens ≈ $0.46 for 200 questions (~$0.002 per question); 2.0M rerank-3 tokens.

## Results (strict, all 200 questions)

| Setup | R@1 | R@5 | R@10 | R@20 | MRR@10 | lenient R@10 | multi-page (14) all pages in top 10 | vs production |
|---|---|---|---|---|---|---|---|---|
| production (b2s + rerank-3 top 50) | 0.620 | 0.860 | 0.915 | 0.940 | 0.730 | 0.92 | 5 | — |
| A: union, reranked against the original | 0.620 | 0.860 | 0.915 | 0.940 | 0.730 | 0.92 | 5 | +0 / −0 |
| **B: round-robin** | 0.620 | **0.875** | **0.930** | 0.945 | **0.733** | **0.94** | **8** | **+3 / −0** |
| C: RRF | 0.605 | 0.870 | 0.930 | 0.945 | 0.723 | 0.93 | 8 | +3 / −1 |

B wins R062 (rank 28 → 5), R117 (11 → 6), R200 (17 → 8). Of the 23 single-page questions flagged multi, three move
down a little inside the top 10 under B (R028 4 → 9, R105 2 → 4, R181 2 → 5); none falls out. C loses R028 (4 → 13).

## Why A changes nothing

Reranking the union against the original question puts back what the sub-queries found apart: the reranker
prefers pages relevant to the *whole* question, usually the latest document. For R062 ("APAR consolidated PAT growth
FY2019-20 to FY2025-26") the FY2019-20 page the sub-query found at the top sits at rank 30 against the original.
Coverage needs a slot per sub-query, which is what round-robin gives.

## What's left, and an answer-key limit

Six multi-page questions still miss a page under B (R064, R115, R118, R159, R160, R182). In most of them the
sub-query *did* find a page with the fact — in the fact's own year's filing — but the answer key names a different
page: the same figure printed as the comparative column of a later filing. Example: R115's "standalone PAT
FY2023-24" is keyed to the FY2024-25 annual report p.122, while the sub-query's top result is the FY2023-24 annual
report's own results table (p.68). These pages look right from the parser text but are **not counted**: the frozen
answer key is only changed from page images, and not to favour one method. The fresh question set will list, for
each fact of a multi-page question, every page that prints it, so coverage is scored per fact.

## Decision

Adopt B provisionally: it is the only merge that raises R@10 without losing a question, and the cost is one
Sonnet 5.5 call per question plus extra searches for the ~1 in 6 questions it expands. Latency was not measured
(one extra LLM call before retrieval). Confirm on the fresh question set.
