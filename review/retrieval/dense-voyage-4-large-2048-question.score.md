# Retrieval score: `dense-voyage-4-large-2048-question.jsonl`

200 questions; missing from run: 0. Strict = answer pages checked on the image; lenient adds machine-found pages that print the answer's numbers. doc@10 = the right document anywhere in the top 10.

| group | n | strict_R@1 | strict_R@5 | strict_R@10 | strict_R@20 | strict_MRR@10 | lenient_R@10 | doc@10 |
|---|---|---|---|---|---|---|---|---|
| all | 200 | 0.39 | 0.71 | 0.78 | 0.83 | 0.52 | 0.81 | 0.92 |
| company:APARINDS | 64 | 0.38 | 0.70 | 0.81 | 0.88 | 0.52 | 0.83 | 0.91 |
| company:HEROMOTOCO | 54 | 0.37 | 0.65 | 0.67 | 0.72 | 0.48 | 0.72 | 0.89 |
| company:E2E | 43 | 0.33 | 0.72 | 0.81 | 0.86 | 0.49 | 0.86 | 0.95 |
| company:ESCONET | 21 | 0.48 | 0.71 | 0.76 | 0.81 | 0.56 | 0.76 | 0.90 |
| company:C2C | 18 | 0.50 | 0.89 | 0.89 | 0.94 | 0.66 | 0.89 | 1.00 |
| doctype:annual_reports | 111 | 0.39 | 0.74 | 0.75 | 0.77 | 0.53 | 0.80 | 0.91 |
| doctype:investor_presentations | 47 | 0.32 | 0.62 | 0.81 | 0.89 | 0.45 | 0.81 | 0.91 |
| doctype:concall_transcripts | 38 | 0.42 | 0.71 | 0.79 | 0.89 | 0.55 | 0.79 | 0.95 |
| doctype:periodic_results | 4 | 0.75 | 1.00 | 1.00 | 1.00 | 0.83 | 1.00 | 1.00 |
| evidence:table | 63 | 0.37 | 0.78 | 0.89 | 0.92 | 0.54 | 0.92 | 0.92 |
| evidence:concall | 33 | 0.48 | 0.79 | 0.88 | 0.91 | 0.62 | 0.88 | 0.94 |
| evidence:prose | 33 | 0.42 | 0.70 | 0.73 | 0.76 | 0.55 | 0.73 | 0.91 |
| evidence:statement | 25 | 0.40 | 0.72 | 0.76 | 0.84 | 0.52 | 0.84 | 0.88 |
| evidence:chart | 15 | 0.40 | 0.80 | 0.80 | 0.87 | 0.54 | 0.87 | 0.93 |
| evidence:multi | 15 | 0.00 | 0.13 | 0.13 | 0.40 | 0.04 | 0.13 | 1.00 |
| evidence:scan | 10 | 0.60 | 0.80 | 0.80 | 0.80 | 0.68 | 0.90 | 0.90 |
| evidence:kpi | 6 | 0.33 | 0.67 | 0.83 | 0.83 | 0.52 | 0.83 | 0.83 |
| hard:decoy_years | 63 | 0.35 | 0.75 | 0.78 | 0.83 | 0.50 | 0.84 | 0.86 |
| hard:standalone_vs_consolidated | 22 | 0.27 | 0.64 | 0.68 | 0.77 | 0.41 | 0.77 | 0.95 |
| hard:cross_doc | 17 | 0.00 | 0.24 | 0.24 | 0.47 | 0.09 | 0.24 | 0.94 |
| hard:spoken_numbers | 16 | 0.44 | 0.69 | 0.75 | 0.81 | 0.56 | 0.75 | 0.88 |
| hard:chart_labels | 14 | 0.36 | 0.79 | 0.79 | 0.86 | 0.51 | 0.86 | 0.93 |
| hard:indian_grouping | 14 | 0.29 | 0.79 | 0.93 | 0.93 | 0.49 | 0.93 | 0.93 |
| hard:multi_hop | 14 | 0.00 | 0.07 | 0.07 | 0.36 | 0.02 | 0.07 | 1.00 |
| hard:slide_table | 13 | 0.31 | 0.54 | 0.92 | 1.00 | 0.44 | 0.92 | 1.00 |
| hard:lakhs_unit | 11 | 0.55 | 0.82 | 0.91 | 0.91 | 0.69 | 1.00 | 0.91 |
| hard:footnote | 10 | 0.30 | 0.80 | 0.90 | 0.90 | 0.52 | 0.90 | 1.00 |
| hard:image_only_page | 10 | 0.60 | 0.80 | 0.80 | 0.80 | 0.68 | 0.90 | 0.90 |
| hard:no_numbers | 10 | 0.40 | 0.80 | 0.90 | 0.90 | 0.55 | 0.90 | 1.00 |
| hard:period_format | 10 | 0.50 | 0.70 | 0.80 | 0.90 | 0.60 | 0.80 | 0.90 |
| style:paraphrase | 140 | 0.42 | 0.76 | 0.83 | 0.86 | 0.56 | 0.86 | 0.89 |
| style:exact | 25 | 0.32 | 0.72 | 0.80 | 0.88 | 0.48 | 0.88 | 0.96 |
| style:vague | 20 | 0.50 | 0.75 | 0.85 | 0.90 | 0.62 | 0.85 | 1.00 |
| style:analytical | 15 | 0.00 | 0.13 | 0.13 | 0.40 | 0.04 | 0.13 | 1.00 |

## Paired comparison vs `bm25-mineru_advanced-question.jsonl` (strict Recall@10)

Only this run finds: 33 (R002, R010, R022, R032, R045, R052, R055, R058, R072, R075, R090, R100, R112, R120, R121, R125, R127, R134, R142, R143, R147, R150, R151, R152, R155, R158, R162, R166, R176, R177, R180, R184, R195)  
Only the other finds: 9 (R013, R021, R023, R069, R078, R087, R098, R099, R107)  
Ties: 158; exact sign test p = 0.000

## Not found in the top 10 (strict): 45

R013, R021, R023, R028, R029, R030, R040, R050, R061, R062, R063, R064, R068, R069, R071, R073, R076, R078, R079, R083, R087, R088, R098, R099, R105, R107, R115, R116, R117, R118, R122, R144, R145, R156, R157, R159, R160, R161, R163, R172, R173, R179, R182, R199, R200
