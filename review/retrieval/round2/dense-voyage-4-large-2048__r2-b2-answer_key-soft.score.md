# Retrieval score: `dense-voyage-4-large-2048__r2-b2-answer_key-soft.jsonl`

200 questions; missing from run: 0. Strict = answer pages checked on the image; lenient adds machine-found pages that print the answer's numbers. doc@10 = the right document anywhere in the top 10.

| group | n | strict_R@1 | strict_R@5 | strict_R@10 | strict_R@20 | strict_MRR@10 | lenient_R@10 | doc@10 |
|---|---|---|---|---|---|---|---|---|
| all | 200 | 0.61 | 0.86 | 0.91 | 0.93 | 0.72 | 0.92 | 0.99 |
| company:APARINDS | 64 | 0.61 | 0.91 | 0.94 | 0.95 | 0.74 | 0.94 | 0.98 |
| company:HEROMOTOCO | 54 | 0.56 | 0.81 | 0.87 | 0.87 | 0.68 | 0.91 | 1.00 |
| company:E2E | 43 | 0.56 | 0.88 | 0.93 | 0.95 | 0.68 | 0.93 | 1.00 |
| company:ESCONET | 21 | 0.67 | 0.86 | 0.90 | 0.95 | 0.76 | 0.90 | 1.00 |
| company:C2C | 18 | 0.83 | 0.83 | 0.89 | 0.89 | 0.84 | 0.89 | 1.00 |
| doctype:annual_reports | 111 | 0.61 | 0.86 | 0.92 | 0.92 | 0.73 | 0.94 | 1.00 |
| doctype:investor_presentations | 47 | 0.53 | 0.87 | 0.87 | 0.91 | 0.67 | 0.87 | 0.98 |
| doctype:concall_transcripts | 38 | 0.66 | 0.87 | 0.92 | 0.95 | 0.76 | 0.92 | 1.00 |
| doctype:periodic_results | 4 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| evidence:table | 63 | 0.62 | 0.97 | 0.98 | 0.98 | 0.78 | 1.00 | 1.00 |
| evidence:concall | 33 | 0.76 | 1.00 | 1.00 | 1.00 | 0.86 | 1.00 | 1.00 |
| evidence:prose | 33 | 0.55 | 0.82 | 0.97 | 0.97 | 0.68 | 0.97 | 1.00 |
| evidence:statement | 25 | 0.72 | 0.96 | 1.00 | 1.00 | 0.82 | 1.00 | 1.00 |
| evidence:chart | 15 | 0.53 | 0.80 | 0.80 | 0.87 | 0.63 | 0.87 | 0.93 |
| evidence:multi | 15 | 0.07 | 0.07 | 0.20 | 0.27 | 0.09 | 0.20 | 1.00 |
| evidence:scan | 10 | 0.90 | 1.00 | 1.00 | 1.00 | 0.95 | 1.00 | 1.00 |
| evidence:kpi | 6 | 0.67 | 0.83 | 0.83 | 1.00 | 0.75 | 0.83 | 1.00 |
| hard:decoy_years | 63 | 0.67 | 0.92 | 0.95 | 0.95 | 0.78 | 0.97 | 0.98 |
| hard:standalone_vs_consolidated | 22 | 0.50 | 0.82 | 0.91 | 0.91 | 0.65 | 0.91 | 1.00 |
| hard:cross_doc | 17 | 0.24 | 0.24 | 0.35 | 0.41 | 0.25 | 0.35 | 1.00 |
| hard:spoken_numbers | 16 | 0.69 | 1.00 | 1.00 | 1.00 | 0.82 | 1.00 | 1.00 |
| hard:chart_labels | 14 | 0.50 | 0.79 | 0.79 | 0.86 | 0.60 | 0.86 | 0.93 |
| hard:indian_grouping | 14 | 0.57 | 0.93 | 1.00 | 1.00 | 0.70 | 1.00 | 1.00 |
| hard:multi_hop | 14 | 0.00 | 0.00 | 0.14 | 0.21 | 0.02 | 0.14 | 1.00 |
| hard:slide_table | 13 | 0.46 | 1.00 | 1.00 | 1.00 | 0.69 | 1.00 | 1.00 |
| hard:lakhs_unit | 11 | 0.82 | 0.91 | 1.00 | 1.00 | 0.88 | 1.00 | 1.00 |
| hard:footnote | 10 | 0.40 | 0.90 | 1.00 | 1.00 | 0.59 | 1.00 | 1.00 |
| hard:image_only_page | 10 | 0.90 | 1.00 | 1.00 | 1.00 | 0.95 | 1.00 | 1.00 |
| hard:no_numbers | 10 | 0.60 | 1.00 | 1.00 | 1.00 | 0.76 | 1.00 | 1.00 |
| hard:period_format | 10 | 0.70 | 0.90 | 0.90 | 1.00 | 0.80 | 0.90 | 1.00 |
| style:paraphrase | 140 | 0.64 | 0.94 | 0.96 | 0.98 | 0.77 | 0.98 | 0.99 |
| style:exact | 25 | 0.76 | 0.92 | 0.96 | 0.96 | 0.84 | 0.96 | 1.00 |
| style:vague | 20 | 0.65 | 0.90 | 1.00 | 1.00 | 0.77 | 1.00 | 1.00 |
| style:analytical | 15 | 0.07 | 0.07 | 0.20 | 0.27 | 0.09 | 0.20 | 1.00 |

## Paired comparison vs `dense-voyage-4-large-2048-answer_key-soft.jsonl` (strict Recall@10)

Only this run finds: 12 (R063, R071, R073, R076, R079, R107, R122, R144, R145, R156, R173, R179)  
Only the other finds: 2 (R088, R172)  
Ties: 186; exact sign test p = 0.013

## Not found in the top 10 (strict): 18

R023, R029, R062, R064, R083, R088, R098, R115, R116, R117, R118, R159, R160, R161, R172, R182, R199, R200
