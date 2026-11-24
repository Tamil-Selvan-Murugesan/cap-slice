# Retrieval score: `dense-voyage-4-large-2048__r2-d-company.jsonl`

200 questions; missing from run: 0. Strict = answer pages checked on the image; lenient adds machine-found pages that print the answer's numbers. doc@10 = the right document anywhere in the top 10.

| group | n | strict_R@1 | strict_R@5 | strict_R@10 | strict_R@20 | strict_MRR@10 | lenient_R@10 | doc@10 |
|---|---|---|---|---|---|---|---|---|
| all | 200 | 0.29 | 0.58 | 0.68 | 0.77 | 0.42 | 0.72 | 0.86 |
| company:APARINDS | 64 | 0.22 | 0.58 | 0.67 | 0.78 | 0.38 | 0.70 | 0.80 |
| company:HEROMOTOCO | 54 | 0.33 | 0.61 | 0.69 | 0.69 | 0.45 | 0.74 | 0.94 |
| company:E2E | 43 | 0.26 | 0.49 | 0.60 | 0.77 | 0.36 | 0.65 | 0.84 |
| company:ESCONET | 21 | 0.38 | 0.52 | 0.62 | 0.81 | 0.44 | 0.71 | 0.76 |
| company:C2C | 18 | 0.44 | 0.83 | 0.89 | 0.94 | 0.62 | 0.89 | 1.00 |
| doctype:annual_reports | 111 | 0.32 | 0.62 | 0.68 | 0.75 | 0.45 | 0.76 | 0.92 |
| doctype:investor_presentations | 47 | 0.23 | 0.47 | 0.60 | 0.79 | 0.33 | 0.62 | 0.74 |
| doctype:concall_transcripts | 38 | 0.24 | 0.58 | 0.71 | 0.79 | 0.40 | 0.71 | 0.82 |
| doctype:periodic_results | 4 | 0.75 | 1.00 | 1.00 | 1.00 | 0.88 | 1.00 | 1.00 |
| evidence:table | 63 | 0.33 | 0.65 | 0.70 | 0.83 | 0.47 | 0.79 | 0.87 |
| evidence:concall | 33 | 0.27 | 0.67 | 0.76 | 0.82 | 0.45 | 0.76 | 0.85 |
| evidence:prose | 33 | 0.24 | 0.52 | 0.58 | 0.70 | 0.37 | 0.58 | 0.85 |
| evidence:statement | 25 | 0.32 | 0.60 | 0.72 | 0.80 | 0.44 | 0.80 | 0.88 |
| evidence:chart | 15 | 0.33 | 0.67 | 0.80 | 0.80 | 0.45 | 0.87 | 0.87 |
| evidence:multi | 15 | 0.00 | 0.07 | 0.27 | 0.40 | 0.05 | 0.27 | 0.73 |
| evidence:scan | 10 | 0.60 | 0.60 | 0.80 | 0.90 | 0.63 | 0.80 | 1.00 |
| evidence:kpi | 6 | 0.33 | 0.83 | 0.83 | 0.83 | 0.51 | 0.83 | 0.83 |
| hard:decoy_years | 63 | 0.33 | 0.67 | 0.73 | 0.83 | 0.47 | 0.83 | 0.92 |
| hard:standalone_vs_consolidated | 22 | 0.27 | 0.45 | 0.55 | 0.68 | 0.36 | 0.68 | 0.91 |
| hard:cross_doc | 17 | 0.00 | 0.18 | 0.41 | 0.53 | 0.10 | 0.41 | 0.76 |
| hard:spoken_numbers | 16 | 0.19 | 0.56 | 0.69 | 0.75 | 0.36 | 0.69 | 0.81 |
| hard:chart_labels | 14 | 0.29 | 0.64 | 0.79 | 0.79 | 0.41 | 0.86 | 0.86 |
| hard:indian_grouping | 14 | 0.29 | 0.79 | 0.79 | 0.86 | 0.50 | 0.93 | 0.93 |
| hard:multi_hop | 14 | 0.00 | 0.07 | 0.29 | 0.36 | 0.05 | 0.29 | 0.79 |
| hard:slide_table | 13 | 0.23 | 0.31 | 0.46 | 0.69 | 0.27 | 0.54 | 0.54 |
| hard:lakhs_unit | 11 | 0.45 | 0.91 | 0.91 | 1.00 | 0.62 | 0.91 | 0.91 |
| hard:footnote | 10 | 0.20 | 0.50 | 0.50 | 0.70 | 0.32 | 0.50 | 0.80 |
| hard:image_only_page | 10 | 0.60 | 0.60 | 0.80 | 0.90 | 0.63 | 0.80 | 1.00 |
| hard:no_numbers | 10 | 0.40 | 0.60 | 0.70 | 0.70 | 0.51 | 0.70 | 0.90 |
| hard:period_format | 10 | 0.20 | 0.50 | 0.60 | 0.80 | 0.32 | 0.60 | 0.70 |
| style:paraphrase | 140 | 0.29 | 0.63 | 0.71 | 0.82 | 0.44 | 0.76 | 0.86 |
| style:exact | 25 | 0.44 | 0.68 | 0.68 | 0.76 | 0.54 | 0.80 | 0.92 |
| style:vague | 20 | 0.35 | 0.55 | 0.70 | 0.70 | 0.47 | 0.70 | 0.85 |
| style:analytical | 15 | 0.00 | 0.07 | 0.27 | 0.40 | 0.05 | 0.27 | 0.73 |

## Paired comparison vs `dense-voyage-4-large-2048-company.jsonl` (strict Recall@10)

Only this run finds: 12 (R025, R050, R053, R066, R069, R086, R087, R090, R099, R105, R161, R164)  
Only the other finds: 11 (R027, R048, R058, R059, R080, R120, R133, R138, R150, R151, R152)  
Ties: 177; exact sign test p = 1.000

## Not found in the top 10 (strict): 65

R004, R006, R009, R010, R013, R021, R022, R023, R027, R028, R029, R038, R042, R048, R055, R058, R059, R061, R062, R063, R064, R068, R071, R073, R075, R076, R078, R079, R080, R083, R088, R097, R098, R107, R115, R116, R117, R118, R120, R122, R127, R130, R133, R135, R136, R137, R138, R144, R145, R146, R150, R151, R152, R156, R159, R163, R166, R170, R171, R172, R173, R179, R181, R199, R200
