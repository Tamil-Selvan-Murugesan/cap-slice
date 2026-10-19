# Retrieval score: `dense-voyage-4-large-2048-company.jsonl`

200 questions; missing from run: 0. Strict = answer pages checked on the image; lenient adds machine-found pages that print the answer's numbers. doc@10 = the right document anywhere in the top 10.

| group | n | strict_R@1 | strict_R@5 | strict_R@10 | strict_R@20 | strict_MRR@10 | lenient_R@10 | doc@10 |
|---|---|---|---|---|---|---|---|---|
| all | 200 | 0.30 | 0.60 | 0.67 | 0.79 | 0.43 | 0.71 | 0.85 |
| company:APARINDS | 64 | 0.27 | 0.58 | 0.69 | 0.84 | 0.40 | 0.72 | 0.81 |
| company:HEROMOTOCO | 54 | 0.28 | 0.54 | 0.57 | 0.61 | 0.40 | 0.63 | 0.81 |
| company:E2E | 43 | 0.28 | 0.60 | 0.72 | 0.86 | 0.42 | 0.74 | 0.95 |
| company:ESCONET | 21 | 0.43 | 0.57 | 0.57 | 0.81 | 0.47 | 0.71 | 0.76 |
| company:C2C | 18 | 0.44 | 0.89 | 0.89 | 0.94 | 0.62 | 0.89 | 1.00 |
| doctype:annual_reports | 111 | 0.31 | 0.60 | 0.65 | 0.73 | 0.43 | 0.72 | 0.89 |
| doctype:investor_presentations | 47 | 0.23 | 0.51 | 0.64 | 0.85 | 0.35 | 0.66 | 0.74 |
| doctype:concall_transcripts | 38 | 0.34 | 0.66 | 0.74 | 0.87 | 0.47 | 0.74 | 0.87 |
| doctype:periodic_results | 4 | 0.75 | 1.00 | 1.00 | 1.00 | 0.83 | 1.00 | 1.00 |
| evidence:table | 63 | 0.30 | 0.62 | 0.68 | 0.86 | 0.43 | 0.78 | 0.84 |
| evidence:concall | 33 | 0.39 | 0.73 | 0.82 | 0.91 | 0.54 | 0.82 | 0.91 |
| evidence:prose | 33 | 0.24 | 0.55 | 0.58 | 0.70 | 0.38 | 0.58 | 0.85 |
| evidence:statement | 25 | 0.36 | 0.64 | 0.68 | 0.76 | 0.47 | 0.76 | 0.88 |
| evidence:chart | 15 | 0.27 | 0.73 | 0.80 | 0.80 | 0.42 | 0.87 | 0.93 |
| evidence:multi | 15 | 0.00 | 0.13 | 0.20 | 0.47 | 0.05 | 0.20 | 0.67 |
| evidence:scan | 10 | 0.60 | 0.70 | 0.90 | 0.90 | 0.68 | 0.90 | 1.00 |
| evidence:kpi | 6 | 0.33 | 0.50 | 0.67 | 0.67 | 0.44 | 0.67 | 0.67 |
| hard:decoy_years | 63 | 0.32 | 0.60 | 0.65 | 0.76 | 0.43 | 0.75 | 0.86 |
| hard:standalone_vs_consolidated | 22 | 0.18 | 0.41 | 0.45 | 0.59 | 0.28 | 0.59 | 0.91 |
| hard:cross_doc | 17 | 0.00 | 0.35 | 0.41 | 0.59 | 0.13 | 0.41 | 0.76 |
| hard:spoken_numbers | 16 | 0.38 | 0.62 | 0.69 | 0.81 | 0.49 | 0.69 | 0.88 |
| hard:chart_labels | 14 | 0.21 | 0.71 | 0.79 | 0.79 | 0.38 | 0.86 | 0.93 |
| hard:indian_grouping | 14 | 0.21 | 0.64 | 0.79 | 0.93 | 0.41 | 0.93 | 0.86 |
| hard:multi_hop | 14 | 0.00 | 0.14 | 0.21 | 0.43 | 0.06 | 0.21 | 0.71 |
| hard:slide_table | 13 | 0.23 | 0.46 | 0.54 | 0.85 | 0.33 | 0.62 | 0.62 |
| hard:lakhs_unit | 11 | 0.45 | 0.91 | 0.91 | 1.00 | 0.62 | 0.91 | 0.91 |
| hard:footnote | 10 | 0.10 | 0.70 | 0.70 | 0.80 | 0.32 | 0.70 | 0.90 |
| hard:image_only_page | 10 | 0.60 | 0.70 | 0.90 | 0.90 | 0.68 | 0.90 | 1.00 |
| hard:no_numbers | 10 | 0.20 | 0.70 | 0.90 | 0.90 | 0.40 | 0.90 | 1.00 |
| hard:period_format | 10 | 0.50 | 0.60 | 0.60 | 0.80 | 0.55 | 0.60 | 0.70 |
| style:paraphrase | 140 | 0.33 | 0.66 | 0.72 | 0.83 | 0.46 | 0.76 | 0.86 |
| style:exact | 25 | 0.28 | 0.52 | 0.56 | 0.72 | 0.38 | 0.68 | 0.84 |
| style:vague | 20 | 0.40 | 0.65 | 0.80 | 0.85 | 0.53 | 0.80 | 1.00 |
| style:analytical | 15 | 0.00 | 0.13 | 0.20 | 0.47 | 0.05 | 0.20 | 0.67 |

## Paired comparison vs `bm25-mineru_advanced-company.jsonl` (strict Recall@10)

Only this run finds: 54 (R002, R005, R014, R015, R017, R026, R027, R030, R032, R033, R034, R037, R041, R044, R045, R048, R049, R052, R058, R072, R089, R096, R100, R103, R106, R109, R112, R119, R120, R121, R123, R125, R134, R141, R142, R143, R147, R150, R151, R152, R155, R157, R158, R160, R162, R167, R175, R176, R177, R180, R182, R184, R188, R195)  
Only the other finds: 14 (R004, R023, R025, R069, R078, R086, R087, R097, R107, R130, R135, R170, R171, R181)  
Ties: 132; exact sign test p = 0.000

## Not found in the top 10 (strict): 66

R004, R006, R009, R010, R013, R021, R022, R023, R025, R028, R029, R038, R042, R050, R053, R055, R061, R062, R063, R064, R066, R068, R069, R071, R073, R075, R076, R078, R079, R083, R086, R087, R088, R090, R097, R098, R099, R105, R107, R115, R116, R117, R118, R122, R127, R130, R135, R136, R137, R144, R145, R146, R156, R159, R161, R163, R164, R166, R170, R171, R172, R173, R179, R181, R199, R200
