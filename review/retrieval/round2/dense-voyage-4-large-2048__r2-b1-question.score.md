# Retrieval score: `dense-voyage-4-large-2048__r2-b1-question.jsonl`

200 questions; missing from run: 0. Strict = answer pages checked on the image; lenient adds machine-found pages that print the answer's numbers. doc@10 = the right document anywhere in the top 10.

| group | n | strict_R@1 | strict_R@5 | strict_R@10 | strict_R@20 | strict_MRR@10 | lenient_R@10 | doc@10 |
|---|---|---|---|---|---|---|---|---|
| all | 200 | 0.52 | 0.82 | 0.85 | 0.90 | 0.64 | 0.87 | 0.95 |
| company:APARINDS | 64 | 0.50 | 0.83 | 0.86 | 0.89 | 0.64 | 0.88 | 0.91 |
| company:HEROMOTOCO | 54 | 0.44 | 0.80 | 0.81 | 0.87 | 0.59 | 0.85 | 0.98 |
| company:E2E | 43 | 0.40 | 0.81 | 0.88 | 0.93 | 0.55 | 0.91 | 0.98 |
| company:ESCONET | 21 | 0.71 | 0.81 | 0.81 | 0.86 | 0.76 | 0.81 | 0.95 |
| company:C2C | 18 | 0.83 | 0.89 | 0.89 | 1.00 | 0.86 | 0.89 | 1.00 |
| doctype:annual_reports | 111 | 0.53 | 0.80 | 0.83 | 0.88 | 0.65 | 0.86 | 0.95 |
| doctype:investor_presentations | 47 | 0.36 | 0.83 | 0.85 | 0.87 | 0.52 | 0.85 | 0.94 |
| doctype:concall_transcripts | 38 | 0.63 | 0.84 | 0.89 | 0.97 | 0.73 | 0.89 | 0.97 |
| doctype:periodic_results | 4 | 0.75 | 1.00 | 1.00 | 1.00 | 0.80 | 1.00 | 1.00 |
| evidence:table | 63 | 0.59 | 0.94 | 0.97 | 0.97 | 0.72 | 0.98 | 0.98 |
| evidence:concall | 33 | 0.73 | 0.94 | 0.94 | 0.97 | 0.82 | 0.94 | 0.97 |
| evidence:prose | 33 | 0.39 | 0.73 | 0.79 | 0.88 | 0.53 | 0.79 | 0.94 |
| evidence:statement | 25 | 0.56 | 0.92 | 0.92 | 0.96 | 0.70 | 0.96 | 0.96 |
| evidence:chart | 15 | 0.47 | 0.80 | 0.80 | 0.80 | 0.58 | 0.87 | 0.93 |
| evidence:multi | 15 | 0.07 | 0.13 | 0.27 | 0.60 | 0.12 | 0.27 | 1.00 |
| evidence:scan | 10 | 0.60 | 0.80 | 0.80 | 0.80 | 0.68 | 0.90 | 0.80 |
| evidence:kpi | 6 | 0.17 | 0.83 | 0.83 | 0.83 | 0.45 | 0.83 | 0.83 |
| hard:decoy_years | 63 | 0.60 | 0.87 | 0.90 | 0.92 | 0.72 | 0.94 | 0.95 |
| hard:standalone_vs_consolidated | 22 | 0.50 | 0.86 | 0.86 | 0.91 | 0.63 | 0.91 | 1.00 |
| hard:cross_doc | 17 | 0.06 | 0.24 | 0.35 | 0.65 | 0.15 | 0.35 | 0.94 |
| hard:spoken_numbers | 16 | 0.75 | 0.88 | 0.88 | 0.94 | 0.80 | 0.88 | 0.94 |
| hard:chart_labels | 14 | 0.43 | 0.79 | 0.79 | 0.79 | 0.55 | 0.86 | 0.93 |
| hard:indian_grouping | 14 | 0.43 | 0.93 | 0.93 | 0.93 | 0.57 | 0.93 | 0.93 |
| hard:multi_hop | 14 | 0.00 | 0.07 | 0.21 | 0.57 | 0.05 | 0.21 | 1.00 |
| hard:slide_table | 13 | 0.31 | 1.00 | 1.00 | 1.00 | 0.53 | 1.00 | 1.00 |
| hard:lakhs_unit | 11 | 0.55 | 0.82 | 0.91 | 0.91 | 0.67 | 1.00 | 0.91 |
| hard:footnote | 10 | 0.30 | 0.80 | 0.90 | 0.90 | 0.49 | 0.90 | 1.00 |
| hard:image_only_page | 10 | 0.60 | 0.80 | 0.80 | 0.80 | 0.68 | 0.90 | 0.80 |
| hard:no_numbers | 10 | 0.60 | 0.90 | 0.90 | 1.00 | 0.73 | 0.90 | 1.00 |
| hard:period_format | 10 | 0.60 | 0.90 | 0.90 | 0.90 | 0.72 | 0.90 | 0.90 |
| style:paraphrase | 140 | 0.55 | 0.87 | 0.89 | 0.92 | 0.68 | 0.91 | 0.94 |
| style:exact | 25 | 0.56 | 0.88 | 0.88 | 0.92 | 0.68 | 0.92 | 0.96 |
| style:vague | 20 | 0.55 | 0.90 | 0.95 | 0.95 | 0.69 | 0.95 | 1.00 |
| style:analytical | 15 | 0.07 | 0.13 | 0.27 | 0.60 | 0.12 | 0.27 | 1.00 |

## Paired comparison vs `dense-voyage-4-large-2048-question.jsonl` (strict Recall@10)

Only this run finds: 16 (R021, R028, R063, R069, R071, R073, R078, R079, R087, R099, R105, R107, R122, R144, R161, R163)  
Only the other finds: 1 (R097)  
Ties: 183; exact sign test p = 0.000

## Not found in the top 10 (strict): 30

R013, R023, R029, R030, R040, R050, R061, R062, R064, R068, R076, R083, R088, R097, R098, R115, R116, R117, R118, R145, R156, R157, R159, R160, R172, R173, R179, R182, R199, R200
