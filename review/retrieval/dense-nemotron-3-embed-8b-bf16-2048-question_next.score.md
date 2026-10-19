# Retrieval score: `dense-nemotron-3-embed-8b-bf16-2048-question_next.jsonl`

200 questions; missing from run: 0. Strict = answer pages checked on the image; lenient adds machine-found pages that print the answer's numbers. doc@10 = the right document anywhere in the top 10.

| group | n | strict_R@1 | strict_R@5 | strict_R@10 | strict_R@20 | strict_MRR@10 | lenient_R@10 | doc@10 |
|---|---|---|---|---|---|---|---|---|
| all | 200 | 0.35 | 0.63 | 0.70 | 0.81 | 0.46 | 0.74 | 0.93 |
| company:APARINDS | 64 | 0.42 | 0.67 | 0.77 | 0.84 | 0.53 | 0.80 | 0.91 |
| company:HEROMOTOCO | 54 | 0.43 | 0.69 | 0.74 | 0.83 | 0.52 | 0.78 | 0.96 |
| company:E2E | 43 | 0.14 | 0.42 | 0.51 | 0.72 | 0.25 | 0.58 | 0.86 |
| company:ESCONET | 21 | 0.29 | 0.62 | 0.67 | 0.76 | 0.42 | 0.71 | 1.00 |
| company:C2C | 18 | 0.50 | 0.83 | 0.83 | 0.89 | 0.63 | 0.83 | 0.94 |
| doctype:annual_reports | 111 | 0.37 | 0.65 | 0.69 | 0.80 | 0.47 | 0.77 | 0.96 |
| doctype:investor_presentations | 47 | 0.38 | 0.62 | 0.72 | 0.85 | 0.49 | 0.72 | 0.87 |
| doctype:concall_transcripts | 38 | 0.29 | 0.55 | 0.66 | 0.76 | 0.39 | 0.66 | 0.87 |
| doctype:periodic_results | 4 | 0.25 | 1.00 | 1.00 | 1.00 | 0.58 | 1.00 | 1.00 |
| evidence:table | 63 | 0.40 | 0.68 | 0.75 | 0.92 | 0.52 | 0.84 | 0.97 |
| evidence:concall | 33 | 0.33 | 0.61 | 0.73 | 0.76 | 0.45 | 0.73 | 0.85 |
| evidence:prose | 33 | 0.36 | 0.70 | 0.76 | 0.79 | 0.49 | 0.76 | 0.94 |
| evidence:statement | 25 | 0.24 | 0.56 | 0.68 | 0.80 | 0.37 | 0.72 | 0.92 |
| evidence:chart | 15 | 0.47 | 0.80 | 0.80 | 0.80 | 0.57 | 0.87 | 0.93 |
| evidence:multi | 15 | 0.00 | 0.07 | 0.13 | 0.47 | 0.03 | 0.13 | 0.93 |
| evidence:scan | 10 | 0.70 | 0.90 | 0.90 | 0.90 | 0.77 | 0.90 | 1.00 |
| evidence:kpi | 6 | 0.50 | 0.67 | 0.67 | 0.83 | 0.58 | 0.67 | 0.67 |
| hard:decoy_years | 63 | 0.35 | 0.57 | 0.65 | 0.84 | 0.44 | 0.75 | 0.94 |
| hard:standalone_vs_consolidated | 22 | 0.27 | 0.50 | 0.59 | 0.73 | 0.36 | 0.68 | 1.00 |
| hard:cross_doc | 17 | 0.00 | 0.12 | 0.18 | 0.47 | 0.03 | 0.18 | 0.88 |
| hard:spoken_numbers | 16 | 0.12 | 0.50 | 0.62 | 0.62 | 0.26 | 0.62 | 0.88 |
| hard:chart_labels | 14 | 0.43 | 0.79 | 0.79 | 0.79 | 0.54 | 0.86 | 0.93 |
| hard:indian_grouping | 14 | 0.36 | 0.71 | 0.86 | 0.93 | 0.51 | 0.93 | 1.00 |
| hard:multi_hop | 14 | 0.00 | 0.07 | 0.07 | 0.43 | 0.02 | 0.07 | 0.93 |
| hard:slide_table | 13 | 0.46 | 0.69 | 0.77 | 0.92 | 0.55 | 0.77 | 0.85 |
| hard:lakhs_unit | 11 | 0.18 | 0.64 | 0.82 | 1.00 | 0.40 | 0.82 | 0.91 |
| hard:footnote | 10 | 0.20 | 0.70 | 0.80 | 0.80 | 0.39 | 0.80 | 0.90 |
| hard:image_only_page | 10 | 0.70 | 0.90 | 0.90 | 0.90 | 0.77 | 0.90 | 1.00 |
| hard:no_numbers | 10 | 0.30 | 0.50 | 0.70 | 0.80 | 0.41 | 0.70 | 0.80 |
| hard:period_format | 10 | 0.30 | 0.60 | 0.70 | 0.70 | 0.45 | 0.70 | 0.80 |
| style:paraphrase | 140 | 0.39 | 0.66 | 0.72 | 0.81 | 0.50 | 0.76 | 0.92 |
| style:exact | 25 | 0.36 | 0.84 | 0.88 | 1.00 | 0.53 | 0.96 | 0.96 |
| style:vague | 20 | 0.35 | 0.60 | 0.75 | 0.85 | 0.44 | 0.75 | 0.90 |
| style:analytical | 15 | 0.00 | 0.07 | 0.13 | 0.47 | 0.03 | 0.13 | 0.93 |

## Paired comparison vs `dense-voyage-4-large-2048-question_next.jsonl` (strict Recall@10)

Only this run finds: 14 (R021, R022, R061, R066, R069, R071, R078, R086, R087, R098, R099, R170, R171, R181)  
Only the other finds: 22 (R002, R006, R030, R054, R055, R075, R120, R125, R130, R137, R142, R143, R146, R147, R150, R151, R152, R158, R160, R166, R168, R185)  
Ties: 164; exact sign test p = 0.243

## Not found in the top 10 (strict): 60

R002, R004, R006, R013, R023, R028, R029, R030, R040, R050, R054, R055, R062, R063, R064, R068, R073, R075, R076, R079, R083, R088, R090, R105, R107, R115, R116, R117, R118, R120, R122, R125, R127, R130, R136, R137, R142, R143, R144, R145, R146, R147, R150, R151, R152, R156, R158, R159, R160, R161, R163, R166, R168, R172, R173, R179, R182, R185, R199, R200
