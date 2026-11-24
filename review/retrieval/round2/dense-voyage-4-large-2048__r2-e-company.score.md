# Retrieval score: `dense-voyage-4-large-2048__r2-e-company.jsonl`

200 questions; missing from run: 0. Strict = answer pages checked on the image; lenient adds machine-found pages that print the answer's numbers. doc@10 = the right document anywhere in the top 10.

| group | n | strict_R@1 | strict_R@5 | strict_R@10 | strict_R@20 | strict_MRR@10 | lenient_R@10 | doc@10 |
|---|---|---|---|---|---|---|---|---|
| all | 200 | 0.31 | 0.59 | 0.71 | 0.80 | 0.44 | 0.74 | 0.91 |
| company:APARINDS | 64 | 0.25 | 0.58 | 0.69 | 0.78 | 0.39 | 0.73 | 0.86 |
| company:HEROMOTOCO | 54 | 0.33 | 0.59 | 0.69 | 0.74 | 0.45 | 0.72 | 0.96 |
| company:E2E | 43 | 0.26 | 0.53 | 0.74 | 0.84 | 0.38 | 0.77 | 0.93 |
| company:ESCONET | 21 | 0.43 | 0.57 | 0.67 | 0.81 | 0.50 | 0.71 | 0.81 |
| company:C2C | 18 | 0.44 | 0.78 | 0.83 | 0.94 | 0.59 | 0.83 | 1.00 |
| doctype:annual_reports | 111 | 0.32 | 0.62 | 0.72 | 0.79 | 0.45 | 0.77 | 0.95 |
| doctype:investor_presentations | 47 | 0.23 | 0.43 | 0.68 | 0.83 | 0.33 | 0.72 | 0.81 |
| doctype:concall_transcripts | 38 | 0.34 | 0.66 | 0.68 | 0.76 | 0.47 | 0.68 | 0.89 |
| doctype:periodic_results | 4 | 0.75 | 1.00 | 1.00 | 1.00 | 0.88 | 1.00 | 1.00 |
| evidence:table | 63 | 0.37 | 0.62 | 0.81 | 0.92 | 0.50 | 0.87 | 0.94 |
| evidence:concall | 33 | 0.39 | 0.76 | 0.79 | 0.79 | 0.55 | 0.79 | 0.91 |
| evidence:prose | 33 | 0.18 | 0.55 | 0.58 | 0.73 | 0.32 | 0.61 | 0.91 |
| evidence:statement | 25 | 0.32 | 0.60 | 0.72 | 0.76 | 0.46 | 0.76 | 0.88 |
| evidence:chart | 15 | 0.33 | 0.60 | 0.80 | 0.80 | 0.44 | 0.87 | 0.93 |
| evidence:multi | 15 | 0.00 | 0.07 | 0.13 | 0.47 | 0.03 | 0.13 | 0.80 |
| evidence:scan | 10 | 0.50 | 0.70 | 0.90 | 0.90 | 0.63 | 0.90 | 1.00 |
| evidence:kpi | 6 | 0.33 | 0.67 | 0.83 | 0.83 | 0.42 | 0.83 | 0.83 |
| hard:decoy_years | 63 | 0.32 | 0.63 | 0.83 | 0.87 | 0.48 | 0.86 | 0.95 |
| hard:standalone_vs_consolidated | 22 | 0.18 | 0.45 | 0.59 | 0.68 | 0.34 | 0.64 | 0.91 |
| hard:cross_doc | 17 | 0.06 | 0.18 | 0.29 | 0.59 | 0.11 | 0.29 | 0.88 |
| hard:spoken_numbers | 16 | 0.31 | 0.62 | 0.62 | 0.62 | 0.42 | 0.62 | 0.81 |
| hard:chart_labels | 14 | 0.29 | 0.57 | 0.79 | 0.79 | 0.40 | 0.86 | 0.93 |
| hard:indian_grouping | 14 | 0.36 | 0.71 | 0.79 | 0.93 | 0.51 | 0.93 | 0.86 |
| hard:multi_hop | 14 | 0.00 | 0.07 | 0.14 | 0.43 | 0.03 | 0.14 | 0.86 |
| hard:slide_table | 13 | 0.31 | 0.38 | 0.54 | 0.77 | 0.37 | 0.62 | 0.77 |
| hard:lakhs_unit | 11 | 0.55 | 0.82 | 0.91 | 0.91 | 0.67 | 0.91 | 0.91 |
| hard:footnote | 10 | 0.10 | 0.50 | 0.80 | 0.80 | 0.25 | 0.80 | 0.90 |
| hard:image_only_page | 10 | 0.50 | 0.70 | 0.90 | 0.90 | 0.63 | 0.90 | 1.00 |
| hard:no_numbers | 10 | 0.30 | 0.70 | 0.80 | 0.80 | 0.50 | 0.80 | 1.00 |
| hard:period_format | 10 | 0.40 | 0.50 | 0.60 | 0.60 | 0.44 | 0.60 | 0.70 |
| style:paraphrase | 140 | 0.33 | 0.63 | 0.77 | 0.84 | 0.46 | 0.81 | 0.90 |
| style:exact | 25 | 0.36 | 0.64 | 0.72 | 0.80 | 0.50 | 0.76 | 0.96 |
| style:vague | 20 | 0.35 | 0.65 | 0.70 | 0.80 | 0.47 | 0.70 | 1.00 |
| style:analytical | 15 | 0.00 | 0.07 | 0.13 | 0.47 | 0.03 | 0.13 | 0.80 |

## Paired comparison vs `dense-voyage-4-large-2048-company.jsonl` (strict Recall@10)

Only this run finds: 16 (R006, R028, R042, R053, R066, R069, R078, R086, R087, R090, R099, R130, R137, R146, R164, R166)  
Only the other finds: 8 (R026, R034, R040, R058, R067, R121, R155, R198)  
Ties: 176; exact sign test p = 0.152

## Not found in the top 10 (strict): 58

R004, R009, R010, R013, R021, R022, R023, R025, R026, R029, R034, R038, R040, R050, R055, R058, R061, R062, R063, R064, R067, R068, R071, R073, R075, R076, R079, R083, R088, R097, R098, R105, R107, R115, R116, R117, R118, R121, R122, R127, R135, R136, R144, R145, R155, R156, R159, R161, R163, R170, R171, R172, R173, R179, R181, R198, R199, R200
