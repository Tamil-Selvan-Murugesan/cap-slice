# Retrieval score: `bm25-mineru_advanced-company.jsonl`

200 questions; missing from run: 0. Strict = answer pages checked on the image; lenient adds machine-found pages that print the answer's numbers. doc@10 = the right document anywhere in the top 10.

| group | n | strict_R@1 | strict_R@5 | strict_R@10 | strict_R@20 | strict_MRR@10 | lenient_R@10 | doc@10 |
|---|---|---|---|---|---|---|---|---|
| all | 200 | 0.19 | 0.39 | 0.49 | 0.64 | 0.28 | 0.54 | 0.82 |
| company:APARINDS | 64 | 0.19 | 0.39 | 0.48 | 0.70 | 0.27 | 0.52 | 0.75 |
| company:HEROMOTOCO | 54 | 0.19 | 0.41 | 0.54 | 0.65 | 0.28 | 0.56 | 0.89 |
| company:E2E | 43 | 0.09 | 0.28 | 0.42 | 0.49 | 0.19 | 0.44 | 0.84 |
| company:ESCONET | 21 | 0.14 | 0.29 | 0.33 | 0.62 | 0.19 | 0.57 | 0.81 |
| company:C2C | 18 | 0.50 | 0.67 | 0.72 | 0.72 | 0.58 | 0.78 | 0.89 |
| doctype:annual_reports | 111 | 0.20 | 0.41 | 0.52 | 0.66 | 0.29 | 0.59 | 0.89 |
| doctype:investor_presentations | 47 | 0.21 | 0.36 | 0.47 | 0.62 | 0.29 | 0.51 | 0.68 |
| doctype:concall_transcripts | 38 | 0.11 | 0.32 | 0.39 | 0.55 | 0.19 | 0.39 | 0.79 |
| doctype:periodic_results | 4 | 0.50 | 0.75 | 0.75 | 1.00 | 0.62 | 0.75 | 1.00 |
| evidence:table | 63 | 0.24 | 0.44 | 0.54 | 0.71 | 0.32 | 0.65 | 0.86 |
| evidence:concall | 33 | 0.12 | 0.33 | 0.42 | 0.61 | 0.21 | 0.42 | 0.82 |
| evidence:prose | 33 | 0.18 | 0.36 | 0.52 | 0.67 | 0.27 | 0.52 | 0.82 |
| evidence:statement | 25 | 0.16 | 0.32 | 0.44 | 0.64 | 0.24 | 0.52 | 0.76 |
| evidence:chart | 15 | 0.27 | 0.53 | 0.60 | 0.67 | 0.41 | 0.67 | 0.93 |
| evidence:multi | 15 | 0.00 | 0.13 | 0.13 | 0.13 | 0.06 | 0.13 | 0.73 |
| evidence:scan | 10 | 0.20 | 0.50 | 0.70 | 0.70 | 0.33 | 0.70 | 0.90 |
| evidence:kpi | 6 | 0.50 | 0.50 | 0.67 | 0.83 | 0.52 | 0.67 | 0.67 |
| hard:decoy_years | 63 | 0.19 | 0.35 | 0.49 | 0.65 | 0.27 | 0.60 | 0.86 |
| hard:standalone_vs_consolidated | 22 | 0.23 | 0.45 | 0.45 | 0.55 | 0.33 | 0.55 | 0.86 |
| hard:cross_doc | 17 | 0.00 | 0.06 | 0.06 | 0.12 | 0.03 | 0.06 | 0.59 |
| hard:spoken_numbers | 16 | 0.06 | 0.25 | 0.38 | 0.50 | 0.15 | 0.38 | 0.81 |
| hard:chart_labels | 14 | 0.29 | 0.50 | 0.57 | 0.64 | 0.40 | 0.64 | 0.93 |
| hard:indian_grouping | 14 | 0.14 | 0.43 | 0.50 | 0.71 | 0.26 | 0.71 | 0.93 |
| hard:multi_hop | 14 | 0.00 | 0.07 | 0.07 | 0.07 | 0.04 | 0.07 | 0.71 |
| hard:slide_table | 13 | 0.23 | 0.38 | 0.46 | 0.62 | 0.30 | 0.54 | 0.62 |
| hard:lakhs_unit | 11 | 0.18 | 0.45 | 0.55 | 0.91 | 0.31 | 0.55 | 0.82 |
| hard:footnote | 10 | 0.10 | 0.50 | 0.60 | 0.60 | 0.25 | 0.60 | 0.90 |
| hard:image_only_page | 10 | 0.20 | 0.50 | 0.70 | 0.70 | 0.33 | 0.70 | 0.90 |
| hard:no_numbers | 10 | 0.10 | 0.40 | 0.60 | 0.80 | 0.24 | 0.60 | 1.00 |
| hard:period_format | 10 | 0.30 | 0.30 | 0.30 | 0.60 | 0.30 | 0.30 | 0.50 |
| style:paraphrase | 140 | 0.21 | 0.39 | 0.51 | 0.67 | 0.29 | 0.56 | 0.81 |
| style:exact | 25 | 0.20 | 0.48 | 0.56 | 0.76 | 0.33 | 0.68 | 0.88 |
| style:vague | 20 | 0.20 | 0.45 | 0.50 | 0.60 | 0.29 | 0.50 | 0.90 |
| style:analytical | 15 | 0.00 | 0.13 | 0.13 | 0.13 | 0.06 | 0.13 | 0.73 |

## Paired comparison vs `bm25-mineru_advanced.jsonl` (strict Recall@10)

Only this run finds: 13 (R001, R003, R017, R035, R069, R099, R126, R138, R165, R173, R174, R190, R198)  
Only the other finds: 0 (-)  
Ties: 187; exact sign test p = 0.000

## Not found in the top 10 (strict): 102

R002, R004, R005, R006, R009, R010, R013, R014, R015, R021, R022, R026, R027, R028, R029, R030, R032, R033, R034, R037, R038, R042, R044, R045, R048, R049, R050, R053, R055, R058, R062, R063, R064, R066, R068, R070, R071, R072, R073, R075, R076, R079, R083, R088, R089, R090, R096, R098, R100, R103, R105, R106, R109, R112, R115, R116, R117, R118, R119, R120, R121, R122, R123, R125, R127, R134, R136, R137, R141, R142, R143, R144, R145, R147, R150, R151, R152, R155, R156, R158, R159, R160, R161, R162, R163, R164, R166, R167, R170, R171, R172, R175, R176, R177, R179, R180, R182, R184, R191, R195, R199, R200
