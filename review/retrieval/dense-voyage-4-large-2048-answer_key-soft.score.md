# Retrieval score: `dense-voyage-4-large-2048-answer_key-soft.jsonl`

200 questions; missing from run: 0. Strict = answer pages checked on the image; lenient adds machine-found pages that print the answer's numbers. doc@10 = the right document anywhere in the top 10.

| group | n | strict_R@1 | strict_R@5 | strict_R@10 | strict_R@20 | strict_MRR@10 | lenient_R@10 | doc@10 |
|---|---|---|---|---|---|---|---|---|
| all | 200 | 0.48 | 0.81 | 0.86 | 0.90 | 0.62 | 0.88 | 0.98 |
| company:APARINDS | 64 | 0.47 | 0.84 | 0.92 | 0.94 | 0.63 | 0.92 | 0.97 |
| company:HEROMOTOCO | 54 | 0.48 | 0.76 | 0.80 | 0.81 | 0.59 | 0.83 | 1.00 |
| company:E2E | 43 | 0.47 | 0.84 | 0.84 | 0.93 | 0.62 | 0.86 | 0.98 |
| company:ESCONET | 21 | 0.57 | 0.76 | 0.86 | 0.90 | 0.64 | 0.86 | 1.00 |
| company:C2C | 18 | 0.50 | 0.89 | 0.89 | 0.89 | 0.66 | 0.89 | 1.00 |
| doctype:annual_reports | 111 | 0.46 | 0.80 | 0.85 | 0.89 | 0.60 | 0.87 | 1.00 |
| doctype:investor_presentations | 47 | 0.51 | 0.87 | 0.89 | 0.89 | 0.65 | 0.89 | 0.96 |
| doctype:concall_transcripts | 38 | 0.50 | 0.76 | 0.84 | 0.89 | 0.61 | 0.84 | 0.97 |
| doctype:periodic_results | 4 | 0.75 | 1.00 | 1.00 | 1.00 | 0.88 | 1.00 | 1.00 |
| evidence:table | 63 | 0.46 | 0.97 | 0.98 | 1.00 | 0.65 | 1.00 | 1.00 |
| evidence:concall | 33 | 0.58 | 0.85 | 0.94 | 0.94 | 0.70 | 0.94 | 0.97 |
| evidence:prose | 33 | 0.55 | 0.76 | 0.79 | 0.88 | 0.64 | 0.79 | 1.00 |
| evidence:statement | 25 | 0.52 | 0.80 | 0.92 | 0.96 | 0.65 | 0.96 | 1.00 |
| evidence:chart | 15 | 0.40 | 0.80 | 0.87 | 0.87 | 0.56 | 0.93 | 0.93 |
| evidence:multi | 15 | 0.07 | 0.13 | 0.13 | 0.27 | 0.08 | 0.13 | 1.00 |
| evidence:scan | 10 | 0.80 | 1.00 | 1.00 | 1.00 | 0.90 | 1.00 | 1.00 |
| evidence:kpi | 6 | 0.50 | 0.83 | 0.83 | 0.83 | 0.64 | 0.83 | 0.83 |
| hard:decoy_years | 63 | 0.44 | 0.86 | 0.92 | 0.94 | 0.61 | 0.95 | 0.98 |
| hard:standalone_vs_consolidated | 22 | 0.27 | 0.64 | 0.77 | 0.82 | 0.42 | 0.82 | 1.00 |
| hard:cross_doc | 17 | 0.12 | 0.29 | 0.29 | 0.41 | 0.18 | 0.29 | 1.00 |
| hard:spoken_numbers | 16 | 0.56 | 0.81 | 0.88 | 0.88 | 0.68 | 0.88 | 0.94 |
| hard:chart_labels | 14 | 0.36 | 0.79 | 0.86 | 0.86 | 0.53 | 0.93 | 0.93 |
| hard:indian_grouping | 14 | 0.29 | 0.93 | 0.93 | 1.00 | 0.52 | 0.93 | 1.00 |
| hard:multi_hop | 14 | 0.00 | 0.07 | 0.07 | 0.21 | 0.01 | 0.07 | 1.00 |
| hard:slide_table | 13 | 0.54 | 1.00 | 1.00 | 1.00 | 0.69 | 1.00 | 1.00 |
| hard:lakhs_unit | 11 | 0.73 | 1.00 | 1.00 | 1.00 | 0.86 | 1.00 | 1.00 |
| hard:footnote | 10 | 0.40 | 0.90 | 0.90 | 0.90 | 0.61 | 0.90 | 1.00 |
| hard:image_only_page | 10 | 0.80 | 1.00 | 1.00 | 1.00 | 0.90 | 1.00 | 1.00 |
| hard:no_numbers | 10 | 0.40 | 0.80 | 0.90 | 0.90 | 0.58 | 0.90 | 1.00 |
| hard:period_format | 10 | 0.60 | 0.80 | 0.90 | 0.90 | 0.70 | 0.90 | 0.90 |
| style:paraphrase | 140 | 0.53 | 0.87 | 0.92 | 0.95 | 0.67 | 0.94 | 0.98 |
| style:exact | 25 | 0.44 | 0.88 | 0.92 | 0.96 | 0.61 | 0.96 | 1.00 |
| style:vague | 20 | 0.55 | 0.85 | 0.90 | 0.90 | 0.68 | 0.90 | 1.00 |
| style:analytical | 15 | 0.07 | 0.13 | 0.13 | 0.27 | 0.08 | 0.13 | 1.00 |

## Paired comparison vs `bm25-mineru_advanced-answer_key-soft.jsonl` (strict Recall@10)

Only this run finds: 34 (R002, R010, R028, R032, R045, R050, R055, R058, R068, R072, R075, R088, R100, R105, R112, R120, R121, R125, R134, R141, R142, R143, R150, R151, R152, R155, R158, R162, R166, R172, R177, R180, R184, R195)  
Only the other finds: 6 (R023, R098, R107, R145, R160, R173)  
Ties: 160; exact sign test p = 0.000

## Not found in the top 10 (strict): 28

R023, R029, R062, R063, R064, R071, R073, R076, R079, R083, R098, R107, R115, R116, R117, R118, R122, R144, R145, R156, R159, R160, R161, R173, R179, R182, R199, R200
