# Retrieval score: `dense-voyage-4-large-2048__r2-c-answer_key.jsonl`

200 questions; missing from run: 0. Strict = answer pages checked on the image; lenient adds machine-found pages that print the answer's numbers. doc@10 = the right document anywhere in the top 10.

| group | n | strict_R@1 | strict_R@5 | strict_R@10 | strict_R@20 | strict_MRR@10 | lenient_R@10 | doc@10 |
|---|---|---|---|---|---|---|---|---|
| all | 200 | 0.46 | 0.74 | 0.81 | 0.86 | 0.58 | 0.83 | 0.99 |
| company:APARINDS | 64 | 0.47 | 0.80 | 0.86 | 0.94 | 0.60 | 0.89 | 0.98 |
| company:HEROMOTOCO | 54 | 0.44 | 0.69 | 0.74 | 0.74 | 0.55 | 0.76 | 1.00 |
| company:E2E | 43 | 0.40 | 0.74 | 0.81 | 0.91 | 0.54 | 0.84 | 0.98 |
| company:ESCONET | 21 | 0.48 | 0.67 | 0.86 | 0.90 | 0.58 | 0.86 | 1.00 |
| company:C2C | 18 | 0.56 | 0.83 | 0.83 | 0.83 | 0.69 | 0.83 | 1.00 |
| doctype:annual_reports | 111 | 0.43 | 0.70 | 0.78 | 0.86 | 0.56 | 0.82 | 1.00 |
| doctype:investor_presentations | 47 | 0.45 | 0.81 | 0.87 | 0.89 | 0.58 | 0.87 | 0.98 |
| doctype:concall_transcripts | 38 | 0.53 | 0.76 | 0.82 | 0.84 | 0.62 | 0.82 | 0.97 |
| doctype:periodic_results | 4 | 0.50 | 1.00 | 1.00 | 1.00 | 0.71 | 1.00 | 1.00 |
| evidence:table | 63 | 0.40 | 0.81 | 0.92 | 1.00 | 0.57 | 0.95 | 1.00 |
| evidence:concall | 33 | 0.61 | 0.88 | 0.94 | 0.94 | 0.71 | 0.94 | 0.97 |
| evidence:prose | 33 | 0.48 | 0.73 | 0.76 | 0.85 | 0.59 | 0.76 | 1.00 |
| evidence:statement | 25 | 0.48 | 0.72 | 0.84 | 0.88 | 0.60 | 0.88 | 1.00 |
| evidence:chart | 15 | 0.47 | 0.80 | 0.87 | 0.87 | 0.61 | 0.93 | 0.93 |
| evidence:multi | 15 | 0.07 | 0.07 | 0.07 | 0.13 | 0.07 | 0.07 | 1.00 |
| evidence:scan | 10 | 0.70 | 0.90 | 0.90 | 0.90 | 0.80 | 0.90 | 1.00 |
| evidence:kpi | 6 | 0.50 | 0.83 | 0.83 | 0.83 | 0.62 | 0.83 | 1.00 |
| hard:decoy_years | 63 | 0.46 | 0.76 | 0.87 | 0.90 | 0.59 | 0.90 | 0.98 |
| hard:standalone_vs_consolidated | 22 | 0.27 | 0.50 | 0.68 | 0.73 | 0.41 | 0.73 | 1.00 |
| hard:cross_doc | 17 | 0.12 | 0.24 | 0.24 | 0.29 | 0.17 | 0.24 | 1.00 |
| hard:spoken_numbers | 16 | 0.62 | 0.81 | 0.88 | 0.88 | 0.71 | 0.88 | 0.94 |
| hard:chart_labels | 14 | 0.43 | 0.79 | 0.86 | 0.86 | 0.58 | 0.93 | 0.93 |
| hard:indian_grouping | 14 | 0.29 | 0.57 | 0.71 | 1.00 | 0.44 | 0.79 | 1.00 |
| hard:multi_hop | 14 | 0.00 | 0.00 | 0.00 | 0.07 | 0.00 | 0.00 | 1.00 |
| hard:slide_table | 13 | 0.31 | 0.85 | 0.92 | 1.00 | 0.50 | 0.92 | 1.00 |
| hard:lakhs_unit | 11 | 0.73 | 1.00 | 1.00 | 1.00 | 0.85 | 1.00 | 1.00 |
| hard:footnote | 10 | 0.30 | 0.70 | 0.80 | 0.80 | 0.45 | 0.80 | 1.00 |
| hard:image_only_page | 10 | 0.70 | 0.90 | 0.90 | 0.90 | 0.80 | 0.90 | 1.00 |
| hard:no_numbers | 10 | 0.40 | 0.80 | 0.90 | 0.90 | 0.58 | 0.90 | 1.00 |
| hard:period_format | 10 | 0.40 | 0.70 | 0.80 | 0.90 | 0.53 | 0.80 | 1.00 |
| style:paraphrase | 140 | 0.49 | 0.79 | 0.88 | 0.94 | 0.62 | 0.90 | 0.99 |
| style:exact | 25 | 0.48 | 0.84 | 0.88 | 0.92 | 0.63 | 0.92 | 1.00 |
| style:vague | 20 | 0.45 | 0.80 | 0.85 | 0.85 | 0.59 | 0.85 | 1.00 |
| style:analytical | 15 | 0.07 | 0.07 | 0.07 | 0.13 | 0.07 | 0.07 | 1.00 |

## Paired comparison vs `dense-voyage-4-large-2048-answer_key.jsonl` (strict Recall@10)

Only this run finds: 4 (R078, R087, R088, R099)  
Only the other finds: 8 (R013, R021, R036, R041, R065, R080, R112, R141)  
Ties: 188; exact sign test p = 0.388

## Not found in the top 10 (strict): 37

R013, R021, R023, R029, R036, R041, R062, R063, R064, R065, R071, R073, R076, R079, R080, R083, R098, R107, R112, R115, R116, R117, R118, R122, R141, R144, R145, R156, R159, R160, R161, R173, R179, R182, R198, R199, R200
