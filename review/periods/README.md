# Period check

`uv run cap-slice-periods` → `check.csv`: one row per downloaded document with the normalised period
(`src/cap_slice/periods.py`) and the periods the document itself states in its first 10 pages (PDF text
layer; MinerU advanced cache for pages without one).

| Status | Meaning | Documents (2026-10-19) |
|---|---|---|
| `agree` | the document states exactly the normalised period | 173 |
| `agree_fy` | same fiscal year, a different quarter/half named (e.g. a Q2 deck that says "H1 FY17") | 5 |
| `no_evidence` | no period stated: general corporate decks (38), investor-day / broker-conference calls (8), 2 others | 48 |
| `disagree` | the document states a different fiscal year | 3 |

The three disagreements, checked by hand:
- APAR `Jul-2020` concall — on Q4 FY20 results (delayed by COVID), not Q1 FY21 → override.
- Esconet `Aug-2026` concall — "Q1-FY26-27 Financial Results", quarter ended June 30, 2026; an SME company
  now holding quarterly calls, so the half-year rule (H2 FY26) is wrong → override.
- E2E `FY2021-22` annual report — flagged because the parser read the image-only cover "ANNUAL REPORT 2022"
  as "2022-23"; the body says year ended March 2022 132 times → rule correct, no override.

Overrides live in `data/period_overrides.csv` (path, fiscal_year, period, note) and are applied by
`normalise_doc()`; `final_fy` / `final_period` in `check.csv` show the result.
