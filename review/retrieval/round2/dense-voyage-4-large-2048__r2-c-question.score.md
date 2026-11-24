# Retrieval score: `dense-voyage-4-large-2048__r2-c-question.jsonl`

200 questions; missing from run: 0. Strict = answer pages checked on the image; lenient adds machine-found pages that print the answer's numbers. doc@10 = the right document anywhere in the top 10.

| group | n | strict_R@1 | strict_R@5 | strict_R@10 | strict_R@20 | strict_MRR@10 | lenient_R@10 | doc@10 |
|---|---|---|---|---|---|---|---|---|
| all | 200 | 0.39 | 0.65 | 0.74 | 0.81 | 0.50 | 0.77 | 0.92 |
| company:APARINDS | 64 | 0.41 | 0.66 | 0.73 | 0.84 | 0.51 | 0.75 | 0.88 |
| company:HEROMOTOCO | 54 | 0.41 | 0.63 | 0.70 | 0.72 | 0.51 | 0.72 | 0.94 |
| company:E2E | 43 | 0.26 | 0.58 | 0.74 | 0.84 | 0.40 | 0.79 | 0.93 |
| company:ESCONET | 21 | 0.38 | 0.62 | 0.71 | 0.81 | 0.48 | 0.76 | 0.90 |
| company:C2C | 18 | 0.56 | 0.89 | 0.89 | 0.94 | 0.68 | 0.89 | 1.00 |
| doctype:annual_reports | 111 | 0.40 | 0.64 | 0.73 | 0.78 | 0.51 | 0.77 | 0.94 |
| doctype:investor_presentations | 47 | 0.28 | 0.60 | 0.70 | 0.81 | 0.40 | 0.72 | 0.85 |
| doctype:concall_transcripts | 38 | 0.47 | 0.71 | 0.79 | 0.89 | 0.57 | 0.79 | 0.95 |
| doctype:periodic_results | 4 | 0.50 | 1.00 | 1.00 | 1.00 | 0.67 | 1.00 | 1.00 |
| evidence:table | 63 | 0.33 | 0.65 | 0.81 | 0.92 | 0.48 | 0.84 | 0.95 |
| evidence:concall | 33 | 0.55 | 0.79 | 0.88 | 0.91 | 0.64 | 0.88 | 0.94 |
| evidence:prose | 33 | 0.42 | 0.70 | 0.73 | 0.76 | 0.54 | 0.73 | 0.91 |
| evidence:statement | 25 | 0.40 | 0.64 | 0.72 | 0.76 | 0.51 | 0.76 | 0.88 |
| evidence:chart | 15 | 0.47 | 0.73 | 0.80 | 0.87 | 0.59 | 0.87 | 0.93 |
| evidence:multi | 15 | 0.00 | 0.13 | 0.20 | 0.40 | 0.05 | 0.20 | 1.00 |
| evidence:scan | 10 | 0.50 | 0.70 | 0.70 | 0.80 | 0.58 | 0.80 | 0.80 |
| evidence:kpi | 6 | 0.33 | 0.67 | 0.67 | 0.67 | 0.50 | 0.67 | 0.67 |
| hard:decoy_years | 63 | 0.40 | 0.63 | 0.78 | 0.84 | 0.52 | 0.81 | 0.90 |
| hard:standalone_vs_consolidated | 22 | 0.27 | 0.50 | 0.64 | 0.68 | 0.40 | 0.68 | 0.95 |
| hard:cross_doc | 17 | 0.00 | 0.18 | 0.29 | 0.47 | 0.09 | 0.29 | 0.94 |
| hard:spoken_numbers | 16 | 0.56 | 0.69 | 0.75 | 0.81 | 0.61 | 0.75 | 0.88 |
| hard:chart_labels | 14 | 0.43 | 0.71 | 0.79 | 0.86 | 0.57 | 0.86 | 0.93 |
| hard:indian_grouping | 14 | 0.21 | 0.57 | 0.64 | 0.86 | 0.37 | 0.71 | 0.93 |
| hard:multi_hop | 14 | 0.00 | 0.07 | 0.14 | 0.36 | 0.03 | 0.14 | 1.00 |
| hard:slide_table | 13 | 0.15 | 0.54 | 0.62 | 0.77 | 0.27 | 0.69 | 0.85 |
| hard:lakhs_unit | 11 | 0.64 | 0.82 | 0.82 | 0.82 | 0.71 | 0.91 | 0.82 |
| hard:footnote | 10 | 0.30 | 0.60 | 0.70 | 0.80 | 0.42 | 0.70 | 0.90 |
| hard:image_only_page | 10 | 0.50 | 0.70 | 0.70 | 0.80 | 0.58 | 0.80 | 0.80 |
| hard:no_numbers | 10 | 0.40 | 0.70 | 0.90 | 0.90 | 0.55 | 0.90 | 1.00 |
| hard:period_format | 10 | 0.30 | 0.70 | 0.80 | 0.80 | 0.45 | 0.80 | 0.90 |
| style:paraphrase | 140 | 0.41 | 0.70 | 0.79 | 0.84 | 0.53 | 0.81 | 0.91 |
| style:exact | 25 | 0.44 | 0.68 | 0.76 | 0.88 | 0.56 | 0.80 | 0.92 |
| style:vague | 20 | 0.45 | 0.65 | 0.80 | 0.85 | 0.56 | 0.80 | 0.95 |
| style:analytical | 15 | 0.00 | 0.13 | 0.20 | 0.40 | 0.05 | 0.20 | 1.00 |

## Paired comparison vs `dense-voyage-4-large-2048-question.jsonl` (strict Recall@10)

Only this run finds: 6 (R069, R078, R087, R088, R099, R116)  
Only the other finds: 13 (R022, R025, R034, R036, R041, R065, R080, R090, R112, R127, R137, R141, R170)  
Ties: 181; exact sign test p = 0.167

## Not found in the top 10 (strict): 52

R013, R021, R022, R023, R025, R028, R029, R030, R034, R036, R040, R041, R050, R061, R062, R063, R064, R065, R068, R071, R073, R076, R079, R080, R083, R090, R098, R105, R107, R112, R115, R117, R118, R122, R127, R137, R141, R144, R145, R156, R157, R159, R160, R161, R163, R170, R172, R173, R179, R182, R199, R200
