# Retrieval score: `dense-voyage-4-large-2048__r2-b1-exact.jsonl`

200 questions; missing from run: 0. Strict = answer pages checked on the image; lenient adds machine-found pages that print the answer's numbers. doc@10 = the right document anywhere in the top 10.

| group | n | strict_R@1 | strict_R@5 | strict_R@10 | strict_R@20 | strict_MRR@10 | lenient_R@10 | doc@10 |
|---|---|---|---|---|---|---|---|---|
| all | 200 | 0.46 | 0.77 | 0.83 | 0.91 | 0.59 | 0.85 | 0.96 |
| company:APARINDS | 64 | 0.39 | 0.77 | 0.83 | 0.88 | 0.55 | 0.86 | 0.92 |
| company:HEROMOTOCO | 54 | 0.41 | 0.74 | 0.80 | 0.89 | 0.54 | 0.83 | 0.98 |
| company:E2E | 43 | 0.40 | 0.74 | 0.86 | 0.93 | 0.53 | 0.86 | 1.00 |
| company:ESCONET | 21 | 0.57 | 0.81 | 0.86 | 0.90 | 0.67 | 0.86 | 0.95 |
| company:C2C | 18 | 0.83 | 0.89 | 0.89 | 1.00 | 0.86 | 0.89 | 1.00 |
| doctype:annual_reports | 111 | 0.48 | 0.76 | 0.81 | 0.89 | 0.60 | 0.85 | 0.97 |
| doctype:investor_presentations | 47 | 0.30 | 0.72 | 0.83 | 0.87 | 0.45 | 0.83 | 0.91 |
| doctype:concall_transcripts | 38 | 0.55 | 0.87 | 0.89 | 0.97 | 0.68 | 0.89 | 1.00 |
| doctype:periodic_results | 4 | 0.75 | 0.75 | 1.00 | 1.00 | 0.79 | 1.00 | 1.00 |
| evidence:table | 63 | 0.49 | 0.86 | 0.90 | 0.94 | 0.64 | 0.94 | 0.98 |
| evidence:concall | 33 | 0.64 | 0.97 | 0.97 | 0.97 | 0.77 | 0.97 | 1.00 |
| evidence:prose | 33 | 0.39 | 0.64 | 0.76 | 0.88 | 0.51 | 0.76 | 0.94 |
| evidence:statement | 25 | 0.48 | 0.88 | 0.92 | 1.00 | 0.63 | 0.96 | 1.00 |
| evidence:chart | 15 | 0.40 | 0.73 | 0.80 | 0.80 | 0.52 | 0.87 | 0.93 |
| evidence:multi | 15 | 0.07 | 0.13 | 0.27 | 0.67 | 0.12 | 0.27 | 0.93 |
| evidence:scan | 10 | 0.60 | 0.90 | 0.90 | 0.90 | 0.73 | 0.90 | 0.90 |
| evidence:kpi | 6 | 0.17 | 0.50 | 0.83 | 0.83 | 0.35 | 0.83 | 0.83 |
| hard:decoy_years | 63 | 0.49 | 0.81 | 0.87 | 0.94 | 0.63 | 0.92 | 0.98 |
| hard:standalone_vs_consolidated | 22 | 0.36 | 0.77 | 0.82 | 0.91 | 0.51 | 0.86 | 1.00 |
| hard:cross_doc | 17 | 0.06 | 0.29 | 0.41 | 0.76 | 0.18 | 0.41 | 0.94 |
| hard:spoken_numbers | 16 | 0.62 | 0.94 | 0.94 | 0.94 | 0.74 | 0.94 | 1.00 |
| hard:chart_labels | 14 | 0.36 | 0.71 | 0.79 | 0.79 | 0.49 | 0.86 | 0.93 |
| hard:indian_grouping | 14 | 0.43 | 0.71 | 0.86 | 0.93 | 0.54 | 0.93 | 0.93 |
| hard:multi_hop | 14 | 0.00 | 0.07 | 0.21 | 0.64 | 0.05 | 0.21 | 0.93 |
| hard:slide_table | 13 | 0.31 | 0.77 | 0.85 | 0.85 | 0.48 | 0.85 | 0.92 |
| hard:lakhs_unit | 11 | 0.64 | 0.82 | 0.91 | 1.00 | 0.74 | 0.91 | 1.00 |
| hard:footnote | 10 | 0.30 | 0.70 | 0.80 | 0.80 | 0.44 | 0.80 | 0.90 |
| hard:image_only_page | 10 | 0.60 | 0.90 | 0.90 | 0.90 | 0.73 | 0.90 | 0.90 |
| hard:no_numbers | 10 | 0.60 | 0.90 | 0.90 | 1.00 | 0.73 | 0.90 | 1.00 |
| hard:period_format | 10 | 0.30 | 0.80 | 0.80 | 0.80 | 0.48 | 0.80 | 0.90 |
| style:paraphrase | 140 | 0.49 | 0.84 | 0.89 | 0.92 | 0.63 | 0.90 | 0.96 |
| style:exact | 25 | 0.48 | 0.68 | 0.84 | 0.92 | 0.58 | 0.92 | 0.96 |
| style:vague | 20 | 0.50 | 0.85 | 0.90 | 0.95 | 0.66 | 0.90 | 1.00 |
| style:analytical | 15 | 0.07 | 0.13 | 0.27 | 0.67 | 0.12 | 0.27 | 0.93 |

## Paired comparison vs `dense-voyage-4-large-2048-exact.jsonl` (strict Recall@10)

Only this run finds: 34 (R001, R004, R009, R010, R025, R028, R042, R044, R050, R053, R055, R071, R073, R075, R078, R090, R105, R107, R122, R127, R135, R136, R137, R144, R146, R161, R163, R164, R165, R166, R170, R171, R181, R198)  
Only the other finds: 2 (R123, R160)  
Ties: 164; exact sign test p = 0.000

## Not found in the top 10 (strict): 33

R006, R013, R021, R022, R023, R029, R038, R061, R062, R063, R064, R068, R076, R079, R083, R088, R097, R098, R115, R116, R117, R118, R123, R130, R145, R156, R159, R160, R172, R173, R179, R199, R200
