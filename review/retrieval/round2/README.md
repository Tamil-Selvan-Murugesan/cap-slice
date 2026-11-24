# Round 2 — chunking (2026-11-24)

**Winner: b2, a context header on every chunk (company · document · period · standalone/consolidated) with the heading path.**
Strict R@10 **0.805 → 0.865** with question-based soft filters (+13 / −1 questions, sign test p = 0.002),
R@1 0.40 → 0.51, MRR@10 0.535 → 0.642. It improves every filter setup (no filter 0.675 → 0.830) and no group
of ≥ 15 questions drops. c, d and e do not pass the decision rule; the combination run (f) is therefore b2 alone.

Full tables: [`results.md`](results.md) (made by `tools/round2/report.py`). Every run, its metadata and score
files are in this folder (`dense-voyage-4-large-2048__r2-<variant>-<filter>.*`), compared against the round-1
runs in `review/retrieval/`.

## Setup

Held fixed: MinerU advanced pages, Voyage 4 Large at 2048 dims, Qdrant server (HNSW m 16, ef_construct 128,
hnsw_ef 128), the same 200 frozen questions and the same question vectors as round 1 (re-running round 1 with the
changed runner gives +0 / −0). Only the chunk corpus changes. Every variant keeps the baseline chunk **text that
is returned** unchanged except d; it changes only what is **embedded** (`embed_text`).

| Variant | What is embedded | Records | Embedded tokens |
|---|---|---|---|
| a | baseline chunk (`chunker-baseline-2026-10-18`) | 40,593 | — (round 1) |
| b1 | `Company · Annual report FY2023-24` header + chunk | 40,593 | 11.1M |
| b2 | b1 header + `· Standalone/Consolidated financial statements` (annual reports and results only) + heading path `top heading › section` in place of the section line | 40,593 | 11.2M |
| c | table chunks: caption, column names and row labels only (no values); other chunks as a | 40,593 | 7.4M |
| d | concalls: opening remarks, then one moderator hand-over → question → answers per chunk (≤ 500 words); decks: one slide per chunk | 38,197 | 10.4M |
| e | small-to-big: ~150-word pieces (tables: caption + header + 5 rows) embedded, the parent baseline chunk returned once at its best piece | 64,257 pieces → 40,593 parents | 11.7M |

Code: `src/cap_slice/chunk_variants.py` (`cap-slice-chunk-variants build|sample`), context fields in
`structured_chunk.py` (heading level, top-level heading, statement scope — the baseline rebuild is byte-identical),
`retrieval_dense.py --corpus <variant>`, runner `tools/round2/run_variant.sh`. ~52M Voyage tokens in total.

## Results (question-based, soft — the production setup)

| Variant | R@1 | R@5 | R@10 | R@20 | MRR@10 | lenient R@10 | wins / losses vs a | passes |
|---|---|---|---|---|---|---|---|---|
| a | 0.400 | 0.730 | 0.805 | 0.865 | 0.535 | 0.830 | — | — |
| b1 | 0.515 | 0.825 | 0.860 | 0.915 | 0.641 | 0.875 | +13 / −2 (p 0.01) | yes |
| **b2** | 0.510 | 0.820 | **0.865** | 0.910 | **0.642** | **0.880** | **+13 / −1 (p 0.002)** | **yes** |
| c | 0.390 | 0.660 | 0.750 | 0.830 | 0.506 | 0.775 | +1 / −12 | no (tables −0.13, decks −0.11) |
| d | 0.375 | 0.710 | 0.790 | 0.865 | 0.521 | 0.810 | +3 / −6 | no (concall evidence −0.12) |
| e | 0.390 | 0.720 | 0.800 | 0.870 | 0.533 | 0.825 | +4 / −5 | no (R@10 not up) |

Across filter setups (strict R@10):

| Setup | a | b1 | b2 |
|---|---|---|---|
| none | 0.675 | 0.835 | 0.830 |
| company (soft) | 0.695 | 0.835 | 0.830 |
| question (hard) | 0.775 | 0.850 | 0.855 |
| question, soft | 0.805 | 0.860 | 0.865 |
| answer key, soft (ceiling) | 0.860 | 0.905 | 0.910 |

Groups where b2 moves most: standalone vs consolidated 0.68 → 0.86 (22 q), statements 0.80 → 0.92, concall
transcripts 0.79 → 0.89, vague questions 0.85 → 0.95, spoken numbers 0.75 → 0.88, cross-document 0.24 → 0.41,
multi-page / analytical 0.13 → 0.33 (still the weakest), Hero MotoCorp 0.76 → 0.85.

## Reading the results

- **The header carries what the chunk text lacks.** Most round-1 misses were look-alike pages in the right
  company's other years or the other statement set (see the briefing, "Why we miss"). The header puts company, year
  and scope into the vector itself, so the right year's page wins even with no filter (+34 / −2 unfiltered). The
  filters then add less: the gap between no filter and question-based soft shrinks from 0.13 to 0.035.
- **b2 vs b1** is +1 question (Hero's standalone/consolidated and cross-document questions); within noise, but b2 is
  never worse on a group of ≥ 15 and its one loss (R088, Hero investment in Ather, rank 9 → 26) is a single table.
  b2 also gives the answer step the heading path and scope for free.
- **c (table descriptors) loses tables.** Embedding a table's labels without its numbers drops questions whose
  wording matches the values ("₹ 3,915 crore", years in cells). The numbers are part of what makes a table
  findable; a descriptor would have to be added to the table, not replace it.
- **d (exchanges and slides) loses concall questions** that the baseline had at rank 1–2 (R048, R150, R151, R152).
  The exchange chunks are larger (often 400–525 words spanning several pages) and a single answer is diluted by the
  rest of the exchange. Caveat, found after the run: when a long exchange is split, every part keeps the page range
  of the whole exchange (e.g. Jan-2026-a parts all "p2–6"). That makes d's page hits *easier*, not harder, so d's
  real score is at most what is shown — the conclusion does not change. Slides alone did not move the deck group
  (0.81 → 0.79).
- **e (small-to-big) is neutral**: +4 / −5. Smaller pieces bring a few answers into the top 10 (R028, R063, R071, R122) and push
  some rank-1–3 answers out (R040, R155: 1 → 13, R198) — a 150-word piece carries less of the context that matched.

## Fairness checks

- Golden facts v1–v3 at L4 on the text each variant **returns** (`tools/round2/golden_guard.py`): b2, c, e unchanged
  (28 / 134 / 101); d −1 v2 (V126, C2C Aug-2026 p.34: "nine levels of approval" — in d the answer and the question
  it answers fall in different parts of a split exchange) and +1 v3 (W060).
- Pages covered by the top 10 (production setup): a 11.0, b1 9.7, b2 9.6, c 11.3, d 13.9, e 11.0. b2 wins while
  returning *fewer* pages, so the gain is not from wider chunks.
- No tuning on the test set: variants were specified before the run (plan of 2026-11-24); two rule bugs (b2's scope
  label leaking onto non-statement pages; d starting an exchange at any "Moderator" turn) were found by reading
  samples and fixed before any embedding.

## Backups

Each variant's vectors (float32 shards, manifest with corpus sha256, log, question vectors) and its chunk file are in
R2 at `tamil/cap-slice/vectors/voyage-4-large-2048__r2-<variant>/` (b1 422 MB, b2 423 MB, c 413 MB, d 399 MB,
e 668 MB), verified with `rclone check`. Restore: copy back, then `cap-slice-retrieval-dense load --corpus <variant>`.
Local copies and Qdrant collections were removed after scoring.

## Next

Adopt b2 as the chunker baseline for rounds 3–5 (tag `chunker-r2-b2-2026-11-24`). Multi-page and analytical
questions (5 of 15) stay the weak spot: candidates for later are a reranker (round 4) and returning neighbouring
chunks, not more chunk shapes. The concall speaker-table defect (S22) is still in the baseline chunker; d's
parsing of turns can be reused to fix it without changing chunk boundaries.
