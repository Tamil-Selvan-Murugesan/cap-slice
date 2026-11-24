# Retrieval score: `dense-voyage-4-large-2048__r2-d-question.jsonl`

200 questions; missing from run: 0. Strict = answer pages checked on the image; lenient adds machine-found pages that print the answer's numbers. doc@10 = the right document anywhere in the top 10.

| group | n | strict_R@1 | strict_R@5 | strict_R@10 | strict_R@20 | strict_MRR@10 | lenient_R@10 | doc@10 |
|---|---|---|---|---|---|---|---|---|
| all | 200 | 0.38 | 0.70 | 0.79 | 0.85 | 0.52 | 0.81 | 0.92 |
| company:APARINDS | 64 | 0.34 | 0.77 | 0.81 | 0.88 | 0.52 | 0.81 | 0.91 |
| company:HEROMOTOCO | 54 | 0.39 | 0.72 | 0.76 | 0.80 | 0.53 | 0.80 | 0.94 |
| company:E2E | 43 | 0.30 | 0.58 | 0.74 | 0.86 | 0.44 | 0.79 | 0.88 |
| company:ESCONET | 21 | 0.43 | 0.62 | 0.76 | 0.81 | 0.51 | 0.76 | 0.90 |
| company:C2C | 18 | 0.56 | 0.83 | 0.89 | 0.94 | 0.68 | 0.89 | 1.00 |
| doctype:annual_reports | 111 | 0.39 | 0.76 | 0.79 | 0.82 | 0.54 | 0.83 | 0.95 |
| doctype:investor_presentations | 47 | 0.36 | 0.60 | 0.79 | 0.85 | 0.48 | 0.79 | 0.89 |
| doctype:concall_transcripts | 38 | 0.32 | 0.66 | 0.74 | 0.92 | 0.48 | 0.74 | 0.87 |
| doctype:periodic_results | 4 | 0.75 | 1.00 | 1.00 | 1.00 | 0.88 | 1.00 | 1.00 |
| evidence:table | 63 | 0.40 | 0.83 | 0.94 | 0.97 | 0.58 | 0.95 | 0.97 |
| evidence:concall | 33 | 0.36 | 0.76 | 0.79 | 0.94 | 0.54 | 0.79 | 0.88 |
| evidence:prose | 33 | 0.39 | 0.67 | 0.73 | 0.76 | 0.52 | 0.73 | 0.91 |
| evidence:statement | 25 | 0.36 | 0.72 | 0.80 | 0.92 | 0.51 | 0.84 | 0.88 |
| evidence:chart | 15 | 0.47 | 0.80 | 0.80 | 0.80 | 0.59 | 0.87 | 0.93 |
| evidence:multi | 15 | 0.00 | 0.00 | 0.20 | 0.33 | 0.03 | 0.20 | 0.93 |
| evidence:scan | 10 | 0.50 | 0.70 | 0.80 | 0.80 | 0.59 | 0.90 | 0.90 |
| evidence:kpi | 6 | 0.67 | 0.83 | 0.83 | 0.83 | 0.75 | 0.83 | 0.83 |
| hard:decoy_years | 63 | 0.37 | 0.81 | 0.86 | 0.90 | 0.54 | 0.89 | 0.92 |
| hard:standalone_vs_consolidated | 22 | 0.27 | 0.64 | 0.73 | 0.82 | 0.41 | 0.77 | 0.95 |
| hard:cross_doc | 17 | 0.00 | 0.12 | 0.24 | 0.41 | 0.07 | 0.24 | 0.82 |
| hard:spoken_numbers | 16 | 0.38 | 0.69 | 0.75 | 0.88 | 0.52 | 0.75 | 0.88 |
| hard:chart_labels | 14 | 0.43 | 0.79 | 0.79 | 0.79 | 0.57 | 0.86 | 0.93 |
| hard:indian_grouping | 14 | 0.43 | 0.86 | 0.93 | 0.93 | 0.62 | 0.93 | 0.93 |
| hard:multi_hop | 14 | 0.00 | 0.00 | 0.14 | 0.29 | 0.02 | 0.14 | 0.93 |
| hard:slide_table | 13 | 0.38 | 0.54 | 0.85 | 1.00 | 0.45 | 0.85 | 0.92 |
| hard:lakhs_unit | 11 | 0.55 | 0.82 | 0.82 | 0.91 | 0.68 | 0.91 | 0.82 |
| hard:footnote | 10 | 0.40 | 0.60 | 0.80 | 0.80 | 0.53 | 0.80 | 0.90 |
| hard:image_only_page | 10 | 0.50 | 0.70 | 0.80 | 0.80 | 0.59 | 0.90 | 0.90 |
| hard:no_numbers | 10 | 0.40 | 0.70 | 0.70 | 0.90 | 0.53 | 0.70 | 0.90 |
| hard:period_format | 10 | 0.30 | 0.60 | 0.80 | 0.90 | 0.46 | 0.80 | 0.90 |
| style:paraphrase | 140 | 0.39 | 0.77 | 0.84 | 0.89 | 0.55 | 0.86 | 0.91 |
| style:exact | 25 | 0.48 | 0.80 | 0.88 | 0.92 | 0.61 | 0.92 | 1.00 |
| style:vague | 20 | 0.40 | 0.65 | 0.75 | 0.85 | 0.54 | 0.75 | 0.90 |
| style:analytical | 15 | 0.00 | 0.00 | 0.20 | 0.33 | 0.03 | 0.20 | 0.93 |

## Paired comparison vs `dense-voyage-4-large-2048-question.jsonl` (strict Recall@10)

Only this run finds: 8 (R013, R069, R078, R087, R088, R099, R105, R161)  
Only the other finds: 6 (R058, R080, R127, R150, R151, R152)  
Ties: 186; exact sign test p = 0.791

## Not found in the top 10 (strict): 43

R021, R023, R028, R029, R030, R040, R050, R058, R061, R062, R063, R064, R068, R071, R073, R076, R079, R080, R083, R098, R107, R115, R116, R117, R118, R122, R127, R144, R145, R150, R151, R152, R156, R157, R159, R160, R163, R172, R173, R179, R182, R199, R200
