# Retrieval score: `dense-nemotron-3-embed-8b-bf16-2048-answer_key.jsonl`

200 questions; missing from run: 0. Strict = answer pages checked on the image; lenient adds machine-found pages that print the answer's numbers. doc@10 = the right document anywhere in the top 10.

| group | n | strict_R@1 | strict_R@5 | strict_R@10 | strict_R@20 | strict_MRR@10 | lenient_R@10 | doc@10 |
|---|---|---|---|---|---|---|---|---|
| all | 200 | 0.43 | 0.74 | 0.81 | 0.84 | 0.57 | 0.82 | 0.98 |
| company:APARINDS | 64 | 0.48 | 0.80 | 0.84 | 0.88 | 0.62 | 0.86 | 0.97 |
| company:HEROMOTOCO | 54 | 0.48 | 0.76 | 0.80 | 0.85 | 0.59 | 0.81 | 1.00 |
| company:E2E | 43 | 0.23 | 0.63 | 0.77 | 0.77 | 0.40 | 0.79 | 0.98 |
| company:ESCONET | 21 | 0.48 | 0.71 | 0.81 | 0.86 | 0.58 | 0.81 | 1.00 |
| company:C2C | 18 | 0.56 | 0.83 | 0.83 | 0.83 | 0.67 | 0.83 | 1.00 |
| doctype:annual_reports | 111 | 0.42 | 0.73 | 0.81 | 0.85 | 0.56 | 0.84 | 1.00 |
| doctype:investor_presentations | 47 | 0.49 | 0.79 | 0.83 | 0.83 | 0.61 | 0.83 | 0.96 |
| doctype:concall_transcripts | 38 | 0.39 | 0.71 | 0.76 | 0.82 | 0.52 | 0.76 | 0.97 |
| doctype:periodic_results | 4 | 0.50 | 1.00 | 1.00 | 1.00 | 0.71 | 1.00 | 1.00 |
| evidence:table | 63 | 0.44 | 0.83 | 0.94 | 0.95 | 0.61 | 0.95 | 1.00 |
| evidence:concall | 33 | 0.45 | 0.82 | 0.85 | 0.91 | 0.60 | 0.85 | 0.97 |
| evidence:prose | 33 | 0.45 | 0.76 | 0.82 | 0.85 | 0.60 | 0.82 | 1.00 |
| evidence:statement | 25 | 0.32 | 0.72 | 0.80 | 0.88 | 0.48 | 0.84 | 0.96 |
| evidence:chart | 15 | 0.53 | 0.80 | 0.80 | 0.80 | 0.62 | 0.87 | 0.93 |
| evidence:multi | 15 | 0.07 | 0.07 | 0.13 | 0.13 | 0.07 | 0.13 | 1.00 |
| evidence:scan | 10 | 0.80 | 0.90 | 0.90 | 0.90 | 0.83 | 0.90 | 1.00 |
| evidence:kpi | 6 | 0.67 | 0.83 | 0.83 | 0.83 | 0.75 | 0.83 | 1.00 |
| hard:decoy_years | 63 | 0.37 | 0.73 | 0.83 | 0.89 | 0.52 | 0.86 | 0.98 |
| hard:standalone_vs_consolidated | 22 | 0.27 | 0.59 | 0.64 | 0.77 | 0.39 | 0.68 | 1.00 |
| hard:cross_doc | 17 | 0.06 | 0.18 | 0.24 | 0.24 | 0.11 | 0.24 | 1.00 |
| hard:spoken_numbers | 16 | 0.25 | 0.69 | 0.75 | 0.88 | 0.43 | 0.75 | 1.00 |
| hard:chart_labels | 14 | 0.50 | 0.79 | 0.79 | 0.79 | 0.60 | 0.86 | 0.93 |
| hard:indian_grouping | 14 | 0.43 | 0.86 | 1.00 | 1.00 | 0.58 | 1.00 | 1.00 |
| hard:multi_hop | 14 | 0.00 | 0.00 | 0.07 | 0.07 | 0.01 | 0.07 | 1.00 |
| hard:slide_table | 13 | 0.54 | 0.92 | 0.92 | 0.92 | 0.69 | 0.92 | 0.92 |
| hard:lakhs_unit | 11 | 0.55 | 0.91 | 1.00 | 1.00 | 0.67 | 1.00 | 1.00 |
| hard:footnote | 10 | 0.50 | 0.70 | 0.90 | 0.90 | 0.61 | 0.90 | 1.00 |
| hard:image_only_page | 10 | 0.80 | 0.90 | 0.90 | 0.90 | 0.83 | 0.90 | 1.00 |
| hard:no_numbers | 10 | 0.50 | 0.80 | 0.80 | 0.80 | 0.61 | 0.80 | 0.90 |
| hard:period_format | 10 | 0.40 | 0.70 | 0.70 | 0.70 | 0.53 | 0.70 | 0.90 |
| style:paraphrase | 140 | 0.44 | 0.77 | 0.85 | 0.88 | 0.59 | 0.86 | 0.98 |
| style:exact | 25 | 0.52 | 0.92 | 0.96 | 1.00 | 0.70 | 1.00 | 1.00 |
| style:vague | 20 | 0.55 | 0.85 | 0.85 | 0.90 | 0.65 | 0.85 | 1.00 |
| style:analytical | 15 | 0.07 | 0.07 | 0.13 | 0.13 | 0.07 | 0.13 | 1.00 |

## Paired comparison vs `dense-voyage-4-large-2048-answer_key.jsonl` (strict Recall@10)

Only this run finds: 8 (R063, R071, R078, R087, R088, R098, R099, R179)  
Only the other finds: 13 (R002, R004, R013, R030, R054, R055, R068, R105, R125, R146, R158, R166, R172)  
Ties: 179; exact sign test p = 0.383

## Not found in the top 10 (strict): 38

R002, R004, R013, R023, R029, R030, R054, R055, R062, R064, R068, R073, R076, R079, R083, R105, R107, R115, R116, R117, R118, R122, R125, R144, R145, R146, R156, R158, R159, R160, R161, R166, R172, R173, R182, R198, R199, R200
