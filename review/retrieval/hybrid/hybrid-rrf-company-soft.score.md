# Retrieval score: `hybrid-rrf-company-soft.jsonl`

200 questions; missing from run: 0. Strict = answer pages checked on the image; lenient adds machine-found pages that print the answer's numbers. doc@10 = the right document anywhere in the top 10.

| group | n | strict_R@1 | strict_R@5 | strict_R@10 | strict_R@20 | strict_MRR@10 | lenient_R@10 | doc@10 |
|---|---|---|---|---|---|---|---|---|
| all | 200 | 0.30 | 0.52 | 0.63 | 0.75 | 0.40 | 0.69 | 0.88 |
| company:APARINDS | 64 | 0.28 | 0.58 | 0.69 | 0.81 | 0.42 | 0.72 | 0.83 |
| company:HEROMOTOCO | 54 | 0.35 | 0.56 | 0.65 | 0.76 | 0.44 | 0.69 | 0.94 |
| company:E2E | 43 | 0.21 | 0.40 | 0.53 | 0.65 | 0.29 | 0.60 | 0.86 |
| company:ESCONET | 21 | 0.14 | 0.33 | 0.52 | 0.67 | 0.24 | 0.67 | 0.90 |
| company:C2C | 18 | 0.61 | 0.72 | 0.72 | 0.83 | 0.65 | 0.78 | 0.89 |
| doctype:annual_reports | 111 | 0.32 | 0.52 | 0.62 | 0.75 | 0.41 | 0.71 | 0.92 |
| doctype:investor_presentations | 47 | 0.26 | 0.53 | 0.64 | 0.74 | 0.37 | 0.66 | 0.81 |
| doctype:concall_transcripts | 38 | 0.29 | 0.47 | 0.61 | 0.74 | 0.37 | 0.61 | 0.84 |
| doctype:periodic_results | 4 | 0.50 | 0.75 | 1.00 | 1.00 | 0.67 | 1.00 | 1.00 |
| evidence:table | 63 | 0.32 | 0.56 | 0.71 | 0.87 | 0.43 | 0.86 | 0.95 |
| evidence:concall | 33 | 0.33 | 0.52 | 0.64 | 0.79 | 0.41 | 0.64 | 0.88 |
| evidence:prose | 33 | 0.30 | 0.52 | 0.61 | 0.73 | 0.40 | 0.61 | 0.85 |
| evidence:statement | 25 | 0.24 | 0.56 | 0.64 | 0.72 | 0.37 | 0.68 | 0.88 |
| evidence:chart | 15 | 0.40 | 0.60 | 0.73 | 0.73 | 0.49 | 0.80 | 0.87 |
| evidence:multi | 15 | 0.00 | 0.13 | 0.20 | 0.27 | 0.07 | 0.20 | 0.87 |
| evidence:scan | 10 | 0.40 | 0.60 | 0.60 | 0.80 | 0.50 | 0.60 | 0.70 |
| evidence:kpi | 6 | 0.50 | 0.67 | 0.67 | 0.67 | 0.54 | 0.67 | 0.67 |
| hard:decoy_years | 63 | 0.30 | 0.56 | 0.67 | 0.79 | 0.41 | 0.79 | 0.94 |
| hard:standalone_vs_consolidated | 22 | 0.45 | 0.50 | 0.55 | 0.59 | 0.47 | 0.64 | 0.95 |
| hard:cross_doc | 17 | 0.00 | 0.12 | 0.24 | 0.35 | 0.07 | 0.24 | 0.82 |
| hard:spoken_numbers | 16 | 0.25 | 0.38 | 0.44 | 0.62 | 0.31 | 0.44 | 0.75 |
| hard:chart_labels | 14 | 0.36 | 0.57 | 0.71 | 0.71 | 0.45 | 0.79 | 0.86 |
| hard:indian_grouping | 14 | 0.14 | 0.43 | 0.71 | 0.86 | 0.29 | 0.86 | 1.00 |
| hard:multi_hop | 14 | 0.00 | 0.07 | 0.14 | 0.21 | 0.04 | 0.14 | 0.86 |
| hard:slide_table | 13 | 0.23 | 0.46 | 0.54 | 0.69 | 0.34 | 0.62 | 0.69 |
| hard:lakhs_unit | 11 | 0.36 | 0.64 | 0.91 | 0.91 | 0.48 | 0.91 | 0.91 |
| hard:footnote | 10 | 0.20 | 0.50 | 0.70 | 0.80 | 0.36 | 0.70 | 0.90 |
| hard:image_only_page | 10 | 0.40 | 0.60 | 0.60 | 0.80 | 0.50 | 0.60 | 0.70 |
| hard:no_numbers | 10 | 0.40 | 0.50 | 0.70 | 0.80 | 0.45 | 0.70 | 1.00 |
| hard:period_format | 10 | 0.20 | 0.50 | 0.60 | 0.70 | 0.28 | 0.60 | 0.70 |
| style:paraphrase | 140 | 0.31 | 0.55 | 0.67 | 0.80 | 0.42 | 0.74 | 0.89 |
| style:exact | 25 | 0.32 | 0.60 | 0.68 | 0.84 | 0.44 | 0.76 | 0.88 |
| style:vague | 20 | 0.45 | 0.50 | 0.60 | 0.65 | 0.47 | 0.60 | 0.85 |
| style:analytical | 15 | 0.00 | 0.13 | 0.20 | 0.27 | 0.07 | 0.20 | 0.87 |

## Paired comparison vs `dense-company-soft.jsonl` (strict Recall@10)

Only this run finds: 11 (R004, R025, R053, R078, R097, R130, R135, R146, R161, R171, R181)  
Only the other finds: 24 (R002, R032, R045, R100, R103, R112, R120, R121, R125, R141, R142, R143, R150, R151, R152, R155, R158, R160, R175, R177, R182, R184, R188, R195)  
Ties: 165; exact sign test p = 0.041

## Not found in the top 10 (strict): 74

R002, R006, R009, R010, R013, R021, R022, R023, R028, R029, R032, R038, R042, R045, R050, R055, R061, R062, R063, R064, R068, R071, R073, R075, R076, R079, R083, R088, R090, R098, R100, R103, R105, R107, R112, R115, R116, R117, R118, R120, R121, R122, R125, R127, R136, R137, R141, R142, R143, R144, R145, R150, R151, R152, R155, R156, R158, R159, R160, R163, R164, R166, R170, R172, R173, R175, R177, R179, R182, R184, R188, R195, R199, R200
