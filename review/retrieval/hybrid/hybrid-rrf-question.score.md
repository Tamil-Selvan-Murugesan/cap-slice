# Retrieval score: `hybrid-rrf-question.jsonl`

200 questions; missing from run: 0. Strict = answer pages checked on the image; lenient adds machine-found pages that print the answer's numbers. doc@10 = the right document anywhere in the top 10.

| group | n | strict_R@1 | strict_R@5 | strict_R@10 | strict_R@20 | strict_MRR@10 | lenient_R@10 | doc@10 |
|---|---|---|---|---|---|---|---|---|
| all | 200 | 0.39 | 0.65 | 0.73 | 0.81 | 0.50 | 0.77 | 0.92 |
| company:APARINDS | 64 | 0.45 | 0.73 | 0.86 | 0.91 | 0.58 | 0.86 | 0.91 |
| company:HEROMOTOCO | 54 | 0.37 | 0.63 | 0.67 | 0.74 | 0.48 | 0.72 | 0.93 |
| company:E2E | 43 | 0.28 | 0.53 | 0.58 | 0.77 | 0.37 | 0.67 | 0.91 |
| company:ESCONET | 21 | 0.24 | 0.52 | 0.67 | 0.71 | 0.37 | 0.71 | 0.90 |
| company:C2C | 18 | 0.67 | 0.83 | 0.89 | 0.89 | 0.73 | 0.89 | 0.94 |
| doctype:annual_reports | 111 | 0.41 | 0.66 | 0.70 | 0.81 | 0.51 | 0.77 | 0.94 |
| doctype:investor_presentations | 47 | 0.40 | 0.66 | 0.77 | 0.79 | 0.51 | 0.77 | 0.87 |
| doctype:concall_transcripts | 38 | 0.32 | 0.61 | 0.74 | 0.82 | 0.44 | 0.74 | 0.89 |
| doctype:periodic_results | 4 | 0.50 | 0.75 | 1.00 | 1.00 | 0.67 | 1.00 | 1.00 |
| evidence:table | 63 | 0.46 | 0.78 | 0.86 | 0.92 | 0.58 | 0.94 | 0.97 |
| evidence:concall | 33 | 0.36 | 0.67 | 0.76 | 0.85 | 0.49 | 0.76 | 0.91 |
| evidence:prose | 33 | 0.42 | 0.67 | 0.70 | 0.79 | 0.53 | 0.70 | 0.94 |
| evidence:statement | 25 | 0.28 | 0.56 | 0.72 | 0.88 | 0.43 | 0.76 | 0.88 |
| evidence:chart | 15 | 0.53 | 0.73 | 0.80 | 0.80 | 0.61 | 0.87 | 0.93 |
| evidence:multi | 15 | 0.00 | 0.13 | 0.27 | 0.33 | 0.08 | 0.27 | 0.93 |
| evidence:scan | 10 | 0.50 | 0.60 | 0.60 | 0.70 | 0.53 | 0.70 | 0.70 |
| evidence:kpi | 6 | 0.50 | 0.67 | 0.67 | 0.67 | 0.58 | 0.67 | 0.67 |
| hard:decoy_years | 63 | 0.38 | 0.67 | 0.75 | 0.84 | 0.50 | 0.84 | 0.89 |
| hard:standalone_vs_consolidated | 22 | 0.50 | 0.55 | 0.64 | 0.82 | 0.53 | 0.73 | 0.95 |
| hard:cross_doc | 17 | 0.00 | 0.12 | 0.24 | 0.41 | 0.07 | 0.24 | 0.88 |
| hard:spoken_numbers | 16 | 0.25 | 0.56 | 0.62 | 0.69 | 0.36 | 0.62 | 0.81 |
| hard:chart_labels | 14 | 0.50 | 0.71 | 0.79 | 0.79 | 0.59 | 0.86 | 0.93 |
| hard:indian_grouping | 14 | 0.14 | 0.79 | 0.93 | 0.93 | 0.40 | 0.93 | 1.00 |
| hard:multi_hop | 14 | 0.00 | 0.07 | 0.21 | 0.29 | 0.05 | 0.21 | 0.93 |
| hard:slide_table | 13 | 0.46 | 0.77 | 0.85 | 0.92 | 0.55 | 0.85 | 0.92 |
| hard:lakhs_unit | 11 | 0.36 | 0.73 | 0.82 | 0.82 | 0.55 | 0.91 | 0.82 |
| hard:footnote | 10 | 0.30 | 0.80 | 0.90 | 0.90 | 0.51 | 0.90 | 1.00 |
| hard:image_only_page | 10 | 0.50 | 0.60 | 0.60 | 0.70 | 0.53 | 0.70 | 0.70 |
| hard:no_numbers | 10 | 0.40 | 0.60 | 0.80 | 0.90 | 0.50 | 0.80 | 1.00 |
| hard:period_format | 10 | 0.30 | 0.60 | 0.80 | 0.90 | 0.45 | 0.80 | 0.90 |
| style:paraphrase | 140 | 0.42 | 0.70 | 0.77 | 0.83 | 0.54 | 0.83 | 0.91 |
| style:exact | 25 | 0.40 | 0.72 | 0.80 | 0.96 | 0.54 | 0.80 | 0.92 |
| style:vague | 20 | 0.45 | 0.60 | 0.70 | 0.85 | 0.50 | 0.70 | 0.95 |
| style:analytical | 15 | 0.00 | 0.13 | 0.27 | 0.33 | 0.08 | 0.27 | 0.93 |

## Paired comparison vs `dense-question.jsonl` (strict Recall@10)

Only this run finds: 7 (R013, R021, R028, R063, R069, R087, R161)  
Only the other finds: 16 (R010, R075, R090, R120, R121, R125, R127, R142, R143, R150, R151, R152, R155, R158, R166, R177)  
Ties: 177; exact sign test p = 0.093

## Not found in the top 10 (strict): 54

R010, R023, R029, R030, R040, R050, R061, R062, R064, R068, R071, R073, R075, R076, R078, R079, R083, R088, R090, R098, R099, R105, R107, R115, R116, R117, R118, R120, R121, R122, R125, R127, R142, R143, R144, R145, R150, R151, R152, R155, R156, R157, R158, R159, R160, R163, R166, R172, R173, R177, R179, R182, R199, R200
