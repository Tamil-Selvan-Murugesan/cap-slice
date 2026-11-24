# Retrieval score: `dense-voyage-4-large-2048__r2-e-question_next.jsonl`

200 questions; missing from run: 0. Strict = answer pages checked on the image; lenient adds machine-found pages that print the answer's numbers. doc@10 = the right document anywhere in the top 10.

| group | n | strict_R@1 | strict_R@5 | strict_R@10 | strict_R@20 | strict_MRR@10 | lenient_R@10 | doc@10 |
|---|---|---|---|---|---|---|---|---|
| all | 200 | 0.36 | 0.68 | 0.76 | 0.85 | 0.49 | 0.78 | 0.93 |
| company:APARINDS | 64 | 0.34 | 0.70 | 0.78 | 0.88 | 0.50 | 0.80 | 0.92 |
| company:HEROMOTOCO | 54 | 0.35 | 0.65 | 0.72 | 0.80 | 0.48 | 0.76 | 0.96 |
| company:E2E | 43 | 0.28 | 0.67 | 0.79 | 0.91 | 0.43 | 0.81 | 0.93 |
| company:ESCONET | 21 | 0.43 | 0.57 | 0.62 | 0.76 | 0.49 | 0.67 | 0.81 |
| company:C2C | 18 | 0.56 | 0.78 | 0.83 | 0.94 | 0.66 | 0.83 | 1.00 |
| doctype:annual_reports | 111 | 0.34 | 0.71 | 0.78 | 0.85 | 0.50 | 0.82 | 0.97 |
| doctype:investor_presentations | 47 | 0.34 | 0.57 | 0.74 | 0.87 | 0.44 | 0.77 | 0.87 |
| doctype:concall_transcripts | 38 | 0.39 | 0.66 | 0.66 | 0.84 | 0.50 | 0.66 | 0.87 |
| doctype:periodic_results | 4 | 0.75 | 1.00 | 1.00 | 1.00 | 0.88 | 1.00 | 1.00 |
| evidence:table | 63 | 0.40 | 0.70 | 0.89 | 0.95 | 0.54 | 0.94 | 0.97 |
| evidence:concall | 33 | 0.45 | 0.76 | 0.76 | 0.85 | 0.58 | 0.76 | 0.85 |
| evidence:prose | 33 | 0.21 | 0.70 | 0.73 | 0.79 | 0.39 | 0.73 | 0.94 |
| evidence:statement | 25 | 0.36 | 0.68 | 0.76 | 0.96 | 0.52 | 0.80 | 0.92 |
| evidence:chart | 15 | 0.47 | 0.80 | 0.80 | 0.80 | 0.57 | 0.87 | 0.93 |
| evidence:multi | 15 | 0.00 | 0.00 | 0.07 | 0.47 | 0.01 | 0.07 | 0.93 |
| evidence:scan | 10 | 0.70 | 0.90 | 0.90 | 0.90 | 0.78 | 0.90 | 1.00 |
| evidence:kpi | 6 | 0.33 | 0.83 | 0.83 | 0.83 | 0.51 | 0.83 | 0.83 |
| hard:decoy_years | 63 | 0.37 | 0.73 | 0.86 | 0.94 | 0.54 | 0.89 | 0.97 |
| hard:standalone_vs_consolidated | 22 | 0.18 | 0.50 | 0.64 | 0.82 | 0.36 | 0.68 | 0.95 |
| hard:cross_doc | 17 | 0.06 | 0.18 | 0.29 | 0.59 | 0.10 | 0.29 | 1.00 |
| hard:spoken_numbers | 16 | 0.44 | 0.62 | 0.62 | 0.75 | 0.50 | 0.62 | 0.75 |
| hard:chart_labels | 14 | 0.43 | 0.79 | 0.79 | 0.79 | 0.54 | 0.86 | 0.93 |
| hard:indian_grouping | 14 | 0.36 | 0.79 | 0.86 | 0.93 | 0.52 | 0.93 | 0.93 |
| hard:multi_hop | 14 | 0.00 | 0.00 | 0.07 | 0.43 | 0.01 | 0.07 | 1.00 |
| hard:slide_table | 13 | 0.31 | 0.46 | 0.62 | 0.92 | 0.39 | 0.69 | 0.85 |
| hard:lakhs_unit | 11 | 0.55 | 0.91 | 0.91 | 1.00 | 0.70 | 0.91 | 0.91 |
| hard:footnote | 10 | 0.10 | 0.80 | 0.90 | 0.90 | 0.29 | 0.90 | 1.00 |
| hard:image_only_page | 10 | 0.70 | 0.90 | 0.90 | 0.90 | 0.78 | 0.90 | 1.00 |
| hard:no_numbers | 10 | 0.40 | 0.80 | 0.80 | 0.90 | 0.55 | 0.80 | 1.00 |
| hard:period_format | 10 | 0.50 | 0.60 | 0.60 | 0.70 | 0.55 | 0.60 | 0.80 |
| style:paraphrase | 140 | 0.39 | 0.72 | 0.81 | 0.89 | 0.53 | 0.84 | 0.91 |
| style:exact | 25 | 0.40 | 0.76 | 0.84 | 0.92 | 0.57 | 0.88 | 1.00 |
| style:vague | 20 | 0.35 | 0.75 | 0.75 | 0.85 | 0.49 | 0.75 | 1.00 |
| style:analytical | 15 | 0.00 | 0.00 | 0.07 | 0.47 | 0.01 | 0.07 | 0.93 |

## Paired comparison vs `dense-voyage-4-large-2048-question_next.jsonl` (strict Recall@10)

Only this run finds: 8 (R028, R066, R069, R078, R086, R087, R090, R099)  
Only the other finds: 5 (R055, R058, R111, R155, R198)  
Ties: 187; exact sign test p = 0.581

## Not found in the top 10 (strict): 49

R004, R013, R021, R022, R023, R029, R040, R050, R055, R058, R061, R062, R063, R064, R068, R071, R073, R076, R079, R083, R088, R098, R105, R107, R111, R115, R116, R117, R118, R122, R127, R136, R144, R145, R155, R156, R159, R161, R163, R170, R171, R172, R173, R179, R181, R182, R198, R199, R200
