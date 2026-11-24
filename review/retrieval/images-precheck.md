# Images: pre-round check (2026-11-24)

Before spending 3–4 days on round 3 (images), we checked whether the 200 questions could show a difference,
and why the image questions that still miss do miss. Result: **round 3 is moved after the answer step; the
reranker (round 4) runs next.**

## 1. The question set can't separate image methods yet

With the round-2 winner (b2, question-based soft filters):

| Evidence | Questions | Found in top 10 | Missed |
|---|---|---|---|
| Charts | 15 | 12 | 3 (R029, R083, R172) |
| KPI tiles | 6 | 5 | 1 (R023) |
| Scanned pages | 10 | 9 | 1 |

At most about four questions can move, so even a perfect image method could not pass a sign test. Of all 27
questions b2 still misses, only these 4–5 involve images (10 are multi-page, 5 prose, 3 tables, 2 statements,
2 concall). Retrieval already finds most chart pages from the slide title and surrounding words, even when the
chart's numbers are not in the text.

## 2. The real image problem shows up after retrieval

In 3 of the 4 chart/KPI misses the answer number is **not anywhere in MinerU's output** — not in the chunks and
not in MinerU's raw page output before our clean-up. The page can be found, but nothing downstream could quote
the value. That is measured at the answer step (answer accuracy), not in a retrieval round.

## 3. Reusing MinerU's picture descriptions is ruled out

MinerU advanced writes its own picture descriptions (`<details>` / Mermaid blocks on 2,324 pages, removed by
`page_clean.py` because they invent values). We hoped option B could simply reuse them. **They don't contain
these values** — the three pages have no description at all. Option B would need a new vision-model pass over
the image-heavy pages.

## 4. But the numbers are printed as text in the PDF

Checking the PDF text layer (PyMuPDF) on the same pages changed the picture: **all three values are real text
in the PDF.** These are vector charts whose data labels are text objects; MinerU, which reads a rendered image of
the page, kept the slide title and dropped the whole chart.

| Question | Page | PDF text layer | MinerU output |
|---|---|---|---|
| R029 APAR conductor EBITDA per tonne, FY2023 | APAR deck Aug-2023-a p.98 | `164 171 102 184 706 / 8,960 10,790 7,926 17,095 45,114` (bar labels, then axis ticks) | Title and two bullet points, no numbers |
| R083 Hero two-wheeler sales 2012-13 vs 2011-12 | Hero AR FY2012-13 p.8 | `12-13 … 08-09 / 6,075,583 6,235,205 5,402,444 4,600,130 3,722,000` | `## Performing for the Long Term` only |
| R172 Esconet clients FY25 | Esconet deck Sep-2025-a p.18 | `384 437 500 / FY23 FY24 FY25 / Clients`, plus EBITDA/PAT margins | `## CONTINUING CONSISTENT PERFORMANCE (CONSOLIDATED)` only |

So for vector charts this is a **parser gap with a possibly cheap fix**: the values exist in the PDF and could be
recovered from the text layer without any vision model. The catch is structure — the text layer gives the labels
in drawing order (values, then years, then axis ticks), so pairing a value with its year and series is not
guaranteed. That is the same risk PROGRESS warns about ("don't snap numbers to nearby text"), so recovered values
would be flagged and checked before the answer step may quote them. Image charts (bitmaps) are a separate case and
still need a vision model.

**Scale is not measured yet.** A rough scan (pages with ≥ 5 printed numbers where half or more are missing from
MinerU's output) flags 330 of 6,825 pages, but spot checks show most flags are noise: cover-letter letterheads
whose phone numbers and CINs are split differently, chart axis ticks, and garbled text layers. A proper count
(e.g. only numbers inside drawn chart regions) is a to-do before deciding the fix.

## Decision

- Round 4 (reranker) next; it targets most of what is left (multi-page questions, look-alike pages ranked 11–20).
- Images move after the answer step and are measured as answer accuracy on chart/KPI questions; ~25 chart/KPI
  questions to be added then (the target was ~40, we have 21), read off page images as always.
- Logged as parser defect P12 in `bugs_resolved.md` (open).
