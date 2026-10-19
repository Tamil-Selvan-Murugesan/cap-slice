# Question reader

Rules-based reader (`src/cap_slice/query_reader.py`) on the 200 retrieval questions; reads only the question text. Year checked against the `period` column (what the question asks about, recorded when the set was built).

**First run, before any change (2026-10-19):** company 200/200; year right 180, wrong 6, none 14; doc type
right 28, wrong 1; hard company + year filter keeps an answer page for 186/200. Three general phrasings
were then fixed — `FY 25-26` read as FY25 and FY22; an event named by "investor day charts" or
"reiterated in May 2023" not recognised; a call named next to slides given a doc-type filter — giving
the numbers below. Because those fixes were made on this set, treat the result as slightly optimistic.

| | Count |
|---|---|
| Company read correctly | 200 / 200 |
| Year: read and right (includes the asked year) | 183 |
| Year: read but wrong | 3 |
| Year: none read (no year filter) | 14 |
| Doc type: read and right | 28 |
| Doc type: read but wrong | 0 |
| Doc type: none read | 172 |

**Does a hard filter keep an answer page?** (if not, the question cannot be answered under that filter)

| Filter | Keeps an answer page | Median pool (chunks of 40,593) |
|---|---|---|
| Company (question-based) | 200 / 200 | 16,122 |
| Company + year (question-based) | 189 / 200 | 996 |
| Company + year or the next year (question-based) | 196 / 200 | 1,811 |
| Company + year + doc type (question-based) | 189 / 200 | 886 |
| Company + year or the next year + doc type (question-based) | 196 / 200 | 1,534 |
| Company + year + doc type (answer key, upper bound) | 187 / 200 | 352 |

## Questions a question-based hard filter makes unanswerable: 11

| qid | question | period | read years | doc type | evidence |
|---|---|---|---|---|---|
| R030 | How much cash did APAR's operations generate in FY2023 on a consolidated basis? | FY2022-23 | 2023 |  | 'FY2023' |
| R040 | After APAR re-priced its employee stock options in 2008, what was the new exercise price, and how many options eventually lapsed unexercised? | FY2012-13 | 2008;2009 |  | '2008' (calendar year) |
| R050 | What revenue path did APAR lay out for its copper transposed conductor (CTC) product on the July 2020 call? | Q1 FY21 | 2021 | concall_transcript | 'July 2020' (event) |
| R064 | For FY2018-19, how did APAR's standalone operating cash flow compare with the consolidated figure? | FY2018-19 | 2019 |  | 'FY2018-19' |
| R068 | How much did Hero MotoCorp book as an exceptional VRS expense in FY2023-24 (standalone)? | FY2023-24 | 2024 |  | 'FY2023-24' |
| R115 | How much did Hero MotoCorp's standalone profit after tax grow between FY2023-24 and FY2025-26? | FY2023-24;FY2025-26 | 2024;2026 |  | 'FY2023-24' | 'FY2025-26' |
| R118 | For FY2023-24, how did Hero MotoCorp's consolidated profit after tax compare with its standalone profit? | FY2023-24 | 2024 |  | 'FY2023-24' |
| R157 | On what terms did E2E Networks borrow to buy hardware in 2021-22? | FY2022-23 | 2022 |  | '2021-22' |
| R159 | How does E2E Networks' revenue in the single quarter Q1 FY27 compare with its full-year revenue in FY21? | FY2020-21;Q1 FY27 | 2021;2027 |  | 'Q1 FY27' | 'FY21' |
| R160 | In July 2024 E2E's CEO said ₹800 crore of FY25 capex was not an announcement — how much did E2E actually spend in FY25? | FY2024-25 | 2025 |  | 'FY25' | 'FY25' | 'July 2024' (month) |
| R182 | Esconet's FY2023-24 EPS was ₹5.99 in its annual report — what figure do later filings show for the same year? | FY2023-24 | 2024 | annual_report | 'FY2023-24' |
