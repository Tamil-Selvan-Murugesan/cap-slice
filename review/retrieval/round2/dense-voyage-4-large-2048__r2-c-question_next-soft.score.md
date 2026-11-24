# Retrieval score: `dense-voyage-4-large-2048__r2-c-question_next-soft.jsonl`

200 questions; missing from run: 0. Strict = answer pages checked on the image; lenient adds machine-found pages that print the answer's numbers. doc@10 = the right document anywhere in the top 10.

| group | n | strict_R@1 | strict_R@5 | strict_R@10 | strict_R@20 | strict_MRR@10 | lenient_R@10 | doc@10 |
|---|---|---|---|---|---|---|---|---|
| all | 200 | 0.35 | 0.63 | 0.71 | 0.81 | 0.47 | 0.76 | 0.92 |
| company:APARINDS | 64 | 0.34 | 0.66 | 0.75 | 0.81 | 0.48 | 0.78 | 0.89 |
| company:HEROMOTOCO | 54 | 0.39 | 0.63 | 0.67 | 0.76 | 0.49 | 0.70 | 0.96 |
| company:E2E | 43 | 0.23 | 0.53 | 0.72 | 0.86 | 0.37 | 0.77 | 0.95 |
| company:ESCONET | 21 | 0.33 | 0.52 | 0.52 | 0.71 | 0.41 | 0.67 | 0.76 |
| company:C2C | 18 | 0.56 | 0.89 | 0.89 | 0.94 | 0.68 | 0.89 | 1.00 |
| doctype:annual_reports | 111 | 0.36 | 0.65 | 0.69 | 0.79 | 0.48 | 0.77 | 0.97 |
| doctype:investor_presentations | 47 | 0.26 | 0.49 | 0.66 | 0.79 | 0.37 | 0.68 | 0.79 |
| doctype:concall_transcripts | 38 | 0.42 | 0.71 | 0.79 | 0.87 | 0.53 | 0.79 | 0.92 |
| doctype:periodic_results | 4 | 0.50 | 1.00 | 1.00 | 1.00 | 0.67 | 1.00 | 1.00 |
| evidence:table | 63 | 0.30 | 0.60 | 0.68 | 0.87 | 0.42 | 0.79 | 0.94 |
| evidence:concall | 33 | 0.48 | 0.79 | 0.88 | 0.91 | 0.60 | 0.88 | 0.94 |
| evidence:prose | 33 | 0.36 | 0.70 | 0.79 | 0.82 | 0.50 | 0.79 | 0.97 |
| evidence:statement | 25 | 0.36 | 0.60 | 0.72 | 0.76 | 0.48 | 0.76 | 0.92 |
| evidence:chart | 15 | 0.40 | 0.73 | 0.80 | 0.80 | 0.56 | 0.87 | 0.93 |
| evidence:multi | 15 | 0.00 | 0.07 | 0.13 | 0.40 | 0.03 | 0.13 | 0.80 |
| evidence:scan | 10 | 0.60 | 0.80 | 0.80 | 0.90 | 0.68 | 0.80 | 0.90 |
| evidence:kpi | 6 | 0.33 | 0.67 | 0.67 | 0.67 | 0.50 | 0.67 | 0.67 |
| hard:decoy_years | 63 | 0.37 | 0.65 | 0.70 | 0.84 | 0.49 | 0.79 | 0.94 |
| hard:standalone_vs_consolidated | 22 | 0.27 | 0.50 | 0.59 | 0.64 | 0.39 | 0.68 | 0.95 |
| hard:cross_doc | 17 | 0.00 | 0.24 | 0.35 | 0.53 | 0.11 | 0.35 | 0.88 |
| hard:spoken_numbers | 16 | 0.50 | 0.69 | 0.75 | 0.81 | 0.56 | 0.75 | 0.88 |
| hard:chart_labels | 14 | 0.36 | 0.71 | 0.79 | 0.79 | 0.53 | 0.86 | 0.93 |
| hard:indian_grouping | 14 | 0.21 | 0.50 | 0.57 | 0.64 | 0.34 | 0.71 | 0.86 |
| hard:multi_hop | 14 | 0.00 | 0.07 | 0.14 | 0.36 | 0.04 | 0.14 | 0.86 |
| hard:slide_table | 13 | 0.15 | 0.31 | 0.54 | 0.62 | 0.22 | 0.62 | 0.77 |
| hard:lakhs_unit | 11 | 0.55 | 0.91 | 0.91 | 0.91 | 0.66 | 0.91 | 0.91 |
| hard:footnote | 10 | 0.20 | 0.60 | 0.80 | 0.90 | 0.35 | 0.80 | 1.00 |
| hard:image_only_page | 10 | 0.60 | 0.80 | 0.80 | 0.90 | 0.68 | 0.80 | 0.90 |
| hard:no_numbers | 10 | 0.30 | 0.70 | 0.90 | 0.90 | 0.49 | 0.90 | 1.00 |
| hard:period_format | 10 | 0.30 | 0.50 | 0.70 | 0.80 | 0.41 | 0.70 | 0.80 |
| style:paraphrase | 140 | 0.38 | 0.67 | 0.76 | 0.84 | 0.50 | 0.81 | 0.92 |
| style:exact | 25 | 0.40 | 0.68 | 0.72 | 0.84 | 0.54 | 0.80 | 0.92 |
| style:vague | 20 | 0.35 | 0.70 | 0.80 | 0.90 | 0.50 | 0.80 | 1.00 |
| style:analytical | 15 | 0.00 | 0.07 | 0.13 | 0.40 | 0.03 | 0.13 | 0.80 |

## Paired comparison vs `dense-voyage-4-large-2048-question_next-soft.jsonl` (strict Recall@10)

Only this run finds: 1 (R004)  
Only the other finds: 14 (R006, R025, R034, R036, R041, R065, R078, R112, R120, R137, R141, R146, R164, R166)  
Ties: 185; exact sign test p = 0.001

## Not found in the top 10 (strict): 58

R006, R013, R021, R022, R023, R025, R028, R029, R034, R036, R041, R050, R061, R062, R063, R064, R065, R068, R071, R073, R076, R078, R079, R083, R088, R090, R098, R105, R107, R112, R115, R116, R117, R118, R120, R122, R127, R136, R137, R141, R144, R145, R146, R156, R159, R161, R163, R164, R166, R170, R171, R172, R173, R179, R181, R182, R199, R200
