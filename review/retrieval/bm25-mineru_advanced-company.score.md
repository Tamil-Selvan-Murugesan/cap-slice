# Retrieval score: `bm25-mineru_advanced-company.jsonl`

200 questions; missing from run: 0. Strict = answer pages checked on the image; lenient adds machine-found pages that print the answer's numbers. doc@10 = the right document anywhere in the top 10.

| group | n | strict_R@1 | strict_R@5 | strict_R@10 | strict_R@20 | strict_MRR@10 | lenient_R@10 | doc@10 |
|---|---|---|---|---|---|---|---|---|
| all | 200 | 0.20 | 0.39 | 0.47 | 0.62 | 0.28 | 0.53 | 0.82 |
| company:APARINDS | 64 | 0.19 | 0.38 | 0.44 | 0.69 | 0.27 | 0.48 | 0.77 |
| company:HEROMOTOCO | 54 | 0.22 | 0.46 | 0.54 | 0.67 | 0.30 | 0.56 | 0.89 |
| company:E2E | 43 | 0.12 | 0.28 | 0.37 | 0.47 | 0.18 | 0.42 | 0.77 |
| company:ESCONET | 21 | 0.14 | 0.24 | 0.38 | 0.57 | 0.20 | 0.57 | 0.86 |
| company:C2C | 18 | 0.50 | 0.67 | 0.72 | 0.72 | 0.58 | 0.78 | 0.89 |
| doctype:annual_reports | 111 | 0.21 | 0.41 | 0.47 | 0.62 | 0.28 | 0.56 | 0.87 |
| doctype:investor_presentations | 47 | 0.21 | 0.38 | 0.51 | 0.62 | 0.29 | 0.53 | 0.70 |
| doctype:concall_transcripts | 38 | 0.16 | 0.32 | 0.39 | 0.61 | 0.23 | 0.39 | 0.79 |
| doctype:periodic_results | 4 | 0.50 | 0.75 | 0.75 | 1.00 | 0.58 | 0.75 | 1.00 |
| evidence:table | 63 | 0.24 | 0.41 | 0.51 | 0.67 | 0.31 | 0.63 | 0.83 |
| evidence:concall | 33 | 0.18 | 0.33 | 0.42 | 0.67 | 0.25 | 0.42 | 0.82 |
| evidence:prose | 33 | 0.21 | 0.39 | 0.52 | 0.70 | 0.30 | 0.52 | 0.82 |
| evidence:statement | 25 | 0.16 | 0.40 | 0.44 | 0.56 | 0.23 | 0.52 | 0.76 |
| evidence:chart | 15 | 0.27 | 0.53 | 0.60 | 0.67 | 0.39 | 0.67 | 0.93 |
| evidence:multi | 15 | 0.00 | 0.13 | 0.13 | 0.13 | 0.07 | 0.13 | 0.80 |
| evidence:scan | 10 | 0.20 | 0.40 | 0.50 | 0.70 | 0.28 | 0.50 | 0.90 |
| evidence:kpi | 6 | 0.50 | 0.67 | 0.67 | 0.83 | 0.53 | 0.67 | 0.67 |
| hard:decoy_years | 63 | 0.19 | 0.41 | 0.46 | 0.59 | 0.27 | 0.60 | 0.81 |
| hard:standalone_vs_consolidated | 22 | 0.27 | 0.50 | 0.50 | 0.55 | 0.35 | 0.59 | 0.95 |
| hard:cross_doc | 17 | 0.00 | 0.06 | 0.06 | 0.12 | 0.03 | 0.06 | 0.65 |
| hard:spoken_numbers | 16 | 0.12 | 0.25 | 0.38 | 0.50 | 0.19 | 0.38 | 0.75 |
| hard:chart_labels | 14 | 0.29 | 0.50 | 0.57 | 0.64 | 0.38 | 0.64 | 0.93 |
| hard:indian_grouping | 14 | 0.14 | 0.29 | 0.50 | 0.71 | 0.21 | 0.71 | 0.93 |
| hard:multi_hop | 14 | 0.00 | 0.07 | 0.07 | 0.07 | 0.04 | 0.07 | 0.79 |
| hard:slide_table | 13 | 0.23 | 0.31 | 0.54 | 0.62 | 0.28 | 0.54 | 0.62 |
| hard:lakhs_unit | 11 | 0.27 | 0.45 | 0.45 | 0.82 | 0.33 | 0.45 | 0.82 |
| hard:footnote | 10 | 0.10 | 0.50 | 0.60 | 0.60 | 0.25 | 0.60 | 0.90 |
| hard:image_only_page | 10 | 0.20 | 0.40 | 0.50 | 0.70 | 0.28 | 0.50 | 0.90 |
| hard:no_numbers | 10 | 0.20 | 0.40 | 0.40 | 0.80 | 0.27 | 0.40 | 1.00 |
| hard:period_format | 10 | 0.30 | 0.30 | 0.40 | 0.60 | 0.32 | 0.40 | 0.60 |
| style:paraphrase | 140 | 0.21 | 0.40 | 0.51 | 0.67 | 0.29 | 0.56 | 0.80 |
| style:exact | 25 | 0.24 | 0.48 | 0.52 | 0.68 | 0.32 | 0.68 | 0.88 |
| style:vague | 20 | 0.25 | 0.40 | 0.40 | 0.60 | 0.30 | 0.40 | 0.90 |
| style:analytical | 15 | 0.00 | 0.13 | 0.13 | 0.13 | 0.07 | 0.13 | 0.80 |

## Paired comparison vs `bm25-mineru_advanced.jsonl` (strict Recall@10)

Only this run finds: 13 (R001, R003, R035, R069, R126, R138, R165, R170, R171, R174, R190, R191, R198)  
Only the other finds: 0 (-)  
Ties: 187; exact sign test p = 0.000

## Not found in the top 10 (strict): 106

R002, R005, R006, R009, R010, R013, R014, R015, R017, R021, R022, R026, R027, R028, R029, R030, R032, R033, R034, R037, R038, R041, R042, R044, R045, R048, R049, R050, R052, R053, R055, R058, R061, R062, R063, R064, R066, R068, R071, R072, R073, R075, R076, R079, R083, R088, R089, R090, R096, R098, R099, R100, R103, R105, R106, R109, R112, R115, R116, R117, R118, R119, R120, R121, R122, R123, R125, R127, R134, R136, R137, R141, R142, R143, R144, R145, R146, R147, R150, R151, R152, R155, R156, R157, R158, R159, R160, R161, R162, R163, R164, R166, R167, R172, R173, R175, R176, R177, R179, R180, R182, R184, R188, R195, R199, R200
