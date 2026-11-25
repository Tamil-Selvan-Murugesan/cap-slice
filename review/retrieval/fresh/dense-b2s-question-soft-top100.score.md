# Retrieval score: `dense-b2s-question-soft-top100.jsonl`

50 questions; missing from run: 0. Strict = answer pages checked on the image; lenient adds machine-found pages that print the answer's numbers. doc@10 = the right document anywhere in the top 10.

| group | n | strict_R@1 | strict_R@5 | strict_R@10 | strict_R@20 | strict_MRR@10 | lenient_R@10 | doc@10 |
|---|---|---|---|---|---|---|---|---|
| all | 50 | 0.38 | 0.66 | 0.74 | 0.86 | 0.50 | 0.74 | 0.84 |
| company:APARINDS | 17 | 0.18 | 0.35 | 0.47 | 0.71 | 0.27 | 0.47 | 0.65 |
| company:E2E | 14 | 0.36 | 0.79 | 0.86 | 0.93 | 0.57 | 0.86 | 0.93 |
| company:ESCONET | 9 | 0.44 | 0.67 | 0.78 | 0.89 | 0.53 | 0.78 | 0.89 |
| company:HEROMOTOCO | 6 | 0.50 | 1.00 | 1.00 | 1.00 | 0.64 | 1.00 | 1.00 |
| company:C2C | 4 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| doctype:annual_reports | 21 | 0.48 | 0.81 | 0.90 | 0.90 | 0.63 | 0.90 | 1.00 |
| doctype:investor_presentations | 19 | 0.16 | 0.42 | 0.53 | 0.84 | 0.28 | 0.53 | 0.63 |
| doctype:concall_transcripts | 9 | 0.56 | 0.78 | 0.78 | 0.78 | 0.63 | 0.78 | 0.89 |
| doctype:periodic_results | 1 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| evidence:chart | 14 | 0.36 | 0.50 | 0.57 | 0.86 | 0.42 | 0.57 | 0.57 |
| evidence:multi_page | 14 | 0.00 | 0.43 | 0.64 | 0.71 | 0.22 | 0.64 | 1.00 |
| evidence:concall | 8 | 0.62 | 0.88 | 0.88 | 0.88 | 0.71 | 0.88 | 0.88 |
| evidence:kpi | 4 | 0.25 | 0.75 | 0.75 | 1.00 | 0.46 | 0.75 | 0.75 |
| evidence:prose | 4 | 0.75 | 1.00 | 1.00 | 1.00 | 0.88 | 1.00 | 1.00 |
| evidence:statement | 3 | 0.67 | 1.00 | 1.00 | 1.00 | 0.78 | 1.00 | 1.00 |
| evidence:table | 2 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| evidence:scan | 1 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| hard:chart_labels | 18 | 0.28 | 0.44 | 0.56 | 0.78 | 0.35 | 0.56 | 0.67 |
| hard:decoy_years | 14 | 0.57 | 0.64 | 0.71 | 0.86 | 0.60 | 0.71 | 0.71 |
| style:paraphrase | 47 | 0.38 | 0.68 | 0.77 | 0.85 | 0.51 | 0.77 | 0.87 |
| style:exact | 3 | 0.33 | 0.33 | 0.33 | 1.00 | 0.33 | 0.33 | 0.33 |

## Not found in the top 10 (strict): 13

F003, F004, F008, F009, F014, F015, F016, F022, F024, F029, F030, F031, F033
