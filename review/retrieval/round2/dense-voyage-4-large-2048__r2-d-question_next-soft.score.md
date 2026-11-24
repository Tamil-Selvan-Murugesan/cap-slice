# Retrieval score: `dense-voyage-4-large-2048__r2-d-question_next-soft.jsonl`

200 questions; missing from run: 0. Strict = answer pages checked on the image; lenient adds machine-found pages that print the answer's numbers. doc@10 = the right document anywhere in the top 10.

| group | n | strict_R@1 | strict_R@5 | strict_R@10 | strict_R@20 | strict_MRR@10 | lenient_R@10 | doc@10 |
|---|---|---|---|---|---|---|---|---|
| all | 200 | 0.34 | 0.68 | 0.76 | 0.85 | 0.48 | 0.79 | 0.91 |
| company:APARINDS | 64 | 0.25 | 0.75 | 0.80 | 0.89 | 0.46 | 0.81 | 0.91 |
| company:HEROMOTOCO | 54 | 0.37 | 0.70 | 0.76 | 0.80 | 0.52 | 0.81 | 0.98 |
| company:E2E | 43 | 0.30 | 0.56 | 0.70 | 0.88 | 0.42 | 0.72 | 0.86 |
| company:ESCONET | 21 | 0.38 | 0.48 | 0.62 | 0.76 | 0.44 | 0.67 | 0.76 |
| company:C2C | 18 | 0.56 | 0.83 | 0.89 | 0.94 | 0.68 | 0.89 | 1.00 |
| doctype:annual_reports | 111 | 0.34 | 0.72 | 0.79 | 0.84 | 0.50 | 0.84 | 0.98 |
| doctype:investor_presentations | 47 | 0.32 | 0.57 | 0.68 | 0.89 | 0.44 | 0.70 | 0.81 |
| doctype:concall_transcripts | 38 | 0.29 | 0.63 | 0.71 | 0.84 | 0.44 | 0.71 | 0.82 |
| doctype:periodic_results | 4 | 0.75 | 1.00 | 1.00 | 1.00 | 0.88 | 1.00 | 1.00 |
| evidence:table | 63 | 0.35 | 0.71 | 0.86 | 0.98 | 0.52 | 0.90 | 0.94 |
| evidence:concall | 33 | 0.33 | 0.73 | 0.76 | 0.85 | 0.50 | 0.76 | 0.85 |
| evidence:prose | 33 | 0.30 | 0.70 | 0.73 | 0.82 | 0.47 | 0.73 | 0.97 |
| evidence:statement | 25 | 0.32 | 0.72 | 0.76 | 0.88 | 0.48 | 0.84 | 0.92 |
| evidence:chart | 15 | 0.47 | 0.80 | 0.80 | 0.80 | 0.59 | 0.87 | 0.87 |
| evidence:multi | 15 | 0.00 | 0.00 | 0.20 | 0.40 | 0.03 | 0.20 | 0.80 |
| evidence:scan | 10 | 0.60 | 0.80 | 0.90 | 0.90 | 0.69 | 0.90 | 1.00 |
| evidence:kpi | 6 | 0.50 | 0.83 | 0.83 | 0.83 | 0.67 | 0.83 | 0.83 |
| hard:decoy_years | 63 | 0.35 | 0.75 | 0.84 | 0.90 | 0.52 | 0.89 | 0.95 |
| hard:standalone_vs_consolidated | 22 | 0.27 | 0.59 | 0.64 | 0.73 | 0.39 | 0.73 | 0.95 |
| hard:cross_doc | 17 | 0.00 | 0.18 | 0.35 | 0.53 | 0.10 | 0.35 | 0.82 |
| hard:spoken_numbers | 16 | 0.31 | 0.62 | 0.69 | 0.69 | 0.44 | 0.69 | 0.81 |
| hard:chart_labels | 14 | 0.43 | 0.79 | 0.79 | 0.79 | 0.57 | 0.86 | 0.86 |
| hard:indian_grouping | 14 | 0.36 | 0.79 | 0.86 | 0.93 | 0.57 | 0.93 | 0.93 |
| hard:multi_hop | 14 | 0.00 | 0.00 | 0.21 | 0.36 | 0.03 | 0.21 | 0.86 |
| hard:slide_table | 13 | 0.31 | 0.46 | 0.62 | 1.00 | 0.37 | 0.69 | 0.77 |
| hard:lakhs_unit | 11 | 0.45 | 0.91 | 0.91 | 1.00 | 0.65 | 0.91 | 0.91 |
| hard:footnote | 10 | 0.20 | 0.70 | 0.70 | 0.90 | 0.42 | 0.70 | 1.00 |
| hard:image_only_page | 10 | 0.60 | 0.80 | 0.90 | 0.90 | 0.69 | 0.90 | 1.00 |
| hard:no_numbers | 10 | 0.40 | 0.70 | 0.70 | 0.90 | 0.53 | 0.70 | 0.90 |
| hard:period_format | 10 | 0.20 | 0.50 | 0.70 | 0.90 | 0.38 | 0.70 | 0.80 |
| style:paraphrase | 140 | 0.35 | 0.73 | 0.80 | 0.89 | 0.51 | 0.83 | 0.91 |
| style:exact | 25 | 0.44 | 0.76 | 0.84 | 0.88 | 0.58 | 0.92 | 1.00 |
| style:vague | 20 | 0.35 | 0.70 | 0.75 | 0.90 | 0.52 | 0.75 | 0.90 |
| style:analytical | 15 | 0.00 | 0.00 | 0.20 | 0.40 | 0.03 | 0.20 | 0.80 |

## Paired comparison vs `dense-voyage-4-large-2048-question_next-soft.jsonl` (strict Recall@10)

Only this run finds: 4 (R022, R090, R105, R161)  
Only the other finds: 8 (R048, R058, R133, R137, R138, R150, R151, R152)  
Ties: 188; exact sign test p = 0.388

## Not found in the top 10 (strict): 49

R004, R013, R021, R023, R028, R029, R048, R050, R058, R061, R062, R063, R064, R068, R071, R073, R076, R079, R083, R088, R098, R107, R115, R116, R117, R118, R122, R127, R133, R136, R137, R138, R144, R145, R150, R151, R152, R156, R159, R163, R170, R171, R172, R173, R179, R181, R182, R199, R200
