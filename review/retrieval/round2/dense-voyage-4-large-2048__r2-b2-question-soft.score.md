# Retrieval score: `dense-voyage-4-large-2048__r2-b2-question-soft.jsonl`

200 questions; missing from run: 0. Strict = answer pages checked on the image; lenient adds machine-found pages that print the answer's numbers. doc@10 = the right document anywhere in the top 10.

| group | n | strict_R@1 | strict_R@5 | strict_R@10 | strict_R@20 | strict_MRR@10 | lenient_R@10 | doc@10 |
|---|---|---|---|---|---|---|---|---|
| all | 200 | 0.51 | 0.82 | 0.86 | 0.91 | 0.64 | 0.88 | 0.96 |
| company:APARINDS | 64 | 0.53 | 0.84 | 0.86 | 0.92 | 0.66 | 0.88 | 0.91 |
| company:HEROMOTOCO | 54 | 0.44 | 0.78 | 0.85 | 0.87 | 0.60 | 0.89 | 0.98 |
| company:E2E | 43 | 0.40 | 0.81 | 0.91 | 0.93 | 0.56 | 0.91 | 1.00 |
| company:ESCONET | 21 | 0.57 | 0.81 | 0.81 | 0.86 | 0.69 | 0.81 | 0.95 |
| company:C2C | 18 | 0.83 | 0.89 | 0.89 | 1.00 | 0.86 | 0.89 | 1.00 |
| doctype:annual_reports | 111 | 0.54 | 0.80 | 0.86 | 0.89 | 0.67 | 0.88 | 0.97 |
| doctype:investor_presentations | 47 | 0.32 | 0.83 | 0.85 | 0.89 | 0.49 | 0.85 | 0.91 |
| doctype:concall_transcripts | 38 | 0.63 | 0.84 | 0.89 | 0.97 | 0.73 | 0.89 | 0.97 |
| doctype:periodic_results | 4 | 0.75 | 1.00 | 1.00 | 1.00 | 0.80 | 1.00 | 1.00 |
| evidence:table | 63 | 0.56 | 0.94 | 0.95 | 0.98 | 0.71 | 0.97 | 0.97 |
| evidence:concall | 33 | 0.73 | 0.94 | 0.94 | 0.97 | 0.82 | 0.94 | 0.97 |
| evidence:prose | 33 | 0.42 | 0.73 | 0.85 | 0.88 | 0.58 | 0.85 | 0.97 |
| evidence:statement | 25 | 0.56 | 0.92 | 0.92 | 0.96 | 0.69 | 0.96 | 0.96 |
| evidence:chart | 15 | 0.53 | 0.80 | 0.80 | 0.80 | 0.63 | 0.87 | 0.93 |
| evidence:multi | 15 | 0.00 | 0.13 | 0.33 | 0.53 | 0.09 | 0.33 | 1.00 |
| evidence:scan | 10 | 0.60 | 0.80 | 0.90 | 1.00 | 0.70 | 0.90 | 0.90 |
| evidence:kpi | 6 | 0.17 | 0.83 | 0.83 | 0.83 | 0.45 | 0.83 | 0.83 |
| hard:decoy_years | 63 | 0.57 | 0.87 | 0.89 | 0.94 | 0.70 | 0.92 | 0.94 |
| hard:standalone_vs_consolidated | 22 | 0.45 | 0.82 | 0.86 | 0.91 | 0.62 | 0.91 | 1.00 |
| hard:cross_doc | 17 | 0.06 | 0.24 | 0.41 | 0.65 | 0.17 | 0.41 | 0.94 |
| hard:spoken_numbers | 16 | 0.75 | 0.88 | 0.88 | 0.94 | 0.80 | 0.88 | 0.94 |
| hard:chart_labels | 14 | 0.50 | 0.79 | 0.79 | 0.79 | 0.60 | 0.86 | 0.93 |
| hard:indian_grouping | 14 | 0.50 | 0.93 | 0.93 | 0.93 | 0.62 | 0.93 | 0.93 |
| hard:multi_hop | 14 | 0.00 | 0.07 | 0.29 | 0.50 | 0.06 | 0.29 | 1.00 |
| hard:slide_table | 13 | 0.31 | 1.00 | 1.00 | 1.00 | 0.53 | 1.00 | 1.00 |
| hard:lakhs_unit | 11 | 0.55 | 0.82 | 1.00 | 1.00 | 0.68 | 1.00 | 1.00 |
| hard:footnote | 10 | 0.30 | 0.80 | 0.90 | 0.90 | 0.49 | 0.90 | 1.00 |
| hard:image_only_page | 10 | 0.60 | 0.80 | 0.90 | 1.00 | 0.70 | 0.90 | 0.90 |
| hard:no_numbers | 10 | 0.60 | 0.90 | 0.90 | 1.00 | 0.73 | 0.90 | 1.00 |
| hard:period_format | 10 | 0.50 | 0.90 | 0.90 | 0.90 | 0.65 | 0.90 | 0.90 |
| style:paraphrase | 140 | 0.55 | 0.88 | 0.91 | 0.94 | 0.69 | 0.92 | 0.95 |
| style:exact | 25 | 0.56 | 0.88 | 0.88 | 0.96 | 0.68 | 0.92 | 0.96 |
| style:vague | 20 | 0.55 | 0.85 | 0.95 | 0.95 | 0.70 | 0.95 | 1.00 |
| style:analytical | 15 | 0.00 | 0.13 | 0.33 | 0.53 | 0.09 | 0.33 | 1.00 |

## Paired comparison vs `dense-voyage-4-large-2048-question-soft.jsonl` (strict Recall@10)

Only this run finds: 13 (R021, R063, R071, R073, R079, R105, R107, R116, R122, R144, R157, R161, R163)  
Only the other finds: 1 (R088)  
Ties: 186; exact sign test p = 0.002

## Not found in the top 10 (strict): 27

R013, R023, R028, R029, R030, R050, R061, R062, R064, R068, R076, R083, R088, R098, R115, R117, R118, R145, R156, R159, R160, R172, R173, R179, R182, R199, R200
