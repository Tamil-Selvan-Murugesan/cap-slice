# Parser recommendation — 2026-10-06

**Choose MinerU 4.0.10, advanced tier, with the tested MinerU2.5-Pro-2605-1.2B model, followed by `page_clean.py` and `structured_chunk.py`.** This is a recommendation for the financial-document application, not a claim that MinerU wins every accuracy metric. Do not substitute the standard tier: its table failures are materially different.

This is the single review handoff: it contains the selection rationale, every failure observed in this review, the complete 25-page case log, and the proposed cleanup/chunker rework. It does not claim to enumerate every failure across all 12,980 pages. A self-contained visual viewer and findings log accompany this report; separate raw outputs and generated case-folder files remain reproducible evidence outside the commit.

## Evidence reviewed

- Historical CPU comparison in `review/README.md`, `review/COMPARISON.md`, and original parsed/chunk Markdown; GPU rehearsal/full-run reports; `bugs_resolved.md`; parser adapters, cleanup, chunker and scorer.
- Final shared-cleanup scores in `parsed_compare/<parser>/fin/v1`, `v2`, and `v3`. These supersede earlier raw scores and the standard-only local `review/gpu/COMPARISON.md`. The now-removed, superseded root `COMPARISON.md` described a five-document, 240-page run despite its full-collection title.
- Local full-collection page caches: 228 documents each for Paddle, MinerU standard and advanced; 226 for Docling. Run summaries independently reproduce the two finalists' throughput.
- Seven selected disagreements inspected as cleaned pages and freshly generated chunks: V106, W004, W036, V045, W116, W058 and W092. Additional repetition examples inspected outside the golden facts.
- Three source PDF pages rendered and visually checked: E2E FY2020-21 PDF p.52, E2E April-2026 results PDF p.4, and APAR Aug-2024 presentation PDF p.123. Page numbers here are PDF indices, not printed page numbers.
- Six complete raw JSON files downloaded read-only from R2: both finalists on those same three documents. Prefix: `tamil/cap-slice/gpu-run-2026-10-04/`; MinerU under `parsed_advanced/mineru/`, Paddle under `parsed/paddleocr_vl/`. Raw HTML confirms the financial errors below precede conversion and chunking. No full reparse, embedding calls, cloud writes, or production integration performed.

## Expanded visual review requested by the user

A subsequent review visually checked **25 additional difficult pages** across all five pilot companies, compared cached parser output with the source images, and regenerated complete-document cleanup/chunks. The complete source-grounded case log is included below. The [self-contained side-by-side viewer](../review/visual-2026-10-06/index.html) and [visual findings log](../review/visual-2026-10-06/README.md) accompany this report. Four further R2 raw objects confirm the key failures and counterexample; their evidence locations are recorded below.

New MinerU advantages include APAR May-2018 PDF p.23 (Paddle changes EBITDA 412 to 71 and loses margin series), C2C FY2024–25 p.104 (Paddle changes 5,882.60 to 5,892.60 and loses/misplaces columns), and E2E FY2022–23 p.125 (Paddle puts A/B/C subtotal markers into year columns, shifts current-year values and drops previous-year subtotals).

**Strong counterevidence:** Hero FY2011–12 p.34 has a severe MinerU advanced year-column shift and missing series. Paddle and MinerU standard preserve that dashboard. MinerU's error is present in the raw R2 output. Paddle also gives better headings or complete table context on several pages. MinerU's Ecuador and PYLMEB loops are now visually confirmed to be unsupported by the source and to survive final candidate chunking. Paddle's Hero SDG-icon loop likewise survives into a 1,112-word chunk.

**The recommendation stands with moderate confidence.** It is an engineering choice for this financial-document mix, supported by concrete statement checks and measured throughput; it is not a demonstrated corpus-wide numerical-accuracy win. Current cleanup and chunking need additional work before unattended scaling. The diagnostic sample does not support an error-rate estimate; no scores or golden facts were changed.

## Accuracy: the finalists are close

| Parser | v1 full-credit facts | v2 full-credit facts | v3 hard full-credit facts |
|---|---:|---:|---:|
| MinerU advanced | 28/28 | 133/150 (88.7%) | 94/123 (76.4%) |
| PaddleOCR-VL-1.6 | 27/28 | 138/150 (92.0%) | 98/123 (79.7%) |
| MinerU standard | 20/28 | 119/150 (79.3%) | 72/123 (58.5%) |
| Docling | 27/28 | 111/150 (74.0%) | 55/123 (44.7% including missing facts) |

Docling's report gives 55/114 scored facts for v3; nine facts are unscored because one document was unavailable. For an operational comparison, 55/123 also accounts for the unavailable document. `chart_point` and `kv` facts receive full credit at L3 by definition; the report records that as L4. These are pipeline fact-survival scores assuming perfect retrieval, not parser-wide correctness rates or measured answer accuracy.

Paddle leads the reported unseen sets. It also leads v3 image-only facts (23/27 versus 18/27), while MinerU leads v3 table facts slightly (56/69 versus 55/69) and two-level headers (19/20 versus 18/20). Paddle's advantages on scans and pictures are real and matter if those become the dominant workload.

However, the small overall margin is not decisive. Some inspected losses are representation mismatches:

- **W004/W005, E2E May-2021 p.23:** MinerU keeps 21 and 23 in a table headed `Value (%)`; Paddle writes `21%` and `23%`. MinerU's zero scores do not mean the values were unread.
- **W036–W038, E2E Jan-2025 p.29:** both preserve the ARPU chart's values, quarters and INR title. MinerU escapes the tilde (`\~ARPU`), while the fact context contains `~ARPU`; it scores L2 against Paddle's L4.
- **V106/V107, APAR May-2023 p.17:** the finalists' tables contain the same target values. Paddle's chunk carries an INR-crore units statement from earlier context, while MinerU's chunk does not. This is context propagation, not a reading difference on p.17. Paddle's chunk also retains the previous slide's section title.

No scores or golden facts were changed in this review. These cases explain why I do not interpret Paddle's lead as a demonstrated, statistically reliable lead in financial reading. Facts on the same page are correlated; v3 is purposively hard; v1 and subsequent cleanup were development data. A simple pooled percentage would overstate the evidence.

## Financial errors that matter more than formatting

**E2E FY2020-21, PDF p.52:** the source has a separate `Profit for the year` row with `(93,533,720)` under March 31, 2020. MinerU preserves that row and value. Paddle collapses several labels into one cell and omits this loss. On the same page, the source's short-term leave provision for March 31, 2021 is `159,894`. MinerU assigns it to leave benefits; Paddle assigns it to gratuity and shifts the remaining provision labels. The raw HTML from R2 contains the same errors. This is a silent semantic failure: a plausible-looking table can answer the wrong financial question.

**E2E April-2026 results, PDF p.4:** the image prints purchase of fixed assets as `(1,26,245.03)` — 126,245.03. MinerU preserves it; Paddle emits `(1,262,245.03)` — ten times larger. Paddle also expands `1,47,283.12` to `1,472,832.12` and `1,35,024.28` to `1,350,242.8`. These are changed digits, not equivalent Indian/Western comma grouping. R2 raw HTML confirms the changes. This is particularly relevant to filings with a defective embedded text layer.

These spot checks do not prove MinerU has fewer numeric errors across all pages. They do show why an aggregate score that gives a formatting miss and a tenfold numeric error the same weight is insufficient for this choice.

## Generated content and repetition

The prior progress statement that Paddle “invents nothing” is too strong. APAR Aug-2024 p.123 is a slide containing small assurance-document thumbnails. Paddle emits **62,253 characters**, including extensive repetitions of `high-level and high-level` and `Account 1 / Page 1 of 2`. APAR Nov-2017-a p.13 repeats `POWERROIC` hundreds of times. These survive wrapper cleanup and can overwhelm chunks, embeddings and retrieval. The raw R2 result confirms the p.123 failure.

MinerU also generates unreliable content on the assurance thumbnails; the raw JSON contains invented prose, and it can generate Mermaid diagrams. Its `<details>`/Mermaid output occurs on **2,324 of 12,980 pages** (tag presence counted across the cache). On the inspected assurance page, existing cleanup removes the generated image content while retaining the source slide's large text. This gives the current MinerU pipeline a useful containment mechanism; it is not a universal hallucination guarantee. Some explanatory content can escape those tags (the decorative-page check includes a `Text / Description` table).

Stripping those blocks also removes genuine image text. This is a deliberate precision/coverage tradeoff, and one reason Paddle wins some image-only facts. Keep raw outputs and any excluded blocks available for audit, but do not treat generated descriptions as financial evidence. **MinerU's cleanup does not contain every repetition failure:** APAR Sep-2024 p.140 retains a table with dozens of repeated/variant Ecuador rows; E2E Nov-2021 p.24 retains a long sequence of `PYLMEB` variant chart rows. A broad token/phrase scan found candidates in both pipelines, including ordinary repeated table labels as false positives. A narrower consecutive-prose regex flagged five cleaned Paddle pages and zero MinerU pages, but it misses the table loops just described and must not be presented as an exhaustive loop rate. Both finalists need repetition and output-quality checks before scaling.

## Measured scaling economics

Summing all pages and using earliest start to latest finish across concurrent run summaries:

| Metric | MinerU advanced | PaddleOCR-VL |
|---|---:|---:|
| Documents / pages | 228 / 12,980 | 228 / 12,980 |
| Wall time | 3,320.1 s (55.3 min) | 5,056.8 s (84.3 min) |
| Throughput | 3.910 pages/s | 2.567 pages/s |
| Historical pod cost / 1,000 pages at $1.01/h | $0.0718 | $0.1093 |
| Projected parser compute for 11M pages | $789 | $1,202 |
| Projected parser compute for 14M pages | $1,005 | $1,530 |

MinerU is about **52% faster** and **34% cheaper per page** in the measured configurations. The comparison is four MinerU clients versus two Paddle clients on the RTX 5090; it measures the deployed pipelines, not equal-client model efficiency. Paddle continuous feeding/tuning may improve its throughput, but that improvement has not been measured here. Projections hold hardware price and document mix fixed and exclude setup, storage, transfers, retries, embedding and operations. They are not current cloud quotes.

## Why the other options lose

- **MinerU standard:** cheaper, but the observed collapse of digital statements into one row and substantially worse hard-set scores make it unsuitable as the single financial parser.
- **Docling:** excellent on the early five-document sample, but the wider test reveals weaker coverage/accuracy, failures on two PDFs, and failure on the bad embedded-text-layer facts (0/8 versus 7/8 for both finalists). Its earlier recommendation was based on narrower evidence.
- **PyMuPDF4LLM:** scanned-table column reconstruction failed in the original examples; the GPU tuning comparison did not justify a full run. Do not assign it an invented full-collection accuracy score.
- **Baseline / PyMuPDF text:** useful fast extraction, but insufficient recovery of scans and financial row/column relationships as the only parser.

## Conditions attached to the recommendation

Use the exact tested advanced tier and model, keep raw block geometry and HTML tables, apply the shared cleanup, and use structured chunks. Before a bulk run, validate rejection/retry handling for loops and suspicious numeric/table output; check inherited titles and units against the correct table scope; normalize harmless Markdown escapes and percent formatting in evaluation. These are known gaps, not changes implemented by this review.

The next quality gate is retrieval on representative questions with known source pages, because these scores assume the correct chunk is found. The current indexer still uses the baseline chunker. Parser selection can proceed now; production answer quality remains unvalidated. This recommendation has not been recorded as user approval to change the indexer or begin bulk acquisition.

For deployment planning, check the license accompanying the exact installed code and weights. Current upstream MinerU uses an Apache-based custom license with service attribution and large-business thresholds; PaddleOCR-VL-1.6 weights list Apache 2.0. Sources checked 2026-10-06: [MinerU license](https://github.com/opendatalab/MinerU/blob/master/LICENSE.md), [Paddle model license](https://huggingface.co/PaddlePaddle/PaddleOCR-VL-1.6/blob/main/LICENSE). Licensing is not the deciding factor in the measured parser recommendation.

## Detailed visual audit: all 25 cases

The source images were inspected before the parser/chunk comparisons. This purposive diagnostic sample includes 17 golden-v3 pages and eight additional pages; it cannot establish a population error rate. Chunk indices are zero-based. Cached adapter page text, cleaned text and complete-document chunks were inspected for both finalists. Docling and MinerU standard were additionally checked on selected consequential examples. No paid embeddings, reparsing or implementation fixes were performed.

## Most consequential new evidence

### Financial column alignment: MinerU wins the new scanned cash-flow check

**H22, E2E FY2022–23, PDF p.125:** the image has net operating cash flow of **3,552.93 / 2,588.52**, investing cash flow of **(2,065.18) / (1,919.21)** and financing cash flow of **(240.78) / (200.69)** for 2023 / 2022, in INR lakhs. The letters `(A)`, `(B)` and `(C)` belong with the labels.

MinerU retains both years correctly in chunks **250–251**. Paddle instead produces `operating activities | (A) | 3,552.93`, and similarly for B/C. Under its year header, the marker occupies 2023 and the 2023 amount occupies 2022; all three 2022 subtotals disappear. This survives in chunks **239–240** and exists in the R2 HTML. Paddle has the better overall statement heading; MinerU's chunks inherit a company-secretary heading and excessive signatory context. That metadata defect does not erase the substantive column advantage here.

### Crowded annual-report tables: another MinerU advantage

**H19, C2C FY2024–25, PDF p.104:** the source's finished goods are **5,882.60** lakhs. MinerU retains this; Paddle writes **5,892.60** while correctly writing the total as 5,882.60. The source's ageing tables have separate rightmost totals of **10,995.87 / 4,269.51**. Paddle drops these columns. It also places C2C Innovations' prior-year **65.06** in an extra, unlabelled third numeric column rather than under March 2024.

MinerU preserves these items in chunks **250, 254, 256 and 260**; Paddle's errors survive in **226–228** and are confirmed in R2 HTML. The original ageing header itself is awkward: the printed “Total” sits over the more-than-three-years column, with the actual total further right. MinerU retains that source awkwardness; it should not be credited with a fully repaired semantic header. Both pipelines retain most other checked balances correctly.

### Charts: a clear MinerU win and a serious MinerU loss

**H07, APAR May-2018 presentation, PDF p.23:** source FY18 EBITDA is **412**, with margin **7.1%**. MinerU preserves the EBITDA series 302/254/367/425/412 and the margin series 6.5/5.0/7.2/8.8/7.1 in chunk **53**. It misnames the margin column “Growth Rate (%)”, although the caption says EBITDA margin. Paddle drops the margin series and writes FY18 EBITDA as **71** in chunk **38**. This is a numerical failure as well as a coverage loss. Docling and MinerU standard do not recover the plotted series in their cleaned outputs.

**H15, Hero FY2011–12 annual report, PDF p.34:** the source ten-year dashboard ends with sales **6,235,205**, total income **23,944** crore and net sales **23,368** crore. MinerU inserts each unit into the first year's cell, shifts the corresponding nine values one year right, and drops the final year. It also omits operating margin, OPBDIT margin, EPS and dividend series. Its chunk **29** retains the wrong table. This is present in the raw R2 block, so shared chunking did not cause it.

Paddle preserves all those years and series in chunks **29–30**, including FY2009–10 OPBDIT margin **17.4%** and EPS **111.8**. Its layout separates metric labels from numeric rows, which hurts strict same-row scoring but leaves the meaning recoverable in a single chunk. MinerU standard also preserves these series, with fragmented labels; Docling leaves the dashboard as an image placeholder. **Advanced is not uniformly superior to standard, and MinerU is not uniformly superior on charts.**

### Generated tables remain a problem for MinerU

**H23, APAR Sep-2024 presentation, PDF p.140:** a trade-flow map accompanies three CBAM bullets and six product categories. MinerU invents an extensive table with repeated Ecuador entries and a rising sequence of percentages. It survives cleanup and occupies chunks **173–175**. Paddle preserves the explanatory text without generating that table, in chunk **175**.

**H24, E2E Nov-2021 presentation, PDF p.24:** “Financial Overview” appears over a stock photograph of a tablet and phone. MinerU turns the small decorative charts into supposed data, including dozens of `PYLMEB_2 ... PYLMEB_78` rows and extrapolated coordinates. These survive in chunks **35–36**. Paddle avoids that loop, but also extracts the tablet's decorative financial numbers into chunks **32, 34 and 36**. Those numbers are visible in the photograph; they are **not established E2E financial disclosures**. Even faithful OCR needs document-role context here.

**H25, Hero FY2025–26, PDF p.35:** tiny SDG icons cause Paddle to repeat “INDUSTRIAL” extensively. Cleanup retains a **1,112-word chunk (74)**, while the source human-capital metric **LTIFR 0.31** is absent from its output. It also wrongly assigns the overall two-wheeler ICE share **28.7%** to the motorcycles-sold row and loses the sales unit “lakh”. MinerU avoids the loop and preserves 0.31, the two sales values and their lakh unit. However, MinerU separates “519” from “New recruits” across chunks **72–73**, proving cleaner text still needs better chunk boundaries.

## Complete case log

Case IDs identify the optional local visual artifacts. Source paths and PDF page numbers are recorded in the evidence inventory below. “Both” means the listed checks succeeded, not that the whole page is flawless.

| Case / source | Image-grounded checks and final-chunk findings |
|---|---|
| H01, C2C FY2024–25 p.19 | Both preserve DSAFDS and the rugged laptop/laser-rangefinder product description in chunk 27. Paddle adds a stray text fragment. Title/context crosses the prior chunk. |
| H02, APAR Nov-2017-a concall p.1 | Both retain the 2-Nov-2017 call date. MinerU reads SEC/2511/2017 but loses it during chunking; Paddle chunk 0 retains it. Paddle invents signature text. |
| H03, E2E FY2021–22 p.6 | MinerU chunk 4 reconstructs timeline years and milestones (2009 inception, 2018 IPO, 2022 mainboard). Paddle chunk 5 loses timeline year labels while preserving some milestone prose. Docling document unavailable. |
| H04, APAR Feb-2020-a concall p.1 | Both preserve 24-Jan-2020 call date; MinerU joins spacing. MinerU raw SEC0302/2020 disappears from chunks; Paddle chunk 0 retains it but garbles signature. Both omit small footer CIN. |
| H05, APAR Jul-2026 presentation p.4 | Both table chunk 8 preserve Q1FY26 EBITDA/KL 7,004 and Q4FY26 5,656. Mixed units need caption/row interpretation; adjustment footnote lives separately. |
| H06, APAR Feb-2018 presentation p.21 | Both reconstruct six chart series, including exports FY17 1,544/domestic 3,297. Trailing “Figures in Rs Crore” fails to accompany chart chunks (MinerU 46–56, Paddle 47–57). Shared chunking gap. |
| H07, APAR May-2018 presentation p.23 | MinerU retains EBITDA + margin series but misnames margin. Paddle loses margins and changes FY18 EBITDA 412 to 71. See detailed finding. |
| H08, APAR Aug-2020 presentation p.22 | Both read segment tables. MinerU splits final cables contribution 19.0/19.3/24.3/21.1 into chunk 66 without the contribution-% subsection; Paddle chunk 42 keeps the whole table. Paddle inherits prior slide's “Capital Employed” heading. |
| H09, APAR Feb-2020-b presentation p.5 | Both preserve HVDC MVA 19,500 and inter-regional MW target 118,050 with headers/units. MinerU chunk 9 joins the companies/orders table to an unrelated same-width table on p.6. Paddle chunk 8 stays on p.5. |
| H10, APAR FY2019–20 p.170 | Both preserve derivative OCI 28.04/(1.53), provision P&L (1.82) and multi-level years. Paddle drops “Deposits from dealers” label for 3.37/3.30 in chunk 725; MinerU chunk 702 keeps it. |
| H11, Hero FY2013–14 p.32 | Both preserve EVA 1,723 for 2009–10 and cost of equity 14.39 for 2010–11. Split table chunks retain years/unit (MinerU 51–52, Paddle 61–62). |
| H12, APAR FY2024–25 p.161 | Both handle cash-flow + rotated equity table: payables 1,139.37, interest (256.58), retained earnings 2,676.45, equity total 4,251.71. MinerU 835/840–841 and Paddle 797/801–802 keep values. Equity section metadata inherits signatory/notes noise. |
| H13, APAR FY2020–21 p.92 | Both retain rotated PPE values, including depreciation 61.75 and net block 409.61. Paddle's group header has four Gross Block cells instead of five, shifting group meaning; MinerU aligns five gross/four depreciation/two net columns. Both chunks 330–331 inherit stale headings. |
| H14, APAR FY2020–21 p.50 | Both preserve 104 shareholders in highest holding bucket, 34,247,246 shares/89.5%, Dec-2020 Sensex 47,751.33, and Jan-2021 BSE/NSE 417.75/418. Correct grouped exchange columns survive (MinerU 187/189, Paddle 192/194). |
| H15, Hero FY2011–12 p.34 | Severe MinerU year shift and omissions; Paddle and MinerU standard preserve the series. Both finalists inherit unrelated GVDP section metadata. See detailed finding. |
| H16, APAR FY2016–17 p.179 | Both preserve Ind-AS reconciliation OCI 124.88, finance transition (5.94), inventory adjustment 53.71 with period/unit headers (MinerU 874, Paddle 872 for OCI). |
| H17, Hero FY2012–13 p.90 | Both preserve six plant/year columns: Gurgaon own-generation 58,073,580/62,244,192, Haridwar Kwh/vehicle 15.71/15.64. Both preserve the source's odd printed grouping 175,489,85 rather than silently correcting it. Plant/year headers repeat in split chunks; footnote is separate. MinerU inherits unrelated earnings/outgo heading. |
| H18, Esconet FY2025–26 p.144 | Both preserve finance totals 118.13/81.53, service charges 1,038.11/850.48, negative forex -48.72, other-expense totals 2,860.70/1,941.62. MinerU writes H lakhs; Paddle correctly writes ₹ lakhs and clearer subsection titles (MinerU 492/494, Paddle 460/461). |
| H19, C2C FY2024–25 p.104 | MinerU preserves inventory, ageing totals and related-party column. Paddle numeric/column errors survive chunks and exist in R2. See detailed finding. |
| H20, E2E FY2019–20 p.57 | Both preserve separate Computer Equipment/Computer columns: gross 556,906,976/3,732,054, depreciation 462,602,969/2,896,356, net 94,304,007/835,699; software net 37,666. Paddle chunks 158–159 have better note headings than MinerU 167/169. No page-wide unit line is printed on this page. |
| H21, Hero FY2023–24 p.176 | Both handle two printed pages in one PDF spread: current debt total 363.43, provision 322.46 non-current/159.44 current, warranty close 422.30 and utilisation (165.73). Values/years/crore unit survive (MinerU 1147/1152/1154, Paddle 1122/1127/1129); Paddle has more precise note titles. |
| H22, E2E FY2022–23 p.125 | MinerU keeps three cash-flow subtotal pairs. Paddle inserts A/B/C into year columns and drops prior-year subtotals. See detailed finding. |
| H23, APAR Sep-2024 presentation p.140 | MinerU invented/repetitive trade-flow table survives cleanup; Paddle retains the main CBAM text. See detailed finding. |
| H24, E2E Nov-2021 presentation p.24 | MinerU invents long chart-coordinate series; both extract decorative photograph numbers without distinguishing them from issuer facts. See detailed finding. |
| H25, Hero FY2025–26 p.35 | Paddle SDG-icon loop survives, LTIFR omitted and market share misassigned. MinerU cleaner but splits recruits value/label. See detailed finding. |

## Cleanup and chunker rework to perform

These are proposed changes, **not implemented fixes**. Parser-origin digit errors and missing cells cannot be repaired reliably by chunking alone. Preserve raw outputs so source verification and alternative parsing remain possible.

| Priority | Observed failure / examples | Proposed work and acceptance check |
|---|---|---|
| P0 | Invented/repetitive content survives cleanup: MinerU H23/H24; Paddle H25 and APAR Aug-2024 p.123 | Detect prose loops, repeated/variant table rows, implausible output growth and missing expected structure. Quarantine suspect blocks/pages and retry or review against the source; preserve the rejected raw output and reason. Validate that both pipelines' observed loops are rejected without deleting legitimate repeated table labels. |
| P0 | Silent financial digit/column errors: E2E Apr-2026 p.4, H15/H19/H22 | Validate header/body column counts, unit placement, year alignment and totals where meaningful. Flag contradictions such as inventory differing from its single-row total. Source-check suspicious tables; use a reviewed retry/fallback rather than inventing corrections. Test both the Paddle failures and the MinerU dashboard counterexample. Arithmetic agreement alone is not proof of correctness. |
| P0 | Decorative photograph data treated as issuer evidence: H24 | Keep original block geometry/type and mark decorative or illustrative content separately from financial disclosures. Do not promote photographed tablet numbers or generated chart descriptions into issuer facts. Test with the source role as well as OCR fidelity. |
| P1 | Wrong inherited section headings/caption spillover: H08/H12/H13/H15/H17/H19/H22 | Assign section and caption metadata from the current block's actual hierarchy and page region, not merely the last heading encountered. Bound signatory/caption carryover. Check that cash-flow/PPE chunks carry their own headings and omit unrelated auditors, equity-rights or GVDP context. |
| P1 | Trailing units absent; inherited units may be wrong: H05/H06/H15/H18/H20 | Attach validated title, period and unit to the correct table/chart before splitting, including units printed after the figure. Support mixed per-row units. Do not infer a whole-table currency from a nearby footnote or convert every metric on H15 into crores. Treat H18's H/₹ glyph mismatch explicitly. |
| P1 | Split table loses subsection or local period context: H08/H17/H19/H22 | Repeat multi-level headers plus the active subsection/year in each split table chunk. A contribution-percent row must retain its percent subsection, even if a global header mentions rupee crores. Keep labels, values, units and dates together where needed to answer a question. |
| P1 | Unrelated adjacent tables joined: H09; nested table headers flattened in H19/H21 | Require semantic header/section compatibility for continuation, not just equal column count. Keep changed header types and new notes as distinct tables. Validate H09's p.5 orders table does not absorb p.6 chart values. |
| P1 | Short document references disappear as boilerplate: H02/H04 | Make repeated-edge filtering conservative for semantic identifiers, dates and numeric differences. Preserve SEC/2511/2017 and SEC0302/2020 in letter chunks while still removing real recurring letterhead. |
| P1 | Label/value split and generation-driven oversized chunk: H25 | Avoid splitting compact key/value pairs across chunks. Apply output-quality rejection before enforcing chunk size so repeated noise does not become a huge embedding chunk. Verify 519/New recruits and 0.31/LTIFR survive together and retain the correct meaning. |
| P2 | Formatting mismatches distort evaluation: W004/W005, W036–W038, H08 | Normalize equivalent percentage representations, harmless Markdown escapes and HTML entities in evaluation, with source/chunk inspection behind changes. Do not normalize genuinely changed numbers or give a wrong column full credit. |

Preserve the exact tested advanced tier/model and raw table geometry. Keep generated picture descriptions in a separately labelled audit field if useful; including them in retrieval should be an explicit experiment, not an automatic promotion into evidence. Missing image facts after stripping must remain measurable.

After these fixes, run focused source-grounded checks on the documented failures and counterexamples, rescore all golden sets with the same preprocessing for every parser, and compare retrieval on representative questions with known source pages. Current fact scores assume perfect retrieval. Track parser/chunker/cleanup versions and invalidate cached indexing deliberately when they change; the present indexer still uses the baseline pipeline. Integration, bulk acquisition and paid indexing have not been approved by this review.

## Evidence locations and reproducibility

The committed `review/visual-2026-10-06/index.html` embeds source images, parser/cleaned/chunk text, extra-parser comparisons, selected raw excerpts and original audit provenance. It can be opened without external assets. The companion README and builder are included; separate generated case-folder files and older untracked reports were removed at the user's request after verifying the portable viewer and superseding results. They can be regenerated from the source PDFs/caches and reporting tools. Source PDFs and batch caches can be recovered from the existing R2 backup prefix `tamil/cap-slice/gpu-run-2026-10-04/`. Images can be rendered from the source PDFs; candidate chunks can be regenerated by applying `clean_pages(pages, pdf_path)` and `chunks_for(parser, cleaned_pages)` to the **entire document**, then selecting chunks covering the reviewed page. MinerU advanced uses cache family `parsed_advanced/mineru/`; Paddle, Docling and MinerU standard use `parsed/<parser>/`. Adapter `pages.json` files contain page/text pairs. Direct raw JSON is distinct from adapter Markdown.

The original score evidence is `parsed_compare/<mineru_advanced|paddleocr_vl|docling|mineru_standard>/fin/v{1,2,3}/`; use the post-fix results, not the older standard-only generated reports. Run-summary timestamps underpin the throughput figures above.

| Case | Source PDF under `data/` | PDF page |
|---|---|---:|
| H01 | `C2C/annual_reports/2025-09-08_FY2024-25.pdf` | 19 |
| H02 | `APARINDS/concall_transcripts/Nov-2017-a.pdf` | 1 |
| H03 | `E2E/annual_reports/2022-07-29_FY2021-22.pdf` | 6 |
| H04 | `APARINDS/concall_transcripts/Feb-2020-a.pdf` | 1 |
| H05 | `APARINDS/investor_presentations/Jul-2026.pdf` | 4 |
| H06 | `APARINDS/investor_presentations/Feb-2018.pdf` | 21 |
| H07 | `APARINDS/investor_presentations/May-2018.pdf` | 23 |
| H08 | `APARINDS/investor_presentations/Aug-2020.pdf` | 22 |
| H09 | `APARINDS/investor_presentations/Feb-2020-b.pdf` | 5 |
| H10 | `APARINDS/annual_reports/FY2019-20.pdf` | 170 |
| H11 | `HEROMOTOCO/annual_reports/FY2013-14.pdf` | 32 |
| H12 | `APARINDS/annual_reports/FY2024-25.pdf` | 161 |
| H13 | `APARINDS/annual_reports/FY2020-21.pdf` | 92 |
| H14 | `APARINDS/annual_reports/FY2020-21.pdf` | 50 |
| H15 | `HEROMOTOCO/annual_reports/FY2011-12.pdf` | 34 |
| H16 | `APARINDS/annual_reports/FY2016-17.pdf` | 179 |
| H17 | `HEROMOTOCO/annual_reports/FY2012-13.pdf` | 90 |
| H18 | `ESCONET/annual_reports/2026-08-25_FY2025-26.pdf` | 144 |
| H19 | `C2C/annual_reports/2025-09-08_FY2024-25.pdf` | 104 |
| H20 | `E2E/annual_reports/2020-08-19_FY2019-20.pdf` | 57 |
| H21 | `HEROMOTOCO/annual_reports/FY2023-24.pdf` | 176 |
| H22 | `E2E/annual_reports/2023-09-21_FY2022-23.pdf` | 125 |
| H23 | `APARINDS/investor_presentations/Sep-2024.pdf` | 140 |
| H24 | `E2E/investor_presentations/Nov-2021.pdf` | 24 |
| H25 | `HEROMOTOCO/annual_reports/FY2025-26.pdf` | 35 |

Four additional raw objects fetched read-only for this expanded review:

| Case / parser | Object key relative to the R2 backup prefix | Complete-object SHA-256 |
|---|---|---|
| `H22/paddleocr_vl-r2-page.json` | `parsed/paddleocr_vl/E2E/annual_reports/2023-09-21_FY2022-23/paddleocr_vl.json` | `c7b6bb52b539f8d725e666b7d00990437968f9d8aada458417161b15c4084294` |
| `H19/paddleocr_vl-r2-page.json` | `parsed/paddleocr_vl/C2C/annual_reports/2025-09-08_FY2024-25/paddleocr_vl.json` | `47a613cdc3d18637a9ab4a0d11759ccedfc2a7f2668e54ee02ca446201edb9c3` |
| `H15/paddleocr_vl-r2-page.json` | `parsed/paddleocr_vl/HEROMOTOCO/annual_reports/FY2011-12/paddleocr_vl.json` | `ecc26e2d00ae01c373293bffeffa3be4c0585d073d5550481bc4ca20777858d0` |
| `H15/mineru_advanced-r2-page.json` | `parsed_advanced/mineru/HEROMOTOCO/annual_reports/FY2011-12/mineru_middle.json` | `95430dab23ad0a3fdd823b54cc90f2ca631a2871abe83c69523776797e7e346a` |

Selected-page raw excerpts are embedded in the committed viewer; separate JSON files are excluded because complete objects are backed up. Code fingerprints used when regenerating the expanded review:

| Code file | SHA-256 |
|---|---|
| `src/cap_slice/page_clean.py` | `15816b284caf13c562af1a47e3dd6f4406e96199217c371dda6f053fcb32e845` |
| `src/cap_slice/structured_chunk.py` | `d5288e7470265717559a9789dfc499f1f6170bce275d676e9b3fd0206d9c55b7` |
| `src/cap_slice/score.py` | `067ed00cdbb7a6238068a9408213d95b2a734caad12a8b20242e68063f398264` |
| `src/cap_slice/parsing/paddleocr_vl.py` | `89b21a93d7397fb27d058630c3533faa8775979a10ee422cdde48f9318dca7d6` |
| `src/cap_slice/parsing/mineru_vlm.py` | `0d3d295ee7a688b8668aa21b57150fc3616c3f282b8f41f1f0a0211accf5cfce` |
