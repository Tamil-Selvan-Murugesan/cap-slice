# Fresh question set: production vs query expansion (2026-11-25)

**Result: round-robin query expansion (B) confirmed on unseen questions.** On 50 new questions
(`data/golden/fresh_questions.csv`, every page per fact checked on the page image), B finds **13 of 14**
multi-page questions with all facts in the top 10 (production 11). Strict R@10 goes **0.90 → 0.94** (+2 / −0) and
R@5 0.80 → 0.94; R@1 is unchanged. Nothing was tuned here: same prompt (hash `05b1e0cac1d0`), same pipeline, same
merges, all fixed before the set was written.

Pooled with the 200 questions, B is **+5 / −0** (sign test p = 0.06). That is still not significant at 0.05, but
there are no losses on 250 questions and it is consistent across both sets.

## Results (strict; scorer `cap-slice-retrieval-score --set fresh`)

| Setup | R@1 | R@5 | R@10 | MRR@10 | multi-page (14) | chart (14) | kpi (4) | concall (8) | others (10) |
|---|---|---|---|---|---|---|---|---|---|
| dense top 100 (b2s, question-based soft filter), no rerank | 0.38 | 0.66 | 0.74 | 0.50 | 0.64 | 0.57 | 0.75 | 0.88 | 1.00 |
| production (+ rerank-3 top 50) | 0.56 | 0.80 | 0.90 | 0.68 | 0.79 | 0.86 | 1.00 | 1.00 | 1.00 |
| **B: query expansion, round-robin** | 0.56 | **0.94** | **0.94** | **0.72** | **0.93** | 0.86 | 1.00 | 1.00 | 1.00 |
| C: query expansion, RRF | 0.56 | 0.86 | 0.92 | 0.69 | 0.86 | 0.86 | 1.00 | 1.00 | 1.00 |

"Others" are prose 4, statement 3, table 2 and scan 1. The 200-question production scores were R@10 0.915,
R@1 0.62, so the fresh set is a little harder but tells the same story.

**Multi-page ranks** (the rank where the last fact appears), production → B:

- F019 7 → 3, F021 3 → 2, F022 13 → 3, F023 7 → 2, F024 5 → 3, F026 7 → 4, F027 8 → 2, F028 6 → 3, F029 3 → 4.
- F030 missed → 2.
- F031 missed in both.
- F020, F025 and F032 are at 2 in both.

So expansion mostly moves the second fact up rather than rescuing it from outside the list.

**Planner** (Sonnet 5.5): 15 of 50 flagged multi, with 30 sub-queries. It caught all 14 multi-page questions. The
fifteenth, F012, asks for a figure and the change from the year before; both are printed on one page, and the
plan did no harm there. Cost: 36K input + 4.6K output tokens; reranking used 0.96M (main) + 0.50M (sub-query)
rerank-3 tokens.

## The three misses

- **F015** (APAR premium conductor volume FY2022, a bar chart label): **parse miss.** No chunk covering
  Aug-2023-a p97 contains 31,477; MinerU kept the slide's text and dropped the chart's value labels. Retrieval
  can't fix this; it is a case for the image round (picture descriptions).
- **F016** (APAR exports FY20, a stacked bar chart): **ranking miss.** MinerU did turn the chart into a table, so
  the value is in a chunk ("Exports contribution at 41% in FY21 | Exports | Domestic | FY17 …"). But those slides
  break into nine small chart chunks and none of them reaches the top 50 for the question.
- **F031** (exports FY20 + overseas share from a call): fails on its F016 fact. The call fact is found.

## Files

- `dense-b2s-question-soft-top100*.jsonl`: production dense search, then rerank-3 top 50.
- `plans.jsonl`, `subqueries.csv`: Sonnet 5.5 plans for the fresh questions (committed, since the model is not
  deterministic).
- `dense-b2s-subqueries-*`: the sub-query runs.
- `expand-{B-roundrobin,C-rrf,A-union-candidates}.jsonl`: merged runs. A, the union reranked against the original,
  was not rerun; on the 200 questions it changed nothing.
- `*.score.{json,md}`: scores; B's file includes the paired comparison against production.

Reproduce (keys from `~/.config/cap-slice/{voyage,llm}.env`; plans are cached, so `plan` makes no calls):

```bash
uv run cap-slice-retrieval-dense search --corpus b2s --filter question --soft --top 100 \
  --questions data/golden/fresh_questions.csv --out review/retrieval/fresh/dense-b2s-question-soft-top100.jsonl
uv run cap-slice-retrieval-rerank review/retrieval/fresh/dense-b2s-question-soft-top100.jsonl --depth 50 --corpus b2s \
  --questions data/golden/fresh_questions.csv --out-dir review/retrieval/fresh
Q="--questions data/golden/fresh_questions.csv --out-dir review/retrieval/fresh"
uv run cap-slice-query-expand $Q plan && uv run cap-slice-query-expand $Q questions
#   ... dense search + rerank of review/retrieval/fresh/subqueries.csv the same way ...
uv run cap-slice-query-expand $Q merge --production review/retrieval/fresh/dense-b2s-question-soft-top100-rerank-rerank-3-d50.jsonl
uv run cap-slice-retrieval-score --set fresh review/retrieval/fresh/expand-B-roundrobin.jsonl \
  --compare review/retrieval/fresh/dense-b2s-question-soft-top100-rerank-rerank-3-d50.jsonl
```
