# Retrieval score: `bm25-mineru_advanced.jsonl`

200 questions; missing from run: 0. Strict = answer pages checked on the image; lenient adds machine-found pages that print the answer's numbers. doc@10 = the right document anywhere in the top 10.

| group | n | strict_R@1 | strict_R@5 | strict_R@10 | strict_R@20 | strict_MRR@10 | lenient_R@10 | doc@10 |
|---|---|---|---|---|---|---|---|---|
| all | 200 | 0.14 | 0.33 | 0.42 | 0.54 | 0.22 | 0.47 | 0.76 |
| company:APARINDS | 64 | 0.14 | 0.36 | 0.42 | 0.56 | 0.23 | 0.44 | 0.70 |
| company:HEROMOTOCO | 54 | 0.13 | 0.37 | 0.50 | 0.63 | 0.24 | 0.52 | 0.87 |
| company:E2E | 43 | 0.07 | 0.26 | 0.37 | 0.42 | 0.15 | 0.42 | 0.74 |
| company:ESCONET | 21 | 0.05 | 0.14 | 0.19 | 0.33 | 0.08 | 0.43 | 0.67 |
| company:C2C | 18 | 0.44 | 0.50 | 0.61 | 0.72 | 0.48 | 0.67 | 0.78 |
| doctype:annual_reports | 111 | 0.14 | 0.35 | 0.43 | 0.53 | 0.22 | 0.50 | 0.82 |
| doctype:investor_presentations | 47 | 0.19 | 0.34 | 0.45 | 0.53 | 0.27 | 0.49 | 0.64 |
| doctype:concall_transcripts | 38 | 0.08 | 0.26 | 0.37 | 0.55 | 0.16 | 0.37 | 0.76 |
| doctype:periodic_results | 4 | 0.25 | 0.25 | 0.50 | 0.75 | 0.28 | 0.75 | 0.50 |
| evidence:table | 63 | 0.16 | 0.38 | 0.49 | 0.59 | 0.24 | 0.60 | 0.83 |
| evidence:concall | 33 | 0.09 | 0.30 | 0.42 | 0.61 | 0.18 | 0.42 | 0.79 |
| evidence:prose | 33 | 0.15 | 0.30 | 0.36 | 0.55 | 0.22 | 0.36 | 0.67 |
| evidence:statement | 25 | 0.08 | 0.24 | 0.28 | 0.36 | 0.16 | 0.36 | 0.60 |
| evidence:chart | 15 | 0.27 | 0.53 | 0.60 | 0.67 | 0.40 | 0.67 | 0.93 |
| evidence:multi | 15 | 0.00 | 0.00 | 0.07 | 0.13 | 0.01 | 0.07 | 0.67 |
| evidence:scan | 10 | 0.20 | 0.50 | 0.70 | 0.70 | 0.33 | 0.70 | 0.90 |
| evidence:kpi | 6 | 0.33 | 0.50 | 0.67 | 0.83 | 0.44 | 0.67 | 0.67 |
| hard:decoy_years | 63 | 0.10 | 0.30 | 0.40 | 0.48 | 0.19 | 0.49 | 0.79 |
| hard:standalone_vs_consolidated | 22 | 0.05 | 0.41 | 0.45 | 0.45 | 0.20 | 0.50 | 0.86 |
| hard:cross_doc | 17 | 0.00 | 0.00 | 0.00 | 0.12 | 0.00 | 0.00 | 0.53 |
| hard:spoken_numbers | 16 | 0.00 | 0.19 | 0.38 | 0.50 | 0.09 | 0.38 | 0.75 |
| hard:chart_labels | 14 | 0.29 | 0.50 | 0.57 | 0.64 | 0.39 | 0.64 | 0.93 |
| hard:indian_grouping | 14 | 0.07 | 0.29 | 0.43 | 0.57 | 0.16 | 0.71 | 0.86 |
| hard:multi_hop | 14 | 0.00 | 0.00 | 0.00 | 0.07 | 0.00 | 0.00 | 0.64 |
| hard:slide_table | 13 | 0.23 | 0.38 | 0.46 | 0.46 | 0.30 | 0.54 | 0.54 |
| hard:lakhs_unit | 11 | 0.18 | 0.36 | 0.45 | 0.64 | 0.26 | 0.55 | 0.64 |
| hard:footnote | 10 | 0.10 | 0.50 | 0.50 | 0.50 | 0.23 | 0.50 | 0.80 |
| hard:image_only_page | 10 | 0.20 | 0.50 | 0.70 | 0.70 | 0.33 | 0.70 | 0.90 |
| hard:no_numbers | 10 | 0.10 | 0.40 | 0.50 | 0.70 | 0.23 | 0.50 | 0.90 |
| hard:period_format | 10 | 0.20 | 0.30 | 0.30 | 0.40 | 0.25 | 0.30 | 0.40 |
| style:paraphrase | 140 | 0.15 | 0.36 | 0.48 | 0.60 | 0.24 | 0.53 | 0.78 |
| style:exact | 25 | 0.12 | 0.32 | 0.36 | 0.40 | 0.20 | 0.48 | 0.68 |
| style:vague | 20 | 0.20 | 0.35 | 0.40 | 0.60 | 0.26 | 0.40 | 0.80 |
| style:analytical | 15 | 0.00 | 0.00 | 0.07 | 0.13 | 0.01 | 0.07 | 0.67 |

## Not found in the top 10 (strict): 115

R001, R002, R003, R004, R005, R006, R009, R010, R013, R014, R015, R017, R021, R022, R026, R027, R028, R029, R030, R032, R033, R034, R035, R037, R038, R042, R044, R045, R048, R049, R050, R053, R055, R058, R062, R063, R064, R066, R068, R069, R070, R071, R072, R073, R075, R076, R079, R083, R088, R089, R090, R096, R098, R099, R100, R103, R105, R106, R109, R112, R115, R116, R117, R118, R119, R120, R121, R122, R123, R125, R126, R127, R134, R136, R137, R138, R141, R142, R143, R144, R145, R147, R150, R151, R152, R155, R156, R158, R159, R160, R161, R162, R163, R164, R165, R166, R167, R170, R171, R172, R173, R174, R175, R176, R177, R179, R180, R182, R184, R190, R191, R195, R198, R199, R200
