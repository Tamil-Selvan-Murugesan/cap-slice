# Retrieval score: `bm25-mineru_advanced-question-soft.jsonl`

200 questions; missing from run: 0. Strict = answer pages checked on the image; lenient adds machine-found pages that print the answer's numbers. doc@10 = the right document anywhere in the top 10.

| group | n | strict_R@1 | strict_R@5 | strict_R@10 | strict_R@20 | strict_MRR@10 | lenient_R@10 | doc@10 |
|---|---|---|---|---|---|---|---|---|
| all | 200 | 0.30 | 0.57 | 0.65 | 0.72 | 0.41 | 0.69 | 0.94 |
| company:APARINDS | 64 | 0.31 | 0.66 | 0.73 | 0.83 | 0.44 | 0.73 | 0.98 |
| company:HEROMOTOCO | 54 | 0.35 | 0.65 | 0.69 | 0.74 | 0.46 | 0.72 | 0.96 |
| company:E2E | 43 | 0.21 | 0.40 | 0.49 | 0.53 | 0.29 | 0.58 | 0.91 |
| company:ESCONET | 21 | 0.14 | 0.38 | 0.52 | 0.71 | 0.25 | 0.57 | 0.90 |
| company:C2C | 18 | 0.56 | 0.72 | 0.72 | 0.78 | 0.64 | 0.78 | 0.89 |
| doctype:annual_reports | 111 | 0.34 | 0.60 | 0.66 | 0.73 | 0.43 | 0.73 | 0.96 |
| doctype:investor_presentations | 47 | 0.26 | 0.57 | 0.68 | 0.70 | 0.41 | 0.68 | 0.89 |
| doctype:concall_transcripts | 38 | 0.24 | 0.47 | 0.55 | 0.71 | 0.33 | 0.55 | 0.95 |
| doctype:periodic_results | 4 | 0.50 | 0.75 | 0.75 | 1.00 | 0.58 | 0.75 | 1.00 |
| evidence:table | 63 | 0.37 | 0.67 | 0.78 | 0.84 | 0.49 | 0.86 | 0.98 |
| evidence:concall | 33 | 0.27 | 0.52 | 0.61 | 0.76 | 0.37 | 0.61 | 0.97 |
| evidence:prose | 33 | 0.27 | 0.67 | 0.73 | 0.76 | 0.42 | 0.73 | 0.97 |
| evidence:statement | 25 | 0.24 | 0.48 | 0.56 | 0.68 | 0.31 | 0.60 | 0.84 |
| evidence:chart | 15 | 0.47 | 0.67 | 0.67 | 0.67 | 0.56 | 0.73 | 1.00 |
| evidence:multi | 15 | 0.00 | 0.13 | 0.13 | 0.20 | 0.07 | 0.13 | 0.93 |
| evidence:scan | 10 | 0.30 | 0.50 | 0.50 | 0.70 | 0.40 | 0.60 | 0.80 |
| evidence:kpi | 6 | 0.67 | 0.83 | 0.83 | 0.83 | 0.75 | 0.83 | 0.83 |
| hard:decoy_years | 63 | 0.35 | 0.56 | 0.65 | 0.73 | 0.42 | 0.75 | 0.94 |
| hard:standalone_vs_consolidated | 22 | 0.50 | 0.55 | 0.59 | 0.64 | 0.52 | 0.64 | 0.95 |
| hard:cross_doc | 17 | 0.00 | 0.06 | 0.12 | 0.18 | 0.04 | 0.12 | 0.88 |
| hard:spoken_numbers | 16 | 0.25 | 0.44 | 0.56 | 0.62 | 0.34 | 0.56 | 1.00 |
| hard:chart_labels | 14 | 0.43 | 0.64 | 0.64 | 0.64 | 0.52 | 0.71 | 1.00 |
| hard:indian_grouping | 14 | 0.21 | 0.57 | 0.79 | 0.93 | 0.34 | 0.86 | 1.00 |
| hard:multi_hop | 14 | 0.00 | 0.07 | 0.07 | 0.14 | 0.04 | 0.07 | 0.93 |
| hard:slide_table | 13 | 0.23 | 0.62 | 0.77 | 0.77 | 0.40 | 0.77 | 0.85 |
| hard:lakhs_unit | 11 | 0.27 | 0.55 | 0.64 | 0.73 | 0.38 | 0.73 | 0.82 |
| hard:footnote | 10 | 0.10 | 0.60 | 0.80 | 0.80 | 0.33 | 0.80 | 1.00 |
| hard:image_only_page | 10 | 0.30 | 0.50 | 0.50 | 0.70 | 0.40 | 0.60 | 0.80 |
| hard:no_numbers | 10 | 0.20 | 0.40 | 0.50 | 0.80 | 0.28 | 0.50 | 1.00 |
| hard:period_format | 10 | 0.30 | 0.60 | 0.60 | 0.90 | 0.43 | 0.60 | 0.90 |
| style:paraphrase | 140 | 0.34 | 0.62 | 0.69 | 0.76 | 0.45 | 0.74 | 0.94 |
| style:exact | 25 | 0.36 | 0.68 | 0.80 | 0.88 | 0.47 | 0.88 | 0.96 |
| style:vague | 20 | 0.25 | 0.45 | 0.50 | 0.70 | 0.34 | 0.50 | 0.95 |
| style:analytical | 15 | 0.00 | 0.13 | 0.13 | 0.20 | 0.07 | 0.13 | 0.93 |

## Paired comparison vs `bm25-mineru_advanced-company.jsonl` (strict Recall@10)

Only this run finds: 36 (R005, R006, R009, R013, R014, R017, R021, R026, R027, R033, R034, R037, R038, R041, R042, R044, R048, R049, R053, R066, R089, R096, R098, R099, R103, R106, R109, R119, R123, R136, R137, R146, R164, R167, R175, R188)  
Only the other finds: 1 (R191)  
Ties: 163; exact sign test p = 0.000

## Not found in the top 10 (strict): 71

R002, R010, R015, R022, R028, R029, R030, R032, R045, R050, R052, R055, R058, R061, R062, R063, R064, R068, R071, R072, R073, R075, R076, R079, R083, R088, R090, R100, R105, R112, R115, R116, R117, R118, R120, R121, R122, R125, R127, R134, R141, R142, R143, R144, R145, R147, R150, R151, R152, R155, R156, R157, R158, R159, R160, R161, R162, R163, R166, R172, R173, R176, R177, R179, R180, R182, R184, R191, R195, R199, R200
