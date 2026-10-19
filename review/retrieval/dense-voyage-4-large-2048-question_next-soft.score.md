# Retrieval score: `dense-voyage-4-large-2048-question_next-soft.jsonl`

200 questions; missing from run: 0. Strict = answer pages checked on the image; lenient adds machine-found pages that print the answer's numbers. doc@10 = the right document anywhere in the top 10.

| group | n | strict_R@1 | strict_R@5 | strict_R@10 | strict_R@20 | strict_MRR@10 | lenient_R@10 | doc@10 |
|---|---|---|---|---|---|---|---|---|
| all | 200 | 0.36 | 0.69 | 0.78 | 0.86 | 0.50 | 0.81 | 0.92 |
| company:APARINDS | 64 | 0.30 | 0.72 | 0.81 | 0.88 | 0.47 | 0.83 | 0.89 |
| company:HEROMOTOCO | 54 | 0.41 | 0.67 | 0.72 | 0.81 | 0.51 | 0.78 | 0.94 |
| company:E2E | 43 | 0.30 | 0.65 | 0.81 | 0.91 | 0.47 | 0.84 | 0.95 |
| company:ESCONET | 21 | 0.43 | 0.52 | 0.62 | 0.76 | 0.48 | 0.67 | 0.76 |
| company:C2C | 18 | 0.50 | 0.89 | 0.89 | 0.94 | 0.65 | 0.89 | 1.00 |
| doctype:annual_reports | 111 | 0.36 | 0.72 | 0.79 | 0.84 | 0.51 | 0.84 | 0.97 |
| doctype:investor_presentations | 47 | 0.30 | 0.57 | 0.70 | 0.89 | 0.42 | 0.72 | 0.81 |
| doctype:concall_transcripts | 38 | 0.39 | 0.68 | 0.79 | 0.87 | 0.52 | 0.79 | 0.87 |
| doctype:periodic_results | 4 | 0.75 | 1.00 | 1.00 | 1.00 | 0.83 | 1.00 | 1.00 |
| evidence:table | 63 | 0.33 | 0.68 | 0.87 | 0.97 | 0.50 | 0.92 | 0.94 |
| evidence:concall | 33 | 0.45 | 0.76 | 0.88 | 0.91 | 0.59 | 0.88 | 0.91 |
| evidence:prose | 33 | 0.33 | 0.73 | 0.76 | 0.82 | 0.48 | 0.76 | 0.97 |
| evidence:statement | 25 | 0.40 | 0.76 | 0.76 | 0.88 | 0.53 | 0.84 | 0.92 |
| evidence:chart | 15 | 0.40 | 0.80 | 0.80 | 0.80 | 0.54 | 0.87 | 0.93 |
| evidence:multi | 15 | 0.00 | 0.07 | 0.13 | 0.40 | 0.03 | 0.13 | 0.73 |
| evidence:scan | 10 | 0.70 | 0.90 | 0.90 | 0.90 | 0.78 | 0.90 | 1.00 |
| evidence:kpi | 6 | 0.33 | 0.67 | 0.67 | 0.83 | 0.50 | 0.67 | 0.67 |
| hard:decoy_years | 63 | 0.37 | 0.73 | 0.83 | 0.90 | 0.51 | 0.87 | 0.94 |
| hard:standalone_vs_consolidated | 22 | 0.27 | 0.59 | 0.64 | 0.73 | 0.39 | 0.73 | 0.95 |
| hard:cross_doc | 17 | 0.00 | 0.29 | 0.35 | 0.53 | 0.11 | 0.35 | 0.82 |
| hard:spoken_numbers | 16 | 0.44 | 0.69 | 0.75 | 0.81 | 0.54 | 0.75 | 0.81 |
| hard:chart_labels | 14 | 0.36 | 0.79 | 0.79 | 0.79 | 0.51 | 0.86 | 0.93 |
| hard:indian_grouping | 14 | 0.21 | 0.64 | 0.86 | 0.93 | 0.43 | 0.93 | 0.86 |
| hard:multi_hop | 14 | 0.00 | 0.07 | 0.14 | 0.36 | 0.03 | 0.14 | 0.79 |
| hard:slide_table | 13 | 0.23 | 0.46 | 0.62 | 0.92 | 0.35 | 0.69 | 0.77 |
| hard:lakhs_unit | 11 | 0.45 | 0.91 | 0.91 | 1.00 | 0.65 | 0.91 | 0.91 |
| hard:footnote | 10 | 0.10 | 0.80 | 0.90 | 0.90 | 0.35 | 0.90 | 1.00 |
| hard:image_only_page | 10 | 0.70 | 0.90 | 0.90 | 0.90 | 0.78 | 0.90 | 1.00 |
| hard:no_numbers | 10 | 0.30 | 0.70 | 0.90 | 0.90 | 0.49 | 0.90 | 1.00 |
| hard:period_format | 10 | 0.50 | 0.60 | 0.70 | 0.80 | 0.56 | 0.70 | 0.80 |
| style:paraphrase | 140 | 0.39 | 0.74 | 0.84 | 0.90 | 0.54 | 0.86 | 0.91 |
| style:exact | 25 | 0.36 | 0.72 | 0.80 | 0.88 | 0.50 | 0.88 | 0.96 |
| style:vague | 20 | 0.40 | 0.70 | 0.80 | 0.90 | 0.53 | 0.80 | 1.00 |
| style:analytical | 15 | 0.00 | 0.07 | 0.13 | 0.40 | 0.03 | 0.13 | 0.73 |

## Paired comparison vs `bm25-mineru_advanced-question_next-soft.jsonl` (strict Recall@10)

Only this run finds: 41 (R002, R010, R014, R015, R032, R045, R048, R052, R055, R058, R072, R075, R100, R106, R112, R119, R120, R121, R125, R134, R137, R141, R142, R143, R147, R150, R151, R152, R155, R158, R160, R162, R164, R166, R167, R176, R177, R180, R184, R191, R195)  
Only the other finds: 8 (R004, R021, R023, R098, R107, R170, R171, R181)  
Ties: 151; exact sign test p = 0.000

## Not found in the top 10 (strict): 45

R004, R013, R021, R022, R023, R028, R029, R050, R061, R062, R063, R064, R068, R071, R073, R076, R079, R083, R088, R090, R098, R105, R107, R115, R116, R117, R118, R122, R127, R136, R144, R145, R156, R159, R161, R163, R170, R171, R172, R173, R179, R181, R182, R199, R200
