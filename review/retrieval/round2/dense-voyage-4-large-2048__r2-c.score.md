# Retrieval score: `dense-voyage-4-large-2048__r2-c.jsonl`

200 questions; missing from run: 0. Strict = answer pages checked on the image; lenient adds machine-found pages that print the answer's numbers. doc@10 = the right document anywhere in the top 10.

| group | n | strict_R@1 | strict_R@5 | strict_R@10 | strict_R@20 | strict_MRR@10 | lenient_R@10 | doc@10 |
|---|---|---|---|---|---|---|---|---|
| all | 200 | 0.28 | 0.53 | 0.60 | 0.71 | 0.38 | 0.65 | 0.83 |
| company:APARINDS | 64 | 0.27 | 0.47 | 0.61 | 0.75 | 0.36 | 0.64 | 0.77 |
| company:HEROMOTOCO | 54 | 0.31 | 0.61 | 0.61 | 0.67 | 0.43 | 0.67 | 0.93 |
| company:E2E | 43 | 0.19 | 0.47 | 0.53 | 0.72 | 0.29 | 0.58 | 0.81 |
| company:ESCONET | 21 | 0.24 | 0.43 | 0.48 | 0.62 | 0.32 | 0.62 | 0.67 |
| company:C2C | 18 | 0.44 | 0.78 | 0.83 | 0.83 | 0.56 | 0.83 | 1.00 |
| doctype:annual_reports | 111 | 0.27 | 0.54 | 0.59 | 0.68 | 0.38 | 0.66 | 0.89 |
| doctype:investor_presentations | 47 | 0.21 | 0.38 | 0.53 | 0.70 | 0.29 | 0.57 | 0.64 |
| doctype:concall_transcripts | 38 | 0.37 | 0.66 | 0.68 | 0.82 | 0.47 | 0.68 | 0.87 |
| doctype:periodic_results | 4 | 0.25 | 0.75 | 1.00 | 1.00 | 0.41 | 1.00 | 1.00 |
| evidence:table | 63 | 0.24 | 0.46 | 0.54 | 0.68 | 0.33 | 0.67 | 0.79 |
| evidence:concall | 33 | 0.42 | 0.76 | 0.79 | 0.91 | 0.54 | 0.79 | 0.88 |
| evidence:prose | 33 | 0.27 | 0.64 | 0.64 | 0.70 | 0.41 | 0.64 | 0.85 |
| evidence:statement | 25 | 0.20 | 0.52 | 0.60 | 0.68 | 0.33 | 0.64 | 0.92 |
| evidence:chart | 15 | 0.33 | 0.60 | 0.73 | 0.80 | 0.43 | 0.80 | 0.87 |
| evidence:multi | 15 | 0.00 | 0.00 | 0.07 | 0.33 | 0.01 | 0.07 | 0.73 |
| evidence:scan | 10 | 0.50 | 0.60 | 0.80 | 0.90 | 0.58 | 0.80 | 0.80 |
| evidence:kpi | 6 | 0.33 | 0.50 | 0.67 | 0.67 | 0.44 | 0.67 | 0.67 |
| hard:decoy_years | 63 | 0.27 | 0.52 | 0.59 | 0.67 | 0.38 | 0.70 | 0.87 |
| hard:standalone_vs_consolidated | 22 | 0.23 | 0.36 | 0.45 | 0.50 | 0.30 | 0.55 | 0.95 |
| hard:cross_doc | 17 | 0.00 | 0.12 | 0.24 | 0.47 | 0.08 | 0.29 | 0.76 |
| hard:spoken_numbers | 16 | 0.44 | 0.69 | 0.69 | 0.81 | 0.52 | 0.69 | 0.88 |
| hard:chart_labels | 14 | 0.29 | 0.57 | 0.71 | 0.79 | 0.39 | 0.79 | 0.86 |
| hard:indian_grouping | 14 | 0.14 | 0.43 | 0.57 | 0.57 | 0.25 | 0.71 | 0.86 |
| hard:multi_hop | 14 | 0.00 | 0.00 | 0.07 | 0.29 | 0.01 | 0.07 | 0.79 |
| hard:slide_table | 13 | 0.15 | 0.31 | 0.31 | 0.54 | 0.19 | 0.38 | 0.46 |
| hard:lakhs_unit | 11 | 0.45 | 0.82 | 0.91 | 0.91 | 0.56 | 0.91 | 0.91 |
| hard:footnote | 10 | 0.20 | 0.50 | 0.70 | 0.70 | 0.32 | 0.70 | 0.90 |
| hard:image_only_page | 10 | 0.50 | 0.60 | 0.80 | 0.90 | 0.58 | 0.80 | 0.80 |
| hard:no_numbers | 10 | 0.20 | 0.70 | 0.80 | 0.90 | 0.39 | 0.80 | 0.80 |
| hard:period_format | 10 | 0.30 | 0.50 | 0.50 | 0.70 | 0.38 | 0.50 | 0.70 |
| style:paraphrase | 140 | 0.31 | 0.56 | 0.64 | 0.74 | 0.41 | 0.71 | 0.83 |
| style:exact | 25 | 0.16 | 0.52 | 0.56 | 0.72 | 0.32 | 0.60 | 0.80 |
| style:vague | 20 | 0.35 | 0.70 | 0.75 | 0.80 | 0.49 | 0.75 | 0.95 |
| style:analytical | 15 | 0.00 | 0.00 | 0.07 | 0.33 | 0.01 | 0.07 | 0.73 |

## Paired comparison vs `dense-voyage-4-large-2048.jsonl` (strict Recall@10)

Only this run finds: 2 (R001, R044)  
Only the other finds: 17 (R030, R032, R034, R036, R041, R065, R085, R112, R120, R125, R129, R133, R139, R141, R142, R152, R182)  
Ties: 181; exact sign test p = 0.001

## Not found in the top 10 (strict): 80

R004, R006, R009, R010, R013, R021, R022, R023, R025, R028, R029, R030, R032, R034, R036, R038, R041, R042, R050, R053, R055, R061, R062, R063, R064, R065, R068, R071, R073, R075, R076, R078, R079, R083, R085, R088, R090, R097, R098, R105, R107, R112, R115, R116, R117, R118, R120, R122, R125, R127, R129, R130, R133, R135, R136, R137, R139, R141, R142, R144, R145, R146, R152, R156, R159, R161, R163, R164, R165, R166, R170, R171, R172, R173, R179, R181, R182, R198, R199, R200
