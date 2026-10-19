# Retrieval score: `hybrid-dbsf-answer_key-soft.jsonl`

200 questions; missing from run: 0. Strict = answer pages checked on the image; lenient adds machine-found pages that print the answer's numbers. doc@10 = the right document anywhere in the top 10.

| group | n | strict_R@1 | strict_R@5 | strict_R@10 | strict_R@20 | strict_MRR@10 | lenient_R@10 | doc@10 |
|---|---|---|---|---|---|---|---|---|
| all | 200 | 0.45 | 0.76 | 0.83 | 0.88 | 0.58 | 0.86 | 1.00 |
| company:APARINDS | 64 | 0.47 | 0.88 | 0.92 | 0.94 | 0.64 | 0.92 | 1.00 |
| company:HEROMOTOCO | 54 | 0.50 | 0.72 | 0.81 | 0.85 | 0.61 | 0.87 | 1.00 |
| company:E2E | 43 | 0.30 | 0.63 | 0.74 | 0.84 | 0.44 | 0.79 | 1.00 |
| company:ESCONET | 21 | 0.33 | 0.71 | 0.76 | 0.81 | 0.48 | 0.76 | 1.00 |
| company:C2C | 18 | 0.67 | 0.78 | 0.89 | 0.89 | 0.73 | 0.89 | 1.00 |
| doctype:annual_reports | 111 | 0.43 | 0.75 | 0.83 | 0.86 | 0.58 | 0.87 | 1.00 |
| doctype:investor_presentations | 47 | 0.45 | 0.79 | 0.89 | 0.91 | 0.59 | 0.89 | 1.00 |
| doctype:concall_transcripts | 38 | 0.45 | 0.71 | 0.76 | 0.87 | 0.55 | 0.76 | 1.00 |
| doctype:periodic_results | 4 | 0.75 | 1.00 | 1.00 | 1.00 | 0.80 | 1.00 | 1.00 |
| evidence:table | 63 | 0.44 | 0.86 | 0.92 | 0.95 | 0.62 | 0.95 | 1.00 |
| evidence:concall | 33 | 0.52 | 0.79 | 0.85 | 0.91 | 0.62 | 0.85 | 1.00 |
| evidence:prose | 33 | 0.45 | 0.79 | 0.88 | 0.91 | 0.59 | 0.88 | 1.00 |
| evidence:statement | 25 | 0.40 | 0.76 | 0.92 | 0.92 | 0.57 | 1.00 | 1.00 |
| evidence:chart | 15 | 0.47 | 0.73 | 0.80 | 0.80 | 0.59 | 0.87 | 1.00 |
| evidence:multi | 15 | 0.07 | 0.13 | 0.13 | 0.33 | 0.09 | 0.13 | 1.00 |
| evidence:scan | 10 | 0.70 | 0.80 | 0.90 | 0.90 | 0.74 | 0.90 | 1.00 |
| evidence:kpi | 6 | 0.67 | 0.83 | 1.00 | 1.00 | 0.78 | 1.00 | 1.00 |
| hard:decoy_years | 63 | 0.44 | 0.79 | 0.87 | 0.90 | 0.60 | 0.94 | 1.00 |
| hard:standalone_vs_consolidated | 22 | 0.45 | 0.64 | 0.77 | 0.77 | 0.55 | 0.86 | 1.00 |
| hard:cross_doc | 17 | 0.06 | 0.24 | 0.24 | 0.41 | 0.11 | 0.24 | 1.00 |
| hard:spoken_numbers | 16 | 0.38 | 0.62 | 0.75 | 0.88 | 0.49 | 0.75 | 1.00 |
| hard:chart_labels | 14 | 0.43 | 0.71 | 0.79 | 0.79 | 0.56 | 0.86 | 1.00 |
| hard:indian_grouping | 14 | 0.21 | 0.93 | 0.93 | 1.00 | 0.46 | 0.93 | 1.00 |
| hard:multi_hop | 14 | 0.00 | 0.07 | 0.07 | 0.29 | 0.02 | 0.07 | 1.00 |
| hard:slide_table | 13 | 0.38 | 0.92 | 1.00 | 1.00 | 0.62 | 1.00 | 1.00 |
| hard:lakhs_unit | 11 | 0.55 | 1.00 | 1.00 | 1.00 | 0.72 | 1.00 | 1.00 |
| hard:footnote | 10 | 0.30 | 0.70 | 0.90 | 0.90 | 0.50 | 0.90 | 1.00 |
| hard:image_only_page | 10 | 0.70 | 0.80 | 0.90 | 0.90 | 0.74 | 0.90 | 1.00 |
| hard:no_numbers | 10 | 0.40 | 0.90 | 0.90 | 0.90 | 0.57 | 0.90 | 1.00 |
| hard:period_format | 10 | 0.30 | 0.80 | 1.00 | 1.00 | 0.52 | 1.00 | 1.00 |
| style:paraphrase | 140 | 0.48 | 0.79 | 0.87 | 0.91 | 0.62 | 0.90 | 1.00 |
| style:exact | 25 | 0.56 | 0.84 | 0.96 | 0.96 | 0.69 | 1.00 | 1.00 |
| style:vague | 20 | 0.35 | 0.85 | 0.95 | 0.95 | 0.54 | 0.95 | 1.00 |
| style:analytical | 15 | 0.07 | 0.13 | 0.13 | 0.33 | 0.09 | 0.13 | 1.00 |

## Paired comparison vs `dense-answer_key-soft.jsonl` (strict Recall@10)

Only this run finds: 4 (R023, R079, R098, R145)  
Only the other finds: 9 (R050, R075, R142, R143, R151, R155, R158, R166, R172)  
Ties: 187; exact sign test p = 0.267

## Not found in the top 10 (strict): 33

R029, R050, R062, R063, R064, R071, R073, R075, R076, R083, R107, R115, R116, R117, R118, R122, R142, R143, R144, R151, R155, R156, R158, R159, R160, R161, R166, R172, R173, R179, R182, R199, R200
