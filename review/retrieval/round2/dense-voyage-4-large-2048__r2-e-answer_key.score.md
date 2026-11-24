# Retrieval score: `dense-voyage-4-large-2048__r2-e-answer_key.jsonl`

200 questions; missing from run: 0. Strict = answer pages checked on the image; lenient adds machine-found pages that print the answer's numbers. doc@10 = the right document anywhere in the top 10.

| group | n | strict_R@1 | strict_R@5 | strict_R@10 | strict_R@20 | strict_MRR@10 | lenient_R@10 | doc@10 |
|---|---|---|---|---|---|---|---|---|
| all | 200 | 0.47 | 0.80 | 0.86 | 0.90 | 0.61 | 0.89 | 0.98 |
| company:APARINDS | 64 | 0.47 | 0.83 | 0.91 | 0.95 | 0.63 | 0.92 | 0.97 |
| company:HEROMOTOCO | 54 | 0.46 | 0.76 | 0.81 | 0.85 | 0.58 | 0.83 | 1.00 |
| company:E2E | 43 | 0.40 | 0.84 | 0.88 | 0.91 | 0.59 | 0.91 | 0.98 |
| company:ESCONET | 21 | 0.48 | 0.76 | 0.86 | 0.90 | 0.62 | 0.90 | 1.00 |
| company:C2C | 18 | 0.61 | 0.78 | 0.83 | 0.83 | 0.69 | 0.83 | 1.00 |
| doctype:annual_reports | 111 | 0.41 | 0.82 | 0.86 | 0.91 | 0.58 | 0.90 | 1.00 |
| doctype:investor_presentations | 47 | 0.53 | 0.83 | 0.89 | 0.91 | 0.66 | 0.89 | 0.96 |
| doctype:concall_transcripts | 38 | 0.50 | 0.68 | 0.82 | 0.84 | 0.60 | 0.82 | 0.97 |
| doctype:periodic_results | 4 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| evidence:table | 63 | 0.48 | 0.92 | 0.98 | 1.00 | 0.66 | 1.00 | 1.00 |
| evidence:concall | 33 | 0.58 | 0.79 | 0.91 | 0.94 | 0.69 | 0.91 | 0.97 |
| evidence:prose | 33 | 0.39 | 0.79 | 0.85 | 0.94 | 0.57 | 0.88 | 1.00 |
| evidence:statement | 25 | 0.48 | 0.88 | 0.92 | 0.96 | 0.64 | 0.96 | 1.00 |
| evidence:chart | 15 | 0.47 | 0.80 | 0.87 | 0.87 | 0.60 | 0.93 | 0.93 |
| evidence:multi | 15 | 0.07 | 0.07 | 0.13 | 0.13 | 0.08 | 0.13 | 1.00 |
| evidence:scan | 10 | 0.80 | 1.00 | 1.00 | 1.00 | 0.88 | 1.00 | 1.00 |
| evidence:kpi | 6 | 0.50 | 0.83 | 0.83 | 1.00 | 0.67 | 0.83 | 0.83 |
| hard:decoy_years | 63 | 0.44 | 0.87 | 0.92 | 0.94 | 0.63 | 0.95 | 0.98 |
| hard:standalone_vs_consolidated | 22 | 0.18 | 0.68 | 0.77 | 0.86 | 0.41 | 0.82 | 1.00 |
| hard:cross_doc | 17 | 0.12 | 0.24 | 0.29 | 0.29 | 0.18 | 0.29 | 1.00 |
| hard:spoken_numbers | 16 | 0.50 | 0.62 | 0.88 | 0.88 | 0.59 | 0.88 | 0.94 |
| hard:chart_labels | 14 | 0.43 | 0.79 | 0.86 | 0.86 | 0.57 | 0.93 | 0.93 |
| hard:indian_grouping | 14 | 0.43 | 0.86 | 0.93 | 1.00 | 0.60 | 1.00 | 1.00 |
| hard:multi_hop | 14 | 0.00 | 0.00 | 0.07 | 0.07 | 0.01 | 0.07 | 1.00 |
| hard:slide_table | 13 | 0.62 | 0.85 | 1.00 | 1.00 | 0.71 | 1.00 | 1.00 |
| hard:lakhs_unit | 11 | 0.73 | 1.00 | 1.00 | 1.00 | 0.86 | 1.00 | 1.00 |
| hard:footnote | 10 | 0.30 | 0.90 | 0.90 | 0.90 | 0.53 | 0.90 | 1.00 |
| hard:image_only_page | 10 | 0.80 | 1.00 | 1.00 | 1.00 | 0.88 | 1.00 | 1.00 |
| hard:no_numbers | 10 | 0.50 | 0.80 | 0.80 | 0.90 | 0.63 | 0.80 | 1.00 |
| hard:period_format | 10 | 0.50 | 0.70 | 0.90 | 1.00 | 0.63 | 0.90 | 0.90 |
| style:paraphrase | 140 | 0.50 | 0.86 | 0.94 | 0.96 | 0.66 | 0.96 | 0.98 |
| style:exact | 25 | 0.48 | 0.88 | 0.92 | 1.00 | 0.67 | 0.96 | 1.00 |
| style:vague | 20 | 0.50 | 0.80 | 0.85 | 0.95 | 0.64 | 0.85 | 1.00 |
| style:analytical | 15 | 0.07 | 0.07 | 0.13 | 0.13 | 0.08 | 0.13 | 1.00 |

## Paired comparison vs `dense-voyage-4-large-2048-answer_key.jsonl` (strict Recall@10)

Only this run finds: 8 (R063, R071, R078, R087, R088, R099, R122, R145)  
Only the other finds: 2 (R013, R058)  
Ties: 190; exact sign test p = 0.109

## Not found in the top 10 (strict): 27

R013, R023, R029, R058, R062, R064, R073, R076, R079, R083, R098, R107, R115, R116, R117, R118, R144, R156, R159, R160, R161, R173, R179, R182, R198, R199, R200
