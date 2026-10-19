# Retrieval score: `hybrid-dbsf-none.jsonl`

200 questions; missing from run: 0. Strict = answer pages checked on the image; lenient adds machine-found pages that print the answer's numbers. doc@10 = the right document anywhere in the top 10.

| group | n | strict_R@1 | strict_R@5 | strict_R@10 | strict_R@20 | strict_MRR@10 | lenient_R@10 | doc@10 |
|---|---|---|---|---|---|---|---|---|
| all | 200 | 0.24 | 0.48 | 0.57 | 0.72 | 0.36 | 0.61 | 0.82 |
| company:APARINDS | 64 | 0.25 | 0.52 | 0.62 | 0.75 | 0.39 | 0.64 | 0.73 |
| company:HEROMOTOCO | 54 | 0.30 | 0.56 | 0.61 | 0.76 | 0.42 | 0.65 | 0.94 |
| company:E2E | 43 | 0.16 | 0.35 | 0.44 | 0.60 | 0.25 | 0.49 | 0.79 |
| company:ESCONET | 21 | 0.05 | 0.33 | 0.48 | 0.67 | 0.16 | 0.62 | 0.71 |
| company:C2C | 18 | 0.50 | 0.67 | 0.72 | 0.83 | 0.57 | 0.72 | 0.94 |
| doctype:annual_reports | 111 | 0.24 | 0.50 | 0.57 | 0.70 | 0.36 | 0.63 | 0.85 |
| doctype:investor_presentations | 47 | 0.26 | 0.47 | 0.57 | 0.72 | 0.35 | 0.60 | 0.72 |
| doctype:concall_transcripts | 38 | 0.24 | 0.42 | 0.55 | 0.74 | 0.34 | 0.55 | 0.84 |
| doctype:periodic_results | 4 | 0.25 | 1.00 | 1.00 | 1.00 | 0.42 | 1.00 | 1.00 |
| evidence:table | 63 | 0.27 | 0.56 | 0.67 | 0.81 | 0.41 | 0.78 | 0.86 |
| evidence:concall | 33 | 0.27 | 0.48 | 0.64 | 0.79 | 0.39 | 0.64 | 0.85 |
| evidence:prose | 33 | 0.24 | 0.52 | 0.55 | 0.67 | 0.34 | 0.55 | 0.82 |
| evidence:statement | 25 | 0.20 | 0.44 | 0.56 | 0.64 | 0.30 | 0.56 | 0.76 |
| evidence:chart | 15 | 0.27 | 0.53 | 0.60 | 0.67 | 0.39 | 0.67 | 0.80 |
| evidence:multi | 15 | 0.00 | 0.07 | 0.07 | 0.33 | 0.03 | 0.07 | 0.80 |
| evidence:scan | 10 | 0.40 | 0.60 | 0.60 | 1.00 | 0.50 | 0.60 | 0.80 |
| evidence:kpi | 6 | 0.33 | 0.50 | 0.67 | 0.67 | 0.44 | 0.67 | 0.67 |
| hard:decoy_years | 63 | 0.25 | 0.49 | 0.59 | 0.71 | 0.37 | 0.67 | 0.83 |
| hard:standalone_vs_consolidated | 22 | 0.32 | 0.50 | 0.50 | 0.55 | 0.40 | 0.55 | 0.86 |
| hard:cross_doc | 17 | 0.00 | 0.06 | 0.06 | 0.41 | 0.02 | 0.06 | 0.71 |
| hard:spoken_numbers | 16 | 0.19 | 0.44 | 0.44 | 0.69 | 0.29 | 0.44 | 0.75 |
| hard:chart_labels | 14 | 0.21 | 0.50 | 0.57 | 0.64 | 0.35 | 0.64 | 0.79 |
| hard:indian_grouping | 14 | 0.07 | 0.43 | 0.64 | 0.79 | 0.23 | 0.79 | 0.93 |
| hard:multi_hop | 14 | 0.00 | 0.00 | 0.00 | 0.29 | 0.00 | 0.00 | 0.79 |
| hard:slide_table | 13 | 0.38 | 0.46 | 0.54 | 0.62 | 0.42 | 0.62 | 0.62 |
| hard:lakhs_unit | 11 | 0.27 | 0.73 | 0.82 | 0.82 | 0.42 | 0.82 | 0.82 |
| hard:footnote | 10 | 0.20 | 0.60 | 0.60 | 0.70 | 0.36 | 0.60 | 0.80 |
| hard:image_only_page | 10 | 0.40 | 0.60 | 0.60 | 1.00 | 0.50 | 0.60 | 0.80 |
| hard:no_numbers | 10 | 0.40 | 0.40 | 0.80 | 0.80 | 0.46 | 0.80 | 0.90 |
| hard:period_format | 10 | 0.10 | 0.40 | 0.50 | 0.70 | 0.22 | 0.50 | 0.60 |
| style:paraphrase | 140 | 0.26 | 0.54 | 0.62 | 0.77 | 0.39 | 0.67 | 0.83 |
| style:exact | 25 | 0.24 | 0.44 | 0.60 | 0.72 | 0.34 | 0.64 | 0.76 |
| style:vague | 20 | 0.35 | 0.45 | 0.60 | 0.65 | 0.42 | 0.60 | 0.85 |
| style:analytical | 15 | 0.00 | 0.07 | 0.07 | 0.33 | 0.03 | 0.07 | 0.80 |

## Paired comparison vs `dense-none.jsonl` (strict Recall@10)

Only this run finds: 5 (R025, R053, R078, R135, R181)  
Only the other finds: 25 (R002, R030, R032, R045, R100, R102, R103, R112, R120, R121, R125, R134, R141, R142, R147, R150, R151, R152, R155, R158, R160, R177, R182, R191, R195)  
Ties: 170; exact sign test p = 0.000

## Not found in the top 10 (strict): 85

R001, R002, R004, R006, R009, R010, R013, R021, R022, R023, R028, R029, R030, R032, R038, R042, R044, R045, R050, R055, R061, R062, R063, R064, R068, R071, R073, R075, R076, R079, R083, R088, R090, R097, R098, R100, R102, R103, R105, R107, R112, R115, R116, R117, R118, R120, R121, R122, R125, R127, R130, R134, R136, R137, R141, R142, R144, R145, R146, R147, R150, R151, R152, R155, R156, R158, R159, R160, R161, R163, R164, R165, R166, R170, R171, R172, R173, R177, R179, R182, R191, R195, R198, R199, R200
