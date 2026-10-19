# Retrieval score: `hybrid-dbsf-question_next.jsonl`

200 questions; missing from run: 0. Strict = answer pages checked on the image; lenient adds machine-found pages that print the answer's numbers. doc@10 = the right document anywhere in the top 10.

| group | n | strict_R@1 | strict_R@5 | strict_R@10 | strict_R@20 | strict_MRR@10 | lenient_R@10 | doc@10 |
|---|---|---|---|---|---|---|---|---|
| all | 200 | 0.31 | 0.59 | 0.70 | 0.81 | 0.44 | 0.76 | 0.93 |
| company:APARINDS | 64 | 0.36 | 0.69 | 0.81 | 0.94 | 0.52 | 0.83 | 0.91 |
| company:HEROMOTOCO | 54 | 0.31 | 0.57 | 0.63 | 0.72 | 0.43 | 0.70 | 0.93 |
| company:E2E | 43 | 0.21 | 0.44 | 0.60 | 0.72 | 0.31 | 0.67 | 0.93 |
| company:ESCONET | 21 | 0.19 | 0.48 | 0.62 | 0.71 | 0.32 | 0.71 | 0.90 |
| company:C2C | 18 | 0.50 | 0.78 | 0.89 | 0.89 | 0.64 | 0.89 | 1.00 |
| doctype:annual_reports | 111 | 0.32 | 0.60 | 0.68 | 0.80 | 0.45 | 0.77 | 0.95 |
| doctype:investor_presentations | 47 | 0.28 | 0.57 | 0.72 | 0.81 | 0.42 | 0.74 | 0.89 |
| doctype:concall_transcripts | 38 | 0.32 | 0.53 | 0.71 | 0.79 | 0.44 | 0.71 | 0.89 |
| doctype:periodic_results | 4 | 0.25 | 1.00 | 1.00 | 1.00 | 0.52 | 1.00 | 1.00 |
| evidence:table | 63 | 0.30 | 0.62 | 0.78 | 0.90 | 0.45 | 0.90 | 0.97 |
| evidence:concall | 33 | 0.36 | 0.58 | 0.76 | 0.82 | 0.49 | 0.76 | 0.91 |
| evidence:prose | 33 | 0.33 | 0.64 | 0.73 | 0.76 | 0.45 | 0.73 | 0.94 |
| evidence:statement | 25 | 0.28 | 0.60 | 0.64 | 0.84 | 0.41 | 0.68 | 0.92 |
| evidence:chart | 15 | 0.33 | 0.73 | 0.80 | 0.80 | 0.51 | 0.87 | 0.93 |
| evidence:multi | 15 | 0.00 | 0.13 | 0.27 | 0.47 | 0.08 | 0.27 | 0.93 |
| evidence:scan | 10 | 0.60 | 0.70 | 0.70 | 0.80 | 0.63 | 0.70 | 0.80 |
| evidence:kpi | 6 | 0.33 | 0.67 | 0.67 | 0.67 | 0.50 | 0.67 | 0.67 |
| hard:decoy_years | 63 | 0.30 | 0.59 | 0.68 | 0.84 | 0.43 | 0.79 | 0.90 |
| hard:standalone_vs_consolidated | 22 | 0.36 | 0.45 | 0.50 | 0.77 | 0.41 | 0.64 | 0.95 |
| hard:cross_doc | 17 | 0.00 | 0.18 | 0.35 | 0.59 | 0.10 | 0.35 | 0.94 |
| hard:spoken_numbers | 16 | 0.25 | 0.44 | 0.62 | 0.69 | 0.36 | 0.62 | 0.81 |
| hard:chart_labels | 14 | 0.29 | 0.71 | 0.79 | 0.79 | 0.47 | 0.86 | 0.93 |
| hard:indian_grouping | 14 | 0.07 | 0.57 | 0.86 | 0.93 | 0.30 | 0.93 | 1.00 |
| hard:multi_hop | 14 | 0.00 | 0.07 | 0.21 | 0.43 | 0.05 | 0.21 | 0.93 |
| hard:slide_table | 13 | 0.31 | 0.46 | 0.69 | 0.85 | 0.40 | 0.77 | 0.92 |
| hard:lakhs_unit | 11 | 0.27 | 0.91 | 0.91 | 0.91 | 0.50 | 0.91 | 0.91 |
| hard:footnote | 10 | 0.20 | 0.70 | 0.80 | 0.90 | 0.41 | 0.80 | 1.00 |
| hard:image_only_page | 10 | 0.60 | 0.70 | 0.70 | 0.80 | 0.63 | 0.70 | 0.80 |
| hard:no_numbers | 10 | 0.40 | 0.50 | 0.80 | 0.80 | 0.50 | 0.80 | 1.00 |
| hard:period_format | 10 | 0.10 | 0.50 | 0.70 | 0.80 | 0.28 | 0.70 | 0.90 |
| style:paraphrase | 140 | 0.33 | 0.64 | 0.75 | 0.82 | 0.47 | 0.81 | 0.92 |
| style:exact | 25 | 0.32 | 0.68 | 0.72 | 0.92 | 0.46 | 0.80 | 0.92 |
| style:vague | 20 | 0.40 | 0.45 | 0.70 | 0.80 | 0.46 | 0.70 | 0.95 |
| style:analytical | 15 | 0.00 | 0.13 | 0.27 | 0.47 | 0.08 | 0.27 | 0.93 |

## Paired comparison vs `dense-question_next.jsonl` (strict Recall@10)

Only this run finds: 8 (R004, R021, R022, R098, R107, R161, R171, R181)  
Only the other finds: 15 (R010, R055, R075, R120, R125, R137, R142, R143, R150, R151, R152, R155, R158, R166, R177)  
Ties: 177; exact sign test p = 0.210

## Not found in the top 10 (strict): 59

R010, R013, R023, R028, R029, R040, R050, R055, R061, R062, R063, R064, R066, R068, R069, R071, R073, R075, R076, R078, R079, R083, R086, R087, R088, R090, R099, R105, R115, R116, R117, R118, R120, R122, R125, R127, R136, R137, R142, R143, R144, R145, R150, R151, R152, R155, R156, R158, R159, R163, R166, R170, R172, R173, R177, R179, R182, R199, R200
