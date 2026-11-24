# Retrieval score: `dense-voyage-4-large-2048__r2-b2-question_next-soft.jsonl`

200 questions; missing from run: 0. Strict = answer pages checked on the image; lenient adds machine-found pages that print the answer's numbers. doc@10 = the right document anywhere in the top 10.

| group | n | strict_R@1 | strict_R@5 | strict_R@10 | strict_R@20 | strict_MRR@10 | lenient_R@10 | doc@10 |
|---|---|---|---|---|---|---|---|---|
| all | 200 | 0.49 | 0.81 | 0.86 | 0.92 | 0.62 | 0.88 | 0.97 |
| company:APARINDS | 64 | 0.50 | 0.83 | 0.86 | 0.92 | 0.63 | 0.88 | 0.92 |
| company:HEROMOTOCO | 54 | 0.44 | 0.76 | 0.85 | 0.91 | 0.59 | 0.89 | 1.00 |
| company:E2E | 43 | 0.40 | 0.84 | 0.91 | 0.93 | 0.55 | 0.91 | 1.00 |
| company:ESCONET | 21 | 0.48 | 0.81 | 0.81 | 0.86 | 0.60 | 0.81 | 0.95 |
| company:C2C | 18 | 0.83 | 0.89 | 0.89 | 1.00 | 0.86 | 0.89 | 1.00 |
| doctype:annual_reports | 111 | 0.53 | 0.80 | 0.86 | 0.91 | 0.65 | 0.89 | 0.98 |
| doctype:investor_presentations | 47 | 0.30 | 0.81 | 0.85 | 0.91 | 0.48 | 0.85 | 0.94 |
| doctype:concall_transcripts | 38 | 0.58 | 0.84 | 0.87 | 0.95 | 0.70 | 0.87 | 0.97 |
| doctype:periodic_results | 4 | 0.75 | 1.00 | 1.00 | 1.00 | 0.80 | 1.00 | 1.00 |
| evidence:table | 63 | 0.51 | 0.92 | 0.97 | 0.98 | 0.66 | 0.98 | 0.98 |
| evidence:concall | 33 | 0.67 | 0.94 | 0.94 | 0.94 | 0.78 | 0.94 | 0.97 |
| evidence:prose | 33 | 0.42 | 0.73 | 0.85 | 0.88 | 0.56 | 0.85 | 0.97 |
| evidence:statement | 25 | 0.56 | 0.92 | 0.96 | 1.00 | 0.69 | 1.00 | 1.00 |
| evidence:chart | 15 | 0.53 | 0.80 | 0.80 | 0.80 | 0.62 | 0.87 | 0.93 |
| evidence:multi | 15 | 0.00 | 0.13 | 0.20 | 0.67 | 0.07 | 0.20 | 1.00 |
| evidence:scan | 10 | 0.70 | 0.90 | 0.90 | 1.00 | 0.78 | 0.90 | 0.90 |
| evidence:kpi | 6 | 0.17 | 0.67 | 0.83 | 0.83 | 0.40 | 0.83 | 0.83 |
| hard:decoy_years | 63 | 0.56 | 0.86 | 0.92 | 0.95 | 0.68 | 0.95 | 0.97 |
| hard:standalone_vs_consolidated | 22 | 0.45 | 0.82 | 0.86 | 0.95 | 0.59 | 0.91 | 1.00 |
| hard:cross_doc | 17 | 0.06 | 0.29 | 0.35 | 0.71 | 0.18 | 0.35 | 1.00 |
| hard:spoken_numbers | 16 | 0.62 | 0.88 | 0.88 | 0.88 | 0.73 | 0.88 | 0.94 |
| hard:chart_labels | 14 | 0.50 | 0.79 | 0.79 | 0.79 | 0.60 | 0.86 | 0.93 |
| hard:indian_grouping | 14 | 0.50 | 0.86 | 0.93 | 0.93 | 0.61 | 0.93 | 0.93 |
| hard:multi_hop | 14 | 0.00 | 0.07 | 0.14 | 0.64 | 0.04 | 0.14 | 1.00 |
| hard:slide_table | 13 | 0.31 | 0.92 | 1.00 | 1.00 | 0.53 | 1.00 | 1.00 |
| hard:lakhs_unit | 11 | 0.55 | 0.91 | 1.00 | 1.00 | 0.69 | 1.00 | 1.00 |
| hard:footnote | 10 | 0.20 | 0.80 | 0.90 | 0.90 | 0.40 | 0.90 | 1.00 |
| hard:image_only_page | 10 | 0.70 | 0.90 | 0.90 | 1.00 | 0.78 | 0.90 | 0.90 |
| hard:no_numbers | 10 | 0.60 | 0.90 | 0.90 | 1.00 | 0.73 | 0.90 | 1.00 |
| hard:period_format | 10 | 0.30 | 0.80 | 0.90 | 0.90 | 0.52 | 0.90 | 0.90 |
| style:paraphrase | 140 | 0.52 | 0.89 | 0.92 | 0.94 | 0.66 | 0.94 | 0.96 |
| style:exact | 25 | 0.56 | 0.80 | 0.88 | 0.96 | 0.65 | 0.92 | 0.96 |
| style:vague | 20 | 0.55 | 0.85 | 0.95 | 0.95 | 0.70 | 0.95 | 1.00 |
| style:analytical | 15 | 0.00 | 0.13 | 0.20 | 0.67 | 0.07 | 0.20 | 1.00 |

## Paired comparison vs `dense-voyage-4-large-2048-question_next-soft.jsonl` (strict Recall@10)

Only this run finds: 19 (R004, R021, R022, R068, R071, R073, R079, R090, R105, R107, R122, R127, R136, R144, R161, R163, R170, R171, R181)  
Only the other finds: 1 (R160)  
Ties: 180; exact sign test p = 0.000

## Not found in the top 10 (strict): 27

R013, R023, R028, R029, R050, R061, R062, R063, R064, R076, R083, R088, R098, R115, R116, R117, R118, R145, R156, R159, R160, R172, R173, R179, R182, R199, R200
