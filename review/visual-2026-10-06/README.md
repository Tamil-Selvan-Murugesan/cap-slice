# Hard-page visual review — 2026-10-06

**Recommendation remains MinerU advanced, with moderate confidence.** The expanded review adds important evidence in both directions. MinerU is preferable for the tested financial-document workload when combined with cleanup and structured chunking, but the current pipeline still admits invented tables, silent column errors and misleading chunk context. Paddle is a serious alternative and wins the most severe counterexample in this review.

Open [the side-by-side viewer](index.html) to compare each source image with the two finalists' cached page text, cleaned text and candidate embedding chunks. The viewer embeds all source images, the finalists' page text and chunks, additional Docling/MinerU-standard comparisons, and the saved raw R2 page excerpts. It opens without separate case-folder files. The observations below refer to **PDF page indices**, not printed page numbers; chunk indices are zero-based.

## Scope and method

Visually inspected **25 additional pages across all five pilot companies**, beyond the three source pages in the initial recommendation. These include 17 selected hard golden-v3 pages, four additional dense annual-report pages selected independently of score disagreements, another scanned cash-flow statement, and three repetition candidates. This is a diagnostic sample, deliberately rich in difficult cases. It cannot establish a population error rate or a statistical winner. Findings are selected source-grounded checks, not exhaustive verification of every cell on every page.

Read the source images first, then the finalists' cached page outputs and chunks. Regenerated chunks from the **entire document** using the current shared `clean_pages` and `chunks_for`, so inherited units, cross-page joins and section names are represented. Cleaned text can incorporate missing units from the native PDF layer. These are the final candidate texts for this comparison; the live indexer still uses the baseline pipeline and no embeddings were created.

Downloaded four additional complete raw JSON objects read-only from R2 to confirm the crucial H15, H19 and H22 observations. Their selected-page excerpts and the provenance (object keys, complete-object SHA-256 hashes and code fingerprints) are embedded in the viewer. The [consolidated report](../../docs/parser-selection-2026-10-06.md) also records those evidence locations. These confirm that the compared failures precede Markdown conversion/chunking. No parser reruns, scorer changes, golden edits or implementation fixes were made. The cached `*-raw.md` files are adapter page text, not the original model JSON; only `*-r2-page.json` files are direct raw excerpts.

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

Links open the corresponding case in the self-contained viewer. “Both” means the listed checks succeeded, not that the whole page is flawless.

| Case / source | Image-grounded checks and final-chunk findings |
|---|---|
| [H01](index.html#H01), C2C FY2024–25 p.19 | Both preserve DSAFDS and the rugged laptop/laser-rangefinder product description in chunk 27. Paddle adds a stray text fragment. Title/context crosses the prior chunk. |
| [H02](index.html#H02), APAR Nov-2017-a concall p.1 | Both retain the 2-Nov-2017 call date. MinerU reads SEC/2511/2017 but loses it during chunking; Paddle chunk 0 retains it. Paddle invents signature text. |
| [H03](index.html#H03), E2E FY2021–22 p.6 | MinerU chunk 4 reconstructs timeline years and milestones (2009 inception, 2018 IPO, 2022 mainboard). Paddle chunk 5 loses timeline year labels while preserving some milestone prose. Docling document unavailable. |
| [H04](index.html#H04), APAR Feb-2020-a concall p.1 | Both preserve 24-Jan-2020 call date; MinerU joins spacing. MinerU raw SEC0302/2020 disappears from chunks; Paddle chunk 0 retains it but garbles signature. Both omit small footer CIN. |
| [H05](index.html#H05), APAR Jul-2026 presentation p.4 | Both table chunk 8 preserve Q1FY26 EBITDA/KL 7,004 and Q4FY26 5,656. Mixed units need caption/row interpretation; adjustment footnote lives separately. |
| [H06](index.html#H06), APAR Feb-2018 presentation p.21 | Both reconstruct six chart series, including exports FY17 1,544/domestic 3,297. Trailing “Figures in Rs Crore” fails to accompany chart chunks (MinerU 46–56, Paddle 47–57). Shared chunking gap. |
| [H07](index.html#H07), APAR May-2018 presentation p.23 | MinerU retains EBITDA + margin series but misnames margin. Paddle loses margins and changes FY18 EBITDA 412 to 71. See detailed finding. |
| [H08](index.html#H08), APAR Aug-2020 presentation p.22 | Both read segment tables. MinerU splits final cables contribution 19.0/19.3/24.3/21.1 into chunk 66 without the contribution-% subsection; Paddle chunk 42 keeps the whole table. Paddle inherits prior slide's “Capital Employed” heading. |
| [H09](index.html#H09), APAR Feb-2020-b presentation p.5 | Both preserve HVDC MVA 19,500 and inter-regional MW target 118,050 with headers/units. MinerU chunk 9 joins the companies/orders table to an unrelated same-width table on p.6. Paddle chunk 8 stays on p.5. |
| [H10](index.html#H10), APAR FY2019–20 p.170 | Both preserve derivative OCI 28.04/(1.53), provision P&L (1.82) and multi-level years. Paddle drops “Deposits from dealers” label for 3.37/3.30 in chunk 725; MinerU chunk 702 keeps it. |
| [H11](index.html#H11), Hero FY2013–14 p.32 | Both preserve EVA 1,723 for 2009–10 and cost of equity 14.39 for 2010–11. Split table chunks retain years/unit (MinerU 51–52, Paddle 61–62). |
| [H12](index.html#H12), APAR FY2024–25 p.161 | Both handle cash-flow + rotated equity table: payables 1,139.37, interest (256.58), retained earnings 2,676.45, equity total 4,251.71. MinerU 835/840–841 and Paddle 797/801–802 keep values. Equity section metadata inherits signatory/notes noise. |
| [H13](index.html#H13), APAR FY2020–21 p.92 | Both retain rotated PPE values, including depreciation 61.75 and net block 409.61. Paddle's group header has four Gross Block cells instead of five, shifting group meaning; MinerU aligns five gross/four depreciation/two net columns. Both chunks 330–331 inherit stale headings. |
| [H14](index.html#H14), APAR FY2020–21 p.50 | Both preserve 104 shareholders in highest holding bucket, 34,247,246 shares/89.5%, Dec-2020 Sensex 47,751.33, and Jan-2021 BSE/NSE 417.75/418. Correct grouped exchange columns survive (MinerU 187/189, Paddle 192/194). |
| [H15](index.html#H15), Hero FY2011–12 p.34 | Severe MinerU year shift and omissions; Paddle and MinerU standard preserve the series. Both finalists inherit unrelated GVDP section metadata. See detailed finding. |
| [H16](index.html#H16), APAR FY2016–17 p.179 | Both preserve Ind-AS reconciliation OCI 124.88, finance transition (5.94), inventory adjustment 53.71 with period/unit headers (MinerU 874, Paddle 872 for OCI). |
| [H17](index.html#H17), Hero FY2012–13 p.90 | Both preserve six plant/year columns: Gurgaon own-generation 58,073,580/62,244,192, Haridwar Kwh/vehicle 15.71/15.64. Both preserve the source's odd printed grouping 175,489,85 rather than silently correcting it. Plant/year headers repeat in split chunks; footnote is separate. MinerU inherits unrelated earnings/outgo heading. |
| [H18](index.html#H18), Esconet FY2025–26 p.144 | Both preserve finance totals 118.13/81.53, service charges 1,038.11/850.48, negative forex -48.72, other-expense totals 2,860.70/1,941.62. MinerU writes H lakhs; Paddle correctly writes ₹ lakhs and clearer subsection titles (MinerU 492/494, Paddle 460/461). |
| [H19](index.html#H19), C2C FY2024–25 p.104 | MinerU preserves inventory, ageing totals and related-party column. Paddle numeric/column errors survive chunks and exist in R2. See detailed finding. |
| [H20](index.html#H20), E2E FY2019–20 p.57 | Both preserve separate Computer Equipment/Computer columns: gross 556,906,976/3,732,054, depreciation 462,602,969/2,896,356, net 94,304,007/835,699; software net 37,666. Paddle chunks 158–159 have better note headings than MinerU 167/169. No page-wide unit line is printed on this page. |
| [H21](index.html#H21), Hero FY2023–24 p.176 | Both handle two printed pages in one PDF spread: current debt total 363.43, provision 322.46 non-current/159.44 current, warranty close 422.30 and utilisation (165.73). Values/years/crore unit survive (MinerU 1147/1152/1154, Paddle 1122/1127/1129); Paddle has more precise note titles. |
| [H22](index.html#H22), E2E FY2022–23 p.125 | MinerU keeps three cash-flow subtotal pairs. Paddle inserts A/B/C into year columns and drops prior-year subtotals. See detailed finding. |
| [H23](index.html#H23), APAR Sep-2024 presentation p.140 | MinerU invented/repetitive trade-flow table survives cleanup; Paddle retains the main CBAM text. See detailed finding. |
| [H24](index.html#H24), E2E Nov-2021 presentation p.24 | MinerU invents long chart-coordinate series; both extract decorative photograph numbers without distinguishing them from issuer facts. See detailed finding. |
| [H25](index.html#H25), Hero FY2025–26 p.35 | Paddle SDG-icon loop survives, LTIFR omitted and market share misassigned. MinerU cleaner but splits recruits value/label. See detailed finding. |

## Decision implications

The newly inspected dense statements, tax reconciliation, exchange quotations and rotated tables often work well in both finalists. Their near-tie in the existing fact scores is credible. Neither has a universal layout advantage; Paddle often gives clearer headings and fuller image/chart coverage. The Hero dashboard is a serious reason to avoid claiming that MinerU guarantees correct financial columns.

I still select **the tested MinerU advanced configuration** for this corpus because its handling of the newly checked scanned subtotals and crowded financial notes, together with the previously verified numeric errors in Paddle, supports the financial-use-case preference; measured throughput remains about 52% higher and compute cost about 34% lower. Those are engineering judgment and measured runtime, **not a proven corpus-wide numerical-accuracy lead**. An application prioritising image dashboards over financial statements could reasonably make the other choice.

Before scaling this pipeline, resolve or reliably reject: surviving generation loops, unit/year column mismatches, decorative-image data, lost subsection labels, stale section metadata and value/label splits. Do not assume current cleanup solves these. Retrieval with source-grounded questions remains the next evaluation gate; no implementation work was done in this review.

Rebuild the artifacts from the repository root with `.venv/bin/python review/visual-2026-10-06/build.py`, with local PDFs and parse caches present. This regenerates images/adapter text/current chunks; the separately saved R2 excerpts and this manual findings log remain unchanged. The viewer embeds the exact page manifest, parser availability, chunk indices and original audit provenance. The separately generated `manifest.json` and `provenance.json` files are not required to open it. To rebuild only the viewer from existing local artifacts, append `--viewer-only`. A fresh rebuild from PDFs/caches recreates images and parser/chunk text; fetching raw R2 excerpts and original provenance is a separate step.
