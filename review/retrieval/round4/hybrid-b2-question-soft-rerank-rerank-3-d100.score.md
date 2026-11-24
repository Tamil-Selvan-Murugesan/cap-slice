# Retrieval score: `hybrid-b2-question-soft-rerank-rerank-3-d100.jsonl`

200 questions; missing from run: 0. Strict = answer pages checked on the image; lenient adds machine-found pages that print the answer's numbers. doc@10 = the right document anywhere in the top 10.

| group | n | strict_R@1 | strict_R@5 | strict_R@10 | strict_R@20 | strict_MRR@10 | lenient_R@10 | doc@10 |
|---|---|---|---|---|---|---|---|---|
| all | 200 | 0.59 | 0.85 | 0.91 | 0.94 | 0.71 | 0.92 | 0.99 |
| company:APARINDS | 64 | 0.59 | 0.91 | 0.92 | 0.95 | 0.74 | 0.92 | 0.97 |
| company:HEROMOTOCO | 54 | 0.61 | 0.80 | 0.87 | 0.91 | 0.70 | 0.89 | 1.00 |
| company:E2E | 43 | 0.58 | 0.88 | 0.93 | 0.95 | 0.71 | 0.93 | 1.00 |
| company:ESCONET | 21 | 0.48 | 0.76 | 0.90 | 0.90 | 0.62 | 0.90 | 1.00 |
| company:C2C | 18 | 0.72 | 0.89 | 0.94 | 1.00 | 0.80 | 0.94 | 1.00 |
| doctype:annual_reports | 111 | 0.51 | 0.82 | 0.91 | 0.94 | 0.66 | 0.92 | 1.00 |
| doctype:investor_presentations | 47 | 0.68 | 0.85 | 0.85 | 0.89 | 0.75 | 0.85 | 0.96 |
| doctype:concall_transcripts | 38 | 0.71 | 0.95 | 0.97 | 1.00 | 0.81 | 0.97 | 1.00 |
| doctype:periodic_results | 4 | 0.75 | 1.00 | 1.00 | 1.00 | 0.81 | 1.00 | 1.00 |
| evidence:table | 63 | 0.68 | 0.95 | 1.00 | 1.00 | 0.81 | 1.00 | 1.00 |
| evidence:concall | 33 | 0.82 | 1.00 | 1.00 | 1.00 | 0.89 | 1.00 | 1.00 |
| evidence:prose | 33 | 0.33 | 0.79 | 0.94 | 0.97 | 0.54 | 0.94 | 1.00 |
| evidence:statement | 25 | 0.64 | 0.92 | 0.96 | 0.96 | 0.76 | 0.96 | 1.00 |
| evidence:chart | 15 | 0.60 | 0.80 | 0.80 | 0.80 | 0.68 | 0.87 | 0.93 |
| evidence:multi | 15 | 0.00 | 0.27 | 0.40 | 0.60 | 0.13 | 0.40 | 1.00 |
| evidence:scan | 10 | 0.90 | 0.90 | 0.90 | 1.00 | 0.90 | 0.90 | 1.00 |
| evidence:kpi | 6 | 0.67 | 0.67 | 0.67 | 0.83 | 0.67 | 0.67 | 0.83 |
| hard:decoy_years | 63 | 0.63 | 0.90 | 0.94 | 0.94 | 0.75 | 0.95 | 0.98 |
| hard:standalone_vs_consolidated | 22 | 0.55 | 0.82 | 0.95 | 0.95 | 0.69 | 0.95 | 1.00 |
| hard:cross_doc | 17 | 0.06 | 0.41 | 0.53 | 0.71 | 0.23 | 0.53 | 1.00 |
| hard:spoken_numbers | 16 | 0.75 | 1.00 | 1.00 | 1.00 | 0.85 | 1.00 | 1.00 |
| hard:chart_labels | 14 | 0.57 | 0.79 | 0.79 | 0.79 | 0.66 | 0.86 | 0.93 |
| hard:indian_grouping | 14 | 0.50 | 0.93 | 1.00 | 1.00 | 0.69 | 1.00 | 1.00 |
| hard:multi_hop | 14 | 0.00 | 0.21 | 0.36 | 0.57 | 0.11 | 0.36 | 1.00 |
| hard:slide_table | 13 | 0.85 | 1.00 | 1.00 | 1.00 | 0.91 | 1.00 | 1.00 |
| hard:lakhs_unit | 11 | 0.73 | 0.91 | 1.00 | 1.00 | 0.80 | 1.00 | 1.00 |
| hard:footnote | 10 | 0.60 | 0.80 | 0.90 | 0.90 | 0.68 | 0.90 | 1.00 |
| hard:image_only_page | 10 | 0.90 | 0.90 | 0.90 | 1.00 | 0.90 | 0.90 | 1.00 |
| hard:no_numbers | 10 | 0.90 | 0.90 | 1.00 | 1.00 | 0.91 | 1.00 | 1.00 |
| hard:period_format | 10 | 0.70 | 0.80 | 0.80 | 0.90 | 0.73 | 0.80 | 0.90 |
| style:paraphrase | 140 | 0.69 | 0.90 | 0.95 | 0.96 | 0.78 | 0.96 | 0.99 |
| style:exact | 25 | 0.52 | 0.92 | 0.96 | 1.00 | 0.69 | 0.96 | 1.00 |
| style:vague | 20 | 0.50 | 0.90 | 0.95 | 0.95 | 0.69 | 0.95 | 1.00 |
| style:analytical | 15 | 0.00 | 0.27 | 0.40 | 0.60 | 0.13 | 0.40 | 1.00 |

## Paired comparison vs `dense-b2-question-soft-top100.jsonl` (strict Recall@10)

Only this run finds: 11 (R013, R028, R030, R050, R064, R088, R098, R156, R173, R179, R199)  
Only the other finds: 2 (R031, R116)  
Ties: 187; exact sign test p = 0.022

## Not found in the top 10 (strict): 18

R023, R029, R031, R061, R062, R068, R076, R083, R115, R116, R117, R118, R145, R159, R160, R172, R182, R200
