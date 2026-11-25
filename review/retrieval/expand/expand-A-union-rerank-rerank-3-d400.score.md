# Retrieval score: `expand-A-union-rerank-rerank-3-d400.jsonl`

200 questions; missing from run: 0. Strict = answer pages checked on the image; lenient adds machine-found pages that print the answer's numbers. doc@10 = the right document anywhere in the top 10.

| group | n | strict_R@1 | strict_R@5 | strict_R@10 | strict_R@20 | strict_MRR@10 | lenient_R@10 | doc@10 |
|---|---|---|---|---|---|---|---|---|
| all | 200 | 0.62 | 0.86 | 0.92 | 0.94 | 0.73 | 0.92 | 0.98 |
| company:APARINDS | 64 | 0.66 | 0.91 | 0.92 | 0.94 | 0.77 | 0.92 | 0.97 |
| company:HEROMOTOCO | 54 | 0.59 | 0.80 | 0.89 | 0.93 | 0.69 | 0.91 | 0.98 |
| company:E2E | 43 | 0.63 | 0.91 | 0.93 | 0.95 | 0.73 | 0.93 | 1.00 |
| company:ESCONET | 21 | 0.48 | 0.81 | 0.90 | 0.90 | 0.64 | 0.90 | 1.00 |
| company:C2C | 18 | 0.72 | 0.89 | 0.94 | 1.00 | 0.80 | 0.94 | 1.00 |
| doctype:annual_reports | 111 | 0.52 | 0.84 | 0.90 | 0.94 | 0.67 | 0.91 | 0.99 |
| doctype:investor_presentations | 47 | 0.72 | 0.85 | 0.89 | 0.89 | 0.78 | 0.89 | 0.96 |
| doctype:concall_transcripts | 38 | 0.76 | 0.95 | 0.97 | 1.00 | 0.84 | 0.97 | 1.00 |
| doctype:periodic_results | 4 | 0.75 | 1.00 | 1.00 | 1.00 | 0.81 | 1.00 | 1.00 |
| evidence:table | 63 | 0.71 | 0.98 | 1.00 | 1.00 | 0.83 | 1.00 | 1.00 |
| evidence:concall | 33 | 0.88 | 1.00 | 1.00 | 1.00 | 0.93 | 1.00 | 1.00 |
| evidence:prose | 33 | 0.33 | 0.79 | 0.94 | 1.00 | 0.54 | 0.94 | 1.00 |
| evidence:statement | 25 | 0.64 | 0.92 | 0.96 | 0.96 | 0.77 | 0.96 | 0.96 |
| evidence:chart | 15 | 0.67 | 0.80 | 0.80 | 0.80 | 0.71 | 0.87 | 0.93 |
| evidence:multi | 15 | 0.00 | 0.27 | 0.40 | 0.53 | 0.12 | 0.40 | 1.00 |
| evidence:scan | 10 | 0.90 | 0.90 | 0.90 | 1.00 | 0.90 | 0.90 | 1.00 |
| evidence:kpi | 6 | 0.67 | 0.67 | 0.83 | 0.83 | 0.69 | 0.83 | 0.83 |
| hard:decoy_years | 63 | 0.65 | 0.92 | 0.94 | 0.94 | 0.77 | 0.95 | 0.97 |
| hard:standalone_vs_consolidated | 22 | 0.55 | 0.82 | 0.91 | 0.91 | 0.69 | 0.91 | 1.00 |
| hard:cross_doc | 17 | 0.06 | 0.41 | 0.53 | 0.65 | 0.22 | 0.53 | 1.00 |
| hard:spoken_numbers | 16 | 0.88 | 1.00 | 1.00 | 1.00 | 0.93 | 1.00 | 1.00 |
| hard:chart_labels | 14 | 0.64 | 0.79 | 0.79 | 0.79 | 0.69 | 0.86 | 0.93 |
| hard:indian_grouping | 14 | 0.64 | 0.93 | 1.00 | 1.00 | 0.76 | 1.00 | 1.00 |
| hard:multi_hop | 14 | 0.00 | 0.21 | 0.36 | 0.50 | 0.09 | 0.36 | 1.00 |
| hard:slide_table | 13 | 0.92 | 1.00 | 1.00 | 1.00 | 0.96 | 1.00 | 1.00 |
| hard:lakhs_unit | 11 | 0.73 | 1.00 | 1.00 | 1.00 | 0.80 | 1.00 | 1.00 |
| hard:footnote | 10 | 0.60 | 0.90 | 0.90 | 1.00 | 0.68 | 0.90 | 1.00 |
| hard:image_only_page | 10 | 0.90 | 0.90 | 0.90 | 1.00 | 0.90 | 0.90 | 1.00 |
| hard:no_numbers | 10 | 0.90 | 0.90 | 1.00 | 1.00 | 0.92 | 1.00 | 1.00 |
| hard:period_format | 10 | 0.80 | 0.80 | 0.90 | 0.90 | 0.82 | 0.90 | 0.90 |
| style:paraphrase | 140 | 0.71 | 0.91 | 0.96 | 0.96 | 0.80 | 0.96 | 0.98 |
| style:exact | 25 | 0.56 | 0.92 | 0.96 | 1.00 | 0.72 | 0.96 | 1.00 |
| style:vague | 20 | 0.55 | 0.90 | 0.95 | 1.00 | 0.72 | 0.95 | 1.00 |
| style:analytical | 15 | 0.00 | 0.27 | 0.40 | 0.53 | 0.12 | 0.40 | 1.00 |

## Paired comparison vs `dense-b2s-question-soft-top100-rerank-rerank-3-d50.jsonl` (strict Recall@10)

Only this run finds: 0 (-)  
Only the other finds: 0 (-)  
Ties: 200; exact sign test p = 1.000

## Not found in the top 10 (strict): 17

R023, R029, R061, R062, R064, R068, R076, R083, R115, R117, R118, R145, R159, R160, R172, R182, R200
