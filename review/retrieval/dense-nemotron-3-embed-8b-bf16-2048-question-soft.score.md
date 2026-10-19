# Retrieval score: `dense-nemotron-3-embed-8b-bf16-2048-question-soft.jsonl`

200 questions; missing from run: 0. Strict = answer pages checked on the image; lenient adds machine-found pages that print the answer's numbers. doc@10 = the right document anywhere in the top 10.

| group | n | strict_R@1 | strict_R@5 | strict_R@10 | strict_R@20 | strict_MRR@10 | lenient_R@10 | doc@10 |
|---|---|---|---|---|---|---|---|---|
| all | 200 | 0.38 | 0.67 | 0.76 | 0.81 | 0.50 | 0.79 | 0.94 |
| company:APARINDS | 64 | 0.45 | 0.69 | 0.83 | 0.86 | 0.58 | 0.84 | 0.92 |
| company:HEROMOTOCO | 54 | 0.43 | 0.72 | 0.78 | 0.83 | 0.54 | 0.80 | 0.94 |
| company:E2E | 43 | 0.12 | 0.47 | 0.63 | 0.72 | 0.27 | 0.70 | 0.91 |
| company:ESCONET | 21 | 0.38 | 0.67 | 0.67 | 0.76 | 0.50 | 0.71 | 1.00 |
| company:C2C | 18 | 0.56 | 0.89 | 0.89 | 0.89 | 0.68 | 0.89 | 0.94 |
| doctype:annual_reports | 111 | 0.38 | 0.69 | 0.75 | 0.80 | 0.51 | 0.80 | 0.96 |
| doctype:investor_presentations | 47 | 0.40 | 0.66 | 0.79 | 0.85 | 0.52 | 0.79 | 0.89 |
| doctype:concall_transcripts | 38 | 0.34 | 0.55 | 0.74 | 0.79 | 0.44 | 0.74 | 0.89 |
| doctype:periodic_results | 4 | 0.25 | 1.00 | 1.00 | 1.00 | 0.58 | 1.00 | 1.00 |
| evidence:table | 63 | 0.43 | 0.75 | 0.87 | 0.94 | 0.58 | 0.92 | 0.98 |
| evidence:concall | 33 | 0.39 | 0.61 | 0.79 | 0.79 | 0.50 | 0.79 | 0.88 |
| evidence:prose | 33 | 0.39 | 0.73 | 0.79 | 0.82 | 0.55 | 0.79 | 0.97 |
| evidence:statement | 25 | 0.24 | 0.64 | 0.72 | 0.80 | 0.40 | 0.76 | 0.92 |
| evidence:chart | 15 | 0.47 | 0.80 | 0.80 | 0.80 | 0.58 | 0.87 | 0.93 |
| evidence:multi | 15 | 0.00 | 0.13 | 0.20 | 0.40 | 0.06 | 0.20 | 0.93 |
| evidence:scan | 10 | 0.60 | 0.80 | 0.80 | 0.80 | 0.67 | 0.90 | 0.90 |
| evidence:kpi | 6 | 0.50 | 0.67 | 0.67 | 0.83 | 0.58 | 0.67 | 0.67 |
| hard:decoy_years | 63 | 0.35 | 0.65 | 0.73 | 0.84 | 0.47 | 0.79 | 0.94 |
| hard:standalone_vs_consolidated | 22 | 0.27 | 0.59 | 0.59 | 0.73 | 0.38 | 0.68 | 1.00 |
| hard:cross_doc | 17 | 0.00 | 0.12 | 0.24 | 0.41 | 0.06 | 0.24 | 0.82 |
| hard:spoken_numbers | 16 | 0.25 | 0.50 | 0.69 | 0.69 | 0.36 | 0.69 | 0.88 |
| hard:chart_labels | 14 | 0.43 | 0.79 | 0.79 | 0.79 | 0.55 | 0.86 | 0.93 |
| hard:indian_grouping | 14 | 0.36 | 0.71 | 0.93 | 0.93 | 0.52 | 0.93 | 1.00 |
| hard:multi_hop | 14 | 0.00 | 0.07 | 0.14 | 0.36 | 0.03 | 0.14 | 0.93 |
| hard:slide_table | 13 | 0.46 | 0.77 | 0.92 | 0.92 | 0.59 | 0.92 | 0.92 |
| hard:lakhs_unit | 11 | 0.27 | 0.64 | 0.82 | 0.91 | 0.43 | 0.91 | 0.91 |
| hard:footnote | 10 | 0.40 | 0.70 | 0.80 | 0.90 | 0.51 | 0.80 | 0.90 |
| hard:image_only_page | 10 | 0.60 | 0.80 | 0.80 | 0.80 | 0.67 | 0.90 | 0.90 |
| hard:no_numbers | 10 | 0.30 | 0.50 | 0.80 | 0.80 | 0.42 | 0.80 | 0.90 |
| hard:period_format | 10 | 0.40 | 0.60 | 0.70 | 0.70 | 0.50 | 0.70 | 0.80 |
| style:paraphrase | 140 | 0.42 | 0.68 | 0.78 | 0.82 | 0.54 | 0.81 | 0.93 |
| style:exact | 25 | 0.36 | 0.88 | 0.92 | 1.00 | 0.59 | 0.96 | 0.96 |
| style:vague | 20 | 0.35 | 0.70 | 0.85 | 0.85 | 0.49 | 0.85 | 0.95 |
| style:analytical | 15 | 0.00 | 0.13 | 0.20 | 0.40 | 0.06 | 0.20 | 0.93 |

## Paired comparison vs `dense-voyage-4-large-2048-question-soft.jsonl` (strict Recall@10)

Only this run finds: 6 (R021, R028, R061, R063, R071, R098)  
Only the other finds: 15 (R002, R004, R054, R055, R090, R125, R137, R142, R143, R146, R147, R151, R158, R166, R168)  
Ties: 179; exact sign test p = 0.078

## Not found in the top 10 (strict): 48

R002, R004, R013, R023, R029, R030, R050, R054, R055, R062, R064, R068, R073, R076, R079, R083, R090, R105, R107, R115, R116, R117, R118, R122, R125, R137, R142, R143, R144, R145, R146, R147, R151, R156, R157, R158, R159, R160, R161, R163, R166, R168, R172, R173, R179, R182, R199, R200
