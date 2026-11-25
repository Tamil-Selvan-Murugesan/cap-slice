# S22 fix — concall speaker tables (2026-11-25)

**Adopted.** MinerU renders about half the concall transcripts as two-column speaker tables (`| Name: | speech |`)
and marks some speaker labels as headings (`## Name:`). The chunker treated them as tables: every part repeated the
first turn as its "header" and the section was a stale speaker name. `chunk_structured(pages, transcript=True)`
now turns those rows and headings back into plain turns (`Name: speech`) for concall transcripts only; everything
else is unchanged (checked: all non-concall chunks identical).

| Concall chunks | Before | After |
|---|---|---|
| chunks | 3,428 | 2,523 |
| parsed as tables | 1,085 | 4 |
| section = a speaker label | 2,519 | 0 |
| chunks sharing an identical opening | 193 | 6 |
| median words | 311 | 412 |

Corpus `r2-b2s` = b2 on the fixed chunker (`cap-slice-chunk-variants build b2s`). Re-embedding reused the vectors of
the 37,474 unchanged chunks (`cap-slice-retrieval-dense embed --reuse`) and embedded only 2,214 new ones
(1.24M Voyage tokens). Golden facts v1–v3 L4 unchanged (28 / 134 / 101). Vectors in R2 at
`tamil/cap-slice/vectors/voyage-4-large-2048__r2-b2s/`.

## Results (production setup: question-based soft filter → rerank-3 top 50)

| | R@1 | R@10 | MRR@10 |
|---|---|---|---|
| b2 + rerank (round 4) | 0.605 | 0.915 | 0.722 |
| **b2s + rerank** | **0.620** | 0.915 | **0.730** |
| concall transcripts (38 q) | 0.711 → **0.763** | 0.974 → 0.974 | 0.811 → **0.842** |
| concall evidence (33 q) | 0.818 → **0.879** | 1.00 → 1.00 | 0.894 → 0.934 |
| spoken numbers (16 q) | 0.75 → **0.875** | 1.00 → 1.00 | 0.854 → 0.927 |

R@10 doesn't change (+0 / −0 in every setup, with and without reranking); the right concall page moves up
(R056, R057, R132, R153: 2 → 1). Dense alone, before reranking: R@10 0.86 / 0.83 (no filter), identical to b2.
