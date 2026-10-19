# Retrieval score: `bm25-mineru_advanced-answer_key.jsonl`

200 questions; missing from run: 0. Strict = answer pages checked on the image; lenient adds machine-found pages that print the answer's numbers. doc@10 = the right document anywhere in the top 10.

| group | n | strict_R@1 | strict_R@5 | strict_R@10 | strict_R@20 | strict_MRR@10 | lenient_R@10 | doc@10 |
|---|---|---|---|---|---|---|---|---|
| all | 200 | 0.40 | 0.69 | 0.73 | 0.81 | 0.51 | 0.77 | 0.99 |
| company:APARINDS | 64 | 0.39 | 0.78 | 0.83 | 0.86 | 0.55 | 0.83 | 1.00 |
| company:HEROMOTOCO | 54 | 0.48 | 0.70 | 0.72 | 0.81 | 0.56 | 0.76 | 1.00 |
| company:E2E | 43 | 0.26 | 0.53 | 0.63 | 0.70 | 0.37 | 0.70 | 1.00 |
| company:ESCONET | 21 | 0.29 | 0.62 | 0.67 | 0.86 | 0.39 | 0.71 | 0.95 |
| company:C2C | 18 | 0.61 | 0.72 | 0.72 | 0.78 | 0.67 | 0.78 | 1.00 |
| doctype:annual_reports | 111 | 0.38 | 0.68 | 0.72 | 0.80 | 0.50 | 0.78 | 1.00 |
| doctype:investor_presentations | 47 | 0.43 | 0.77 | 0.79 | 0.83 | 0.55 | 0.79 | 0.98 |
| doctype:concall_transcripts | 38 | 0.37 | 0.61 | 0.68 | 0.76 | 0.46 | 0.68 | 1.00 |
| doctype:periodic_results | 4 | 0.75 | 0.75 | 0.75 | 1.00 | 0.75 | 0.75 | 1.00 |
| evidence:table | 63 | 0.43 | 0.76 | 0.83 | 0.87 | 0.56 | 0.90 | 1.00 |
| evidence:concall | 33 | 0.42 | 0.70 | 0.79 | 0.88 | 0.53 | 0.79 | 1.00 |
| evidence:prose | 33 | 0.33 | 0.76 | 0.79 | 0.91 | 0.49 | 0.79 | 1.00 |
| evidence:statement | 25 | 0.32 | 0.68 | 0.72 | 0.80 | 0.45 | 0.76 | 1.00 |
| evidence:chart | 15 | 0.53 | 0.67 | 0.67 | 0.73 | 0.59 | 0.73 | 1.00 |
| evidence:multi | 15 | 0.07 | 0.07 | 0.07 | 0.07 | 0.07 | 0.07 | 1.00 |
| evidence:scan | 10 | 0.40 | 0.70 | 0.70 | 0.90 | 0.55 | 0.70 | 0.90 |
| evidence:kpi | 6 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| hard:decoy_years | 63 | 0.43 | 0.68 | 0.75 | 0.79 | 0.52 | 0.84 | 1.00 |
| hard:standalone_vs_consolidated | 22 | 0.55 | 0.59 | 0.64 | 0.64 | 0.57 | 0.68 | 1.00 |
| hard:cross_doc | 17 | 0.00 | 0.12 | 0.12 | 0.18 | 0.03 | 0.12 | 1.00 |
| hard:spoken_numbers | 16 | 0.31 | 0.62 | 0.69 | 0.81 | 0.43 | 0.69 | 1.00 |
| hard:chart_labels | 14 | 0.50 | 0.64 | 0.64 | 0.71 | 0.56 | 0.71 | 1.00 |
| hard:indian_grouping | 14 | 0.29 | 0.64 | 0.86 | 1.00 | 0.45 | 0.93 | 1.00 |
| hard:multi_hop | 14 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 1.00 |
| hard:slide_table | 13 | 0.38 | 0.92 | 0.92 | 0.92 | 0.57 | 0.92 | 1.00 |
| hard:lakhs_unit | 11 | 0.36 | 0.82 | 0.91 | 1.00 | 0.55 | 0.91 | 1.00 |
| hard:footnote | 10 | 0.10 | 0.70 | 0.80 | 1.00 | 0.35 | 0.80 | 1.00 |
| hard:image_only_page | 10 | 0.40 | 0.70 | 0.70 | 0.90 | 0.55 | 0.70 | 0.90 |
| hard:no_numbers | 10 | 0.30 | 0.70 | 0.90 | 1.00 | 0.45 | 0.90 | 1.00 |
| hard:period_format | 10 | 0.50 | 0.70 | 0.80 | 0.90 | 0.59 | 0.80 | 1.00 |
| style:paraphrase | 140 | 0.43 | 0.74 | 0.78 | 0.84 | 0.54 | 0.81 | 1.00 |
| style:exact | 25 | 0.48 | 0.80 | 0.88 | 0.92 | 0.62 | 0.96 | 1.00 |
| style:vague | 20 | 0.30 | 0.65 | 0.70 | 0.95 | 0.44 | 0.70 | 0.95 |
| style:analytical | 15 | 0.07 | 0.07 | 0.07 | 0.07 | 0.07 | 0.07 | 1.00 |

## Paired comparison vs `bm25-mineru_advanced-company.jsonl` (strict Recall@10)

Only this run finds: 53 (R005, R006, R009, R013, R014, R015, R017, R021, R022, R026, R027, R030, R033, R034, R037, R038, R041, R042, R044, R048, R049, R052, R053, R055, R061, R066, R089, R090, R096, R098, R099, R103, R105, R106, R109, R119, R123, R127, R136, R137, R141, R145, R146, R147, R152, R157, R163, R164, R167, R173, R175, R176, R188)  
Only the other finds: 1 (R198)  
Ties: 146; exact sign test p = 0.000

## Not found in the top 10 (strict): 54

R002, R010, R028, R029, R032, R045, R050, R058, R062, R063, R064, R068, R071, R072, R073, R075, R076, R079, R083, R088, R100, R112, R115, R116, R117, R118, R120, R121, R122, R125, R134, R142, R143, R144, R150, R151, R155, R156, R158, R159, R160, R161, R162, R166, R172, R177, R179, R180, R182, R184, R195, R198, R199, R200
