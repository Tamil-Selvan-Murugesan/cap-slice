# Retrieval runs

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
