# Retrieval score: `dense-voyage-4-large-2048__r2-e-question.jsonl`

200 questions; missing from run: 0. Strict = answer pages checked on the image; lenient adds machine-found pages that print the answer's numbers. doc@10 = the right document anywhere in the top 10.

| group | n | strict_R@1 | strict_R@5 | strict_R@10 | strict_R@20 | strict_MRR@10 | lenient_R@10 | doc@10 |
|---|---|---|---|---|---|---|---|---|
| all | 200 | 0.39 | 0.72 | 0.80 | 0.86 | 0.53 | 0.82 | 0.94 |
| company:APARINDS | 64 | 0.39 | 0.70 | 0.83 | 0.88 | 0.55 | 0.84 | 0.92 |
| company:HEROMOTOCO | 54 | 0.37 | 0.72 | 0.78 | 0.81 | 0.51 | 0.80 | 0.96 |
| company:E2E | 43 | 0.33 | 0.72 | 0.79 | 0.86 | 0.48 | 0.84 | 0.91 |
| company:ESCONET | 21 | 0.43 | 0.71 | 0.76 | 0.86 | 0.55 | 0.76 | 0.90 |
| company:C2C | 18 | 0.56 | 0.78 | 0.83 | 0.94 | 0.66 | 0.83 | 1.00 |
| doctype:annual_reports | 111 | 0.36 | 0.75 | 0.81 | 0.84 | 0.53 | 0.85 | 0.95 |
| doctype:investor_presentations | 47 | 0.36 | 0.66 | 0.81 | 0.89 | 0.47 | 0.81 | 0.91 |
| doctype:concall_transcripts | 38 | 0.47 | 0.68 | 0.74 | 0.87 | 0.57 | 0.74 | 0.89 |
| doctype:periodic_results | 4 | 0.75 | 1.00 | 1.00 | 1.00 | 0.88 | 1.00 | 1.00 |
| evidence:table | 63 | 0.41 | 0.79 | 0.95 | 0.97 | 0.58 | 0.97 | 0.98 |
| evidence:concall | 33 | 0.55 | 0.79 | 0.82 | 0.88 | 0.65 | 0.82 | 0.88 |
| evidence:prose | 33 | 0.27 | 0.73 | 0.79 | 0.82 | 0.47 | 0.79 | 0.94 |
| evidence:statement | 25 | 0.40 | 0.72 | 0.80 | 0.92 | 0.55 | 0.84 | 0.88 |
| evidence:chart | 15 | 0.47 | 0.80 | 0.80 | 0.87 | 0.57 | 0.87 | 0.93 |
| evidence:multi | 15 | 0.00 | 0.07 | 0.13 | 0.40 | 0.02 | 0.13 | 1.00 |
| evidence:scan | 10 | 0.60 | 0.80 | 0.80 | 0.80 | 0.68 | 0.90 | 0.90 |
| evidence:kpi | 6 | 0.33 | 0.83 | 0.83 | 0.83 | 0.54 | 0.83 | 0.83 |
| hard:decoy_years | 63 | 0.38 | 0.78 | 0.87 | 0.90 | 0.56 | 0.90 | 0.94 |
| hard:standalone_vs_consolidated | 22 | 0.18 | 0.59 | 0.73 | 0.82 | 0.39 | 0.77 | 0.95 |
| hard:cross_doc | 17 | 0.06 | 0.18 | 0.24 | 0.47 | 0.11 | 0.24 | 0.94 |
| hard:spoken_numbers | 16 | 0.50 | 0.62 | 0.69 | 0.75 | 0.55 | 0.69 | 0.75 |
| hard:chart_labels | 14 | 0.43 | 0.79 | 0.79 | 0.86 | 0.54 | 0.86 | 0.93 |
| hard:indian_grouping | 14 | 0.36 | 0.79 | 0.93 | 0.93 | 0.54 | 0.93 | 0.93 |
| hard:multi_hop | 14 | 0.00 | 0.00 | 0.07 | 0.36 | 0.01 | 0.07 | 1.00 |
| hard:slide_table | 13 | 0.38 | 0.54 | 0.85 | 1.00 | 0.46 | 0.85 | 0.92 |
| hard:lakhs_unit | 11 | 0.55 | 0.82 | 0.82 | 0.91 | 0.68 | 0.91 | 0.82 |
| hard:footnote | 10 | 0.20 | 0.90 | 0.90 | 0.90 | 0.42 | 0.90 | 1.00 |
| hard:image_only_page | 10 | 0.60 | 0.80 | 0.80 | 0.80 | 0.68 | 0.90 | 0.90 |
| hard:no_numbers | 10 | 0.50 | 0.80 | 0.80 | 0.90 | 0.62 | 0.80 | 1.00 |
| hard:period_format | 10 | 0.50 | 0.70 | 0.80 | 0.90 | 0.58 | 0.80 | 0.90 |
| style:paraphrase | 140 | 0.42 | 0.78 | 0.86 | 0.89 | 0.57 | 0.88 | 0.91 |
| style:exact | 25 | 0.40 | 0.76 | 0.88 | 0.96 | 0.59 | 0.92 | 1.00 |
| style:vague | 20 | 0.45 | 0.75 | 0.80 | 0.85 | 0.58 | 0.80 | 1.00 |
| style:analytical | 15 | 0.00 | 0.07 | 0.13 | 0.40 | 0.02 | 0.13 | 1.00 |

## Paired comparison vs `dense-voyage-4-large-2048-question.jsonl` (strict Recall@10)

Only this run finds: 9 (R028, R063, R069, R071, R078, R087, R088, R099, R122)  
Only the other finds: 4 (R058, R127, R155, R198)  
Ties: 187; exact sign test p = 0.267

## Not found in the top 10 (strict): 40

R013, R021, R023, R029, R030, R040, R050, R058, R061, R062, R064, R068, R073, R076, R079, R083, R098, R105, R107, R115, R116, R117, R118, R127, R144, R145, R155, R156, R157, R159, R160, R161, R163, R172, R173, R179, R182, R198, R199, R200
