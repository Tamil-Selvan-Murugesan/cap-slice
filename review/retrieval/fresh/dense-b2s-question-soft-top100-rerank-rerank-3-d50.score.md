# Retrieval score: `dense-b2s-question-soft-top100-rerank-rerank-3-d50.jsonl`

50 questions; missing from run: 0. Strict = answer pages checked on the image; lenient adds machine-found pages that print the answer's numbers. doc@10 = the right document anywhere in the top 10.

| group | n | strict_R@1 | strict_R@5 | strict_R@10 | strict_R@20 | strict_MRR@10 | lenient_R@10 | doc@10 |
|---|---|---|---|---|---|---|---|---|
| all | 50 | 0.56 | 0.80 | 0.90 | 0.92 | 0.68 | 0.90 | 0.96 |
| company:APARINDS | 17 | 0.41 | 0.65 | 0.76 | 0.82 | 0.53 | 0.76 | 0.88 |
| company:E2E | 14 | 0.57 | 0.93 | 0.93 | 0.93 | 0.73 | 0.93 | 1.00 |
| company:ESCONET | 9 | 0.56 | 0.78 | 1.00 | 1.00 | 0.66 | 1.00 | 1.00 |
| company:HEROMOTOCO | 6 | 0.67 | 0.83 | 1.00 | 1.00 | 0.77 | 1.00 | 1.00 |
| company:C2C | 4 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| doctype:annual_reports | 21 | 0.52 | 0.76 | 0.95 | 1.00 | 0.65 | 0.95 | 1.00 |
| doctype:investor_presentations | 19 | 0.47 | 0.79 | 0.84 | 0.84 | 0.62 | 0.84 | 0.89 |
| doctype:concall_transcripts | 9 | 0.78 | 0.89 | 0.89 | 0.89 | 0.83 | 0.89 | 1.00 |
| doctype:periodic_results | 1 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| evidence:chart | 14 | 0.71 | 0.86 | 0.86 | 0.86 | 0.77 | 0.86 | 0.86 |
| evidence:multi_page | 14 | 0.00 | 0.43 | 0.79 | 0.86 | 0.22 | 0.79 | 1.00 |
| evidence:concall | 8 | 0.88 | 1.00 | 1.00 | 1.00 | 0.94 | 1.00 | 1.00 |
| evidence:kpi | 4 | 0.50 | 1.00 | 1.00 | 1.00 | 0.75 | 1.00 | 1.00 |
| evidence:prose | 4 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| evidence:statement | 3 | 0.67 | 1.00 | 1.00 | 1.00 | 0.78 | 1.00 | 1.00 |
| evidence:table | 2 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| evidence:scan | 1 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| hard:chart_labels | 18 | 0.56 | 0.72 | 0.83 | 0.83 | 0.64 | 0.83 | 0.89 |
| hard:decoy_years | 14 | 0.71 | 0.79 | 0.86 | 0.86 | 0.75 | 0.86 | 0.86 |
| style:paraphrase | 47 | 0.53 | 0.79 | 0.89 | 0.91 | 0.65 | 0.89 | 0.96 |
| style:exact | 3 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |

## Not found in the top 10 (strict): 5

F015, F016, F022, F030, F031
