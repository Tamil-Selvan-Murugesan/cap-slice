# Retrieval score: `dense-nemotron-3-embed-8b-bf16-2048-company.jsonl`

200 questions; missing from run: 0. Strict = answer pages checked on the image; lenient adds machine-found pages that print the answer's numbers. doc@10 = the right document anywhere in the top 10.

| group | n | strict_R@1 | strict_R@5 | strict_R@10 | strict_R@20 | strict_MRR@10 | lenient_R@10 | doc@10 |
|---|---|---|---|---|---|---|---|---|
| all | 200 | 0.34 | 0.54 | 0.63 | 0.72 | 0.43 | 0.66 | 0.88 |
| company:APARINDS | 64 | 0.39 | 0.55 | 0.64 | 0.75 | 0.48 | 0.67 | 0.84 |
| company:HEROMOTOCO | 54 | 0.43 | 0.61 | 0.70 | 0.74 | 0.51 | 0.74 | 0.93 |
| company:E2E | 43 | 0.12 | 0.33 | 0.42 | 0.56 | 0.20 | 0.44 | 0.79 |
| company:ESCONET | 21 | 0.24 | 0.57 | 0.71 | 0.81 | 0.38 | 0.76 | 1.00 |
| company:C2C | 18 | 0.50 | 0.78 | 0.78 | 0.89 | 0.62 | 0.78 | 0.94 |
| doctype:annual_reports | 111 | 0.35 | 0.54 | 0.62 | 0.71 | 0.44 | 0.68 | 0.94 |
| doctype:investor_presentations | 47 | 0.34 | 0.55 | 0.68 | 0.77 | 0.44 | 0.68 | 0.81 |
| doctype:concall_transcripts | 38 | 0.29 | 0.47 | 0.55 | 0.68 | 0.37 | 0.55 | 0.79 |
| doctype:periodic_results | 4 | 0.25 | 1.00 | 1.00 | 1.00 | 0.54 | 1.00 | 1.00 |
| evidence:table | 63 | 0.38 | 0.60 | 0.70 | 0.79 | 0.49 | 0.76 | 0.94 |
| evidence:concall | 33 | 0.33 | 0.52 | 0.61 | 0.73 | 0.42 | 0.61 | 0.79 |
| evidence:prose | 33 | 0.30 | 0.55 | 0.64 | 0.76 | 0.41 | 0.64 | 0.94 |
| evidence:statement | 25 | 0.24 | 0.44 | 0.56 | 0.64 | 0.32 | 0.60 | 0.88 |
| evidence:chart | 15 | 0.47 | 0.67 | 0.73 | 0.80 | 0.53 | 0.80 | 0.87 |
| evidence:multi | 15 | 0.00 | 0.07 | 0.20 | 0.33 | 0.04 | 0.20 | 0.80 |
| evidence:scan | 10 | 0.60 | 0.90 | 0.90 | 0.90 | 0.72 | 0.90 | 0.90 |
| evidence:kpi | 6 | 0.50 | 0.67 | 0.67 | 0.67 | 0.58 | 0.67 | 0.67 |
| hard:decoy_years | 63 | 0.35 | 0.49 | 0.59 | 0.68 | 0.42 | 0.65 | 0.90 |
| hard:standalone_vs_consolidated | 22 | 0.27 | 0.36 | 0.45 | 0.55 | 0.32 | 0.55 | 1.00 |
| hard:cross_doc | 17 | 0.00 | 0.06 | 0.18 | 0.35 | 0.03 | 0.18 | 0.71 |
| hard:spoken_numbers | 16 | 0.19 | 0.31 | 0.38 | 0.62 | 0.24 | 0.38 | 0.75 |
| hard:chart_labels | 14 | 0.43 | 0.64 | 0.71 | 0.79 | 0.49 | 0.79 | 0.86 |
| hard:indian_grouping | 14 | 0.29 | 0.71 | 0.79 | 0.86 | 0.42 | 0.86 | 1.00 |
| hard:multi_hop | 14 | 0.00 | 0.07 | 0.14 | 0.29 | 0.03 | 0.14 | 0.79 |
| hard:slide_table | 13 | 0.38 | 0.62 | 0.69 | 0.77 | 0.48 | 0.69 | 0.77 |
| hard:lakhs_unit | 11 | 0.18 | 0.64 | 0.73 | 0.91 | 0.38 | 0.73 | 0.82 |
| hard:footnote | 10 | 0.10 | 0.60 | 0.70 | 0.80 | 0.29 | 0.70 | 0.80 |
| hard:image_only_page | 10 | 0.60 | 0.90 | 0.90 | 0.90 | 0.72 | 0.90 | 0.90 |
| hard:no_numbers | 10 | 0.30 | 0.50 | 0.70 | 0.70 | 0.41 | 0.70 | 0.80 |
| hard:period_format | 10 | 0.30 | 0.60 | 0.60 | 0.60 | 0.43 | 0.60 | 0.70 |
| style:paraphrase | 140 | 0.36 | 0.59 | 0.66 | 0.76 | 0.46 | 0.69 | 0.87 |
| style:exact | 25 | 0.36 | 0.56 | 0.68 | 0.80 | 0.46 | 0.76 | 0.96 |
| style:vague | 20 | 0.35 | 0.55 | 0.65 | 0.70 | 0.42 | 0.65 | 0.90 |
| style:analytical | 15 | 0.00 | 0.07 | 0.20 | 0.33 | 0.04 | 0.20 | 0.80 |

## Paired comparison vs `dense-voyage-4-large-2048-company.jsonl` (strict Recall@10)

Only this run finds: 17 (R022, R025, R053, R061, R066, R069, R078, R086, R087, R097, R098, R099, R135, R164, R170, R171, R181)  
Only the other finds: 25 (R002, R008, R030, R032, R037, R045, R054, R103, R119, R120, R121, R125, R142, R143, R147, R150, R151, R152, R153, R154, R158, R160, R168, R185, R195)  
Ties: 158; exact sign test p = 0.280

## Not found in the top 10 (strict): 74

R002, R004, R006, R008, R009, R010, R013, R021, R023, R028, R029, R030, R032, R037, R038, R042, R045, R050, R054, R055, R062, R063, R064, R068, R071, R073, R075, R076, R079, R083, R088, R090, R103, R105, R107, R115, R116, R117, R118, R119, R120, R121, R122, R125, R127, R130, R136, R137, R142, R143, R144, R145, R146, R147, R150, R151, R152, R153, R154, R156, R158, R159, R160, R161, R163, R166, R168, R172, R173, R179, R185, R195, R199, R200
