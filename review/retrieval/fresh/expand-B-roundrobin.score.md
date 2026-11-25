# Retrieval score: `expand-B-roundrobin.jsonl`

50 questions; missing from run: 0. Strict = answer pages checked on the image; lenient adds machine-found pages that print the answer's numbers. doc@10 = the right document anywhere in the top 10.

| group | n | strict_R@1 | strict_R@5 | strict_R@10 | strict_R@20 | strict_MRR@10 | lenient_R@10 | doc@10 |
|---|---|---|---|---|---|---|---|---|
| all | 50 | 0.56 | 0.94 | 0.94 | 0.94 | 0.72 | 0.94 | 0.96 |
| company:APARINDS | 17 | 0.41 | 0.82 | 0.82 | 0.82 | 0.58 | 0.82 | 0.88 |
| company:E2E | 14 | 0.57 | 1.00 | 1.00 | 1.00 | 0.77 | 1.00 | 1.00 |
| company:ESCONET | 9 | 0.56 | 1.00 | 1.00 | 1.00 | 0.70 | 1.00 | 1.00 |
| company:HEROMOTOCO | 6 | 0.67 | 1.00 | 1.00 | 1.00 | 0.83 | 1.00 | 1.00 |
| company:C2C | 4 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| doctype:annual_reports | 21 | 0.52 | 1.00 | 1.00 | 1.00 | 0.71 | 1.00 | 1.00 |
| doctype:investor_presentations | 19 | 0.47 | 0.84 | 0.84 | 0.84 | 0.63 | 0.84 | 0.89 |
| doctype:concall_transcripts | 9 | 0.78 | 1.00 | 1.00 | 1.00 | 0.89 | 1.00 | 1.00 |
| doctype:periodic_results | 1 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| evidence:chart | 14 | 0.71 | 0.86 | 0.86 | 0.86 | 0.77 | 0.86 | 0.86 |
| evidence:multi_page | 14 | 0.00 | 0.93 | 0.93 | 0.93 | 0.38 | 0.93 | 1.00 |
| evidence:concall | 8 | 0.88 | 1.00 | 1.00 | 1.00 | 0.94 | 1.00 | 1.00 |
| evidence:kpi | 4 | 0.50 | 1.00 | 1.00 | 1.00 | 0.75 | 1.00 | 1.00 |
| evidence:prose | 4 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| evidence:statement | 3 | 0.67 | 1.00 | 1.00 | 1.00 | 0.78 | 1.00 | 1.00 |
| evidence:table | 2 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| evidence:scan | 1 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| hard:chart_labels | 18 | 0.56 | 0.83 | 0.83 | 0.83 | 0.66 | 0.83 | 0.89 |
| hard:decoy_years | 14 | 0.71 | 0.86 | 0.86 | 0.86 | 0.76 | 0.86 | 0.86 |
| style:paraphrase | 47 | 0.53 | 0.94 | 0.94 | 0.94 | 0.70 | 0.94 | 0.96 |
| style:exact | 3 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |

## Paired comparison vs `dense-b2s-question-soft-top100-rerank-rerank-3-d50.jsonl` (strict Recall@10)

Only this run finds: 2 (F022, F030)  
Only the other finds: 0 (-)  
Ties: 48; exact sign test p = 0.500

## Not found in the top 10 (strict): 3

F015, F016, F031
