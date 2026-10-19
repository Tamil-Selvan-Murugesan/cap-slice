# Retrieval score: `hybrid-rrf-answer_key.jsonl`

200 questions; missing from run: 0. Strict = answer pages checked on the image; lenient adds machine-found pages that print the answer's numbers. doc@10 = the right document anywhere in the top 10.

| group | n | strict_R@1 | strict_R@5 | strict_R@10 | strict_R@20 | strict_MRR@10 | lenient_R@10 | doc@10 |
|---|---|---|---|---|---|---|---|---|
| all | 200 | 0.47 | 0.75 | 0.81 | 0.89 | 0.59 | 0.84 | 0.99 |
| company:APARINDS | 64 | 0.55 | 0.83 | 0.92 | 0.94 | 0.67 | 0.92 | 0.98 |
| company:HEROMOTOCO | 54 | 0.48 | 0.74 | 0.76 | 0.87 | 0.59 | 0.80 | 1.00 |
| company:E2E | 43 | 0.35 | 0.67 | 0.74 | 0.84 | 0.47 | 0.79 | 0.98 |
| company:ESCONET | 21 | 0.29 | 0.67 | 0.76 | 0.90 | 0.45 | 0.81 | 1.00 |
| company:C2C | 18 | 0.72 | 0.78 | 0.83 | 0.83 | 0.74 | 0.83 | 1.00 |
| doctype:annual_reports | 111 | 0.45 | 0.74 | 0.79 | 0.89 | 0.57 | 0.84 | 1.00 |
| doctype:investor_presentations | 47 | 0.53 | 0.79 | 0.89 | 0.91 | 0.64 | 0.89 | 0.98 |
| doctype:concall_transcripts | 38 | 0.45 | 0.74 | 0.76 | 0.82 | 0.55 | 0.76 | 0.97 |
| doctype:periodic_results | 4 | 0.75 | 0.75 | 1.00 | 1.00 | 0.79 | 1.00 | 1.00 |
| evidence:table | 63 | 0.49 | 0.86 | 0.90 | 0.97 | 0.64 | 0.95 | 1.00 |
| evidence:concall | 33 | 0.52 | 0.85 | 0.85 | 0.91 | 0.64 | 0.85 | 0.97 |
| evidence:prose | 33 | 0.48 | 0.76 | 0.82 | 0.97 | 0.59 | 0.82 | 1.00 |
| evidence:statement | 25 | 0.40 | 0.72 | 0.88 | 0.96 | 0.55 | 0.92 | 1.00 |
| evidence:chart | 15 | 0.60 | 0.73 | 0.80 | 0.87 | 0.65 | 0.87 | 0.93 |
| evidence:multi | 15 | 0.07 | 0.07 | 0.13 | 0.13 | 0.07 | 0.13 | 1.00 |
| evidence:scan | 10 | 0.70 | 0.80 | 0.90 | 0.90 | 0.74 | 0.90 | 1.00 |
| evidence:kpi | 6 | 0.67 | 0.83 | 1.00 | 1.00 | 0.77 | 1.00 | 1.00 |
| hard:decoy_years | 63 | 0.43 | 0.78 | 0.86 | 0.92 | 0.57 | 0.92 | 0.98 |
| hard:standalone_vs_consolidated | 22 | 0.50 | 0.59 | 0.68 | 0.82 | 0.54 | 0.77 | 1.00 |
| hard:cross_doc | 17 | 0.06 | 0.18 | 0.24 | 0.29 | 0.10 | 0.24 | 1.00 |
| hard:spoken_numbers | 16 | 0.38 | 0.75 | 0.75 | 0.81 | 0.50 | 0.75 | 0.94 |
| hard:chart_labels | 14 | 0.57 | 0.71 | 0.79 | 0.86 | 0.62 | 0.86 | 0.93 |
| hard:indian_grouping | 14 | 0.21 | 0.93 | 0.93 | 1.00 | 0.47 | 0.93 | 1.00 |
| hard:multi_hop | 14 | 0.00 | 0.00 | 0.07 | 0.07 | 0.01 | 0.07 | 1.00 |
| hard:slide_table | 13 | 0.62 | 0.92 | 1.00 | 1.00 | 0.73 | 1.00 | 1.00 |
| hard:lakhs_unit | 11 | 0.64 | 0.91 | 1.00 | 1.00 | 0.77 | 1.00 | 1.00 |
| hard:footnote | 10 | 0.20 | 0.90 | 0.90 | 1.00 | 0.47 | 0.90 | 1.00 |
| hard:image_only_page | 10 | 0.70 | 0.80 | 0.90 | 0.90 | 0.74 | 0.90 | 1.00 |
| hard:no_numbers | 10 | 0.40 | 0.90 | 0.90 | 1.00 | 0.60 | 0.90 | 1.00 |
| hard:period_format | 10 | 0.50 | 0.70 | 1.00 | 1.00 | 0.61 | 1.00 | 1.00 |
| style:paraphrase | 140 | 0.52 | 0.79 | 0.86 | 0.93 | 0.63 | 0.90 | 0.99 |
| style:exact | 25 | 0.52 | 0.84 | 0.88 | 1.00 | 0.65 | 0.88 | 1.00 |
| style:vague | 20 | 0.40 | 0.85 | 0.90 | 1.00 | 0.57 | 0.90 | 1.00 |
| style:analytical | 15 | 0.07 | 0.07 | 0.13 | 0.13 | 0.07 | 0.13 | 1.00 |

## Paired comparison vs `dense-answer_key.jsonl` (strict Recall@10)

Only this run finds: 6 (R023, R063, R078, R087, R099, R145)  
Only the other finds: 10 (R010, R050, R075, R142, R143, R151, R155, R158, R166, R172)  
Ties: 184; exact sign test p = 0.454

## Not found in the top 10 (strict): 37

R010, R029, R050, R062, R064, R071, R073, R075, R076, R079, R083, R088, R098, R107, R115, R116, R117, R118, R122, R142, R143, R144, R151, R155, R156, R158, R159, R160, R161, R166, R172, R173, R179, R182, R198, R199, R200
