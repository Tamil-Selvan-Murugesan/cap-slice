# Retrieval score: `hybrid-dbsf-question-soft.jsonl`

200 questions; missing from run: 0. Strict = answer pages checked on the image; lenient adds machine-found pages that print the answer's numbers. doc@10 = the right document anywhere in the top 10.

| group | n | strict_R@1 | strict_R@5 | strict_R@10 | strict_R@20 | strict_MRR@10 | lenient_R@10 | doc@10 |
|---|---|---|---|---|---|---|---|---|
| all | 200 | 0.37 | 0.66 | 0.77 | 0.82 | 0.50 | 0.80 | 0.94 |
| company:APARINDS | 64 | 0.38 | 0.75 | 0.88 | 0.92 | 0.55 | 0.88 | 0.92 |
| company:HEROMOTOCO | 54 | 0.41 | 0.69 | 0.78 | 0.80 | 0.54 | 0.83 | 0.98 |
| company:E2E | 43 | 0.28 | 0.51 | 0.58 | 0.74 | 0.37 | 0.67 | 0.91 |
| company:ESCONET | 21 | 0.29 | 0.52 | 0.67 | 0.71 | 0.39 | 0.67 | 0.90 |
| company:C2C | 18 | 0.56 | 0.78 | 0.89 | 0.89 | 0.67 | 0.89 | 1.00 |
| doctype:annual_reports | 111 | 0.39 | 0.69 | 0.77 | 0.83 | 0.53 | 0.84 | 0.97 |
| doctype:investor_presentations | 47 | 0.36 | 0.64 | 0.74 | 0.79 | 0.48 | 0.74 | 0.87 |
| doctype:concall_transcripts | 38 | 0.32 | 0.55 | 0.74 | 0.84 | 0.43 | 0.74 | 0.92 |
| doctype:periodic_results | 4 | 0.50 | 1.00 | 1.00 | 1.00 | 0.69 | 1.00 | 1.00 |
| evidence:table | 63 | 0.41 | 0.75 | 0.89 | 0.94 | 0.58 | 0.94 | 0.98 |
| evidence:concall | 33 | 0.36 | 0.61 | 0.79 | 0.88 | 0.48 | 0.79 | 0.91 |
| evidence:prose | 33 | 0.39 | 0.76 | 0.85 | 0.85 | 0.54 | 0.85 | 1.00 |
| evidence:statement | 25 | 0.36 | 0.68 | 0.76 | 0.84 | 0.50 | 0.84 | 0.92 |
| evidence:chart | 15 | 0.40 | 0.73 | 0.73 | 0.80 | 0.55 | 0.80 | 0.93 |
| evidence:multi | 15 | 0.00 | 0.13 | 0.20 | 0.33 | 0.07 | 0.20 | 1.00 |
| evidence:scan | 10 | 0.50 | 0.60 | 0.60 | 0.70 | 0.53 | 0.70 | 0.70 |
| evidence:kpi | 6 | 0.50 | 0.67 | 0.67 | 0.67 | 0.58 | 0.67 | 0.67 |
| hard:decoy_years | 63 | 0.38 | 0.70 | 0.79 | 0.86 | 0.53 | 0.87 | 0.94 |
| hard:standalone_vs_consolidated | 22 | 0.45 | 0.59 | 0.73 | 0.77 | 0.53 | 0.82 | 0.95 |
| hard:cross_doc | 17 | 0.00 | 0.18 | 0.24 | 0.41 | 0.08 | 0.24 | 0.94 |
| hard:spoken_numbers | 16 | 0.25 | 0.50 | 0.69 | 0.75 | 0.36 | 0.69 | 0.81 |
| hard:chart_labels | 14 | 0.36 | 0.71 | 0.71 | 0.79 | 0.51 | 0.79 | 0.93 |
| hard:indian_grouping | 14 | 0.14 | 0.71 | 0.93 | 0.93 | 0.41 | 0.93 | 1.00 |
| hard:multi_hop | 14 | 0.00 | 0.07 | 0.14 | 0.29 | 0.04 | 0.14 | 1.00 |
| hard:slide_table | 13 | 0.38 | 0.69 | 0.85 | 0.92 | 0.51 | 0.85 | 0.92 |
| hard:lakhs_unit | 11 | 0.45 | 0.82 | 0.82 | 0.82 | 0.60 | 0.91 | 0.82 |
| hard:footnote | 10 | 0.40 | 0.70 | 0.80 | 0.90 | 0.53 | 0.80 | 1.00 |
| hard:image_only_page | 10 | 0.50 | 0.60 | 0.60 | 0.70 | 0.53 | 0.70 | 0.70 |
| hard:no_numbers | 10 | 0.40 | 0.50 | 0.80 | 0.90 | 0.48 | 0.80 | 1.00 |
| hard:period_format | 10 | 0.30 | 0.70 | 0.80 | 0.90 | 0.46 | 0.80 | 0.90 |
| style:paraphrase | 140 | 0.40 | 0.71 | 0.80 | 0.85 | 0.54 | 0.84 | 0.94 |
| style:exact | 25 | 0.40 | 0.76 | 0.88 | 0.92 | 0.56 | 0.92 | 0.92 |
| style:vague | 20 | 0.40 | 0.60 | 0.80 | 0.90 | 0.48 | 0.80 | 0.95 |
| style:analytical | 15 | 0.00 | 0.13 | 0.20 | 0.33 | 0.07 | 0.20 | 1.00 |

## Paired comparison vs `dense-question-soft.jsonl` (strict Recall@10)

Only this run finds: 7 (R013, R021, R028, R079, R098, R107, R161)  
Only the other finds: 15 (R075, R090, R120, R125, R127, R134, R142, R143, R150, R151, R152, R155, R158, R166, R177)  
Ties: 178; exact sign test p = 0.134

## Not found in the top 10 (strict): 47

R023, R029, R030, R050, R061, R062, R063, R064, R068, R071, R073, R075, R076, R083, R090, R105, R115, R116, R117, R118, R120, R122, R125, R127, R134, R142, R143, R144, R145, R150, R151, R152, R155, R156, R157, R158, R159, R160, R163, R166, R172, R173, R177, R179, R182, R199, R200
