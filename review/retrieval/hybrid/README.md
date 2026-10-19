# Hybrid search: BM25 + Voyage 4 Large (2026-10-19)

Round 4 of `docs/plan.md` (hybrid search), run early on the round-1 setup to see whether keyword search
adds anything to dense search. `cap-slice-retrieval-hybrid` fuses a BM25 run and a dense run made with
the **same filter setup**, each 100 deep (`inputs/`), and keeps the fused top 50. Two standard fusions,
parameters fixed before the run (not tuned on the question set): **RRF** (k = 60, ranks only) and
**DBSF** (each list's scores scaled to 0–1 between mean ± 3 sd, then summed). Same 40,593 chunks,
Voyage 4 Large 2048-d cosine on the Qdrant server, BM25 as in the keyword baseline.

## Strict R@10 (200 questions)

| Filter | BM25 | Voyage (dense) | Hybrid RRF | Hybrid DBSF | DBSF vs dense |
|---|---|---|---|---|---|
| none | 0.41 | **0.68** | 0.59 | 0.57 | +5 / −25 |
| company, hard | 0.47 | **0.67** | 0.60 | 0.61 | +9 / −20 |
| company, soft | 0.47 | **0.69** | 0.63 | 0.65 | +10 / −20 |
| question-based, hard | 0.66 | **0.78** | 0.73 | 0.76 | +8 / −11 |
| question-based, soft | 0.65 | **0.81** | 0.74 | 0.77 | +7 / −15 |
| question-based + next year, hard | 0.61 | **0.74** | 0.69 | 0.70 | +8 / −15 |
| question-based + next year, soft | 0.61 | **0.78** | 0.72 | 0.73 | +8 / −16 |
| answer key, hard (*upper bound*) | 0.73 | 0.83 | 0.81 | **0.84** | +8 / −7 |
| answer key, soft (*upper bound*) | 0.72 | **0.86** | 0.81 | 0.83 | +4 / −9 |

Full metrics: `hybrid-<rrf|dbsf>-<filter>.score.md`. RRF vs dense, question-based soft: +6 / −18 (p = 0.02).

## Where it helps and where it hurts (question-based soft, strict R@10)

| Group | n | BM25 | Dense | DBSF |
|---|---|---|---|---|
| prose | 33 | 0.73 | 0.79 | **0.85** |
| exact wording | 25 | 0.80 | 0.84 | **0.88** |
| multi-page | 15 | 0.13 | 0.13 | **0.20** |
| analytical | 15 | 0.13 | 0.13 | **0.20** |
| tables | 63 | 0.78 | **0.94** | 0.89 |
| concall | 33 | 0.61 | **0.88** | 0.79 |
| statements | 25 | 0.56 | **0.80** | 0.76 |
| charts | 15 | 0.67 | **0.80** | 0.73 |
| scanned pages | 10 | 0.50 | **0.80** | 0.60 |

**As a candidate pool for a reranker**, BM25 adds nothing either: an answer page is among dense top-50 +
BM25 top-50 for 182 / 186 questions (no filter / question-based soft) — the same as dense top-100 alone
(183 / 186).

## Verdict

Not adopted. Equal-weight fusion with a retriever this much weaker pulls wrong chunks into the top 10:
hybrid loses overall in every production setup, and tables, concall and scanned pages drop by more than one
question in ten — it fails both parts of the decision rule. Keyword search helps where the question uses
the document's own words (prose, exact wording) and slightly on comparisons. Not tried, because they need
data we don't have: weights or routing tuned on a separate development question set (tuning them on these
200 would overfit), and a BM25 tokenizer tuned for numbers and identifiers. Dense-only stays the setup for
the next rounds; revisit hybrid with the reranker and with the open model (round 5).

The dense inputs here are 100 deep; where their top 50 differs from the committed 50-deep runs (48 of 200
questions with no filter) it is one chunk at rank 50 swapped with another of identical score (repeated
boilerplate) — R@10 and R@50 are unchanged.

Reproduce:

```bash
I=review/retrieval/hybrid/inputs
uv run cap-slice-retrieval-bm25 --parser mineru --cache parsed_advanced --top 100 --filter question --soft --out $I/bm25-question-soft.jsonl
uv run cap-slice-retrieval-dense search --top 100 --filter question --soft --out $I/dense-question-soft.jsonl
uv run cap-slice-retrieval-hybrid $I/bm25-question-soft.jsonl $I/dense-question-soft.jsonl --method dbsf --out review/retrieval/hybrid/hybrid-dbsf-question-soft.jsonl
uv run cap-slice-retrieval-score review/retrieval/hybrid/hybrid-dbsf-question-soft.jsonl --compare $I/dense-question-soft.jsonl
```
