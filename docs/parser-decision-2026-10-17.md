# Parser decision — 2026-10-17

**Recommend MinerU 4.0.10, tier `advanced`, using MinerU2.5-Pro-2605-1.2B via vLLM 0.28, as cap-slice's default parser. Confidence: moderate in the choice for this financial-document mix; low in unattended operation at 11–14 million pages until the gates below pass.** Keep PaddleOCR-VL-1.6 as the challenger and a candidate for reviewed exceptions. Neither finalist is ready to supply unchecked financial facts at that scale.

The deciding preference is explicit: a plausible wrong amount, year or row is worse for financial Q&A than an acknowledged missing fact. MinerU advanced has fewer changed-number flags on the tested digital pages, handles several consequential statements better, and costs about one-third less at measured throughput. Paddle preserves more golden facts and has important genuine advantages on image dashboards. Those advantages prevent a high-confidence or universal recommendation for MinerU.

This selects a default configuration for subsequent validation. It does not authorize bulk acquisition, integration, paid indexing or GPU work. The indexer remains unchanged. Use the shared cleanup and structured chunker as the comparison baseline, but require the containment and context checks below before scaling.

## Evidence and reproducibility

Reviewed [AGENTS.md](../AGENTS.md), [PROGRESS.md](../PROGRESS.md), [the agreed plan](plan.md), the Lessons and relevant fixes in [bugs_resolved.md](../bugs_resolved.md), all golden-set definitions and sampling files, scorer/cleanup/chunker code, [number-fidelity method and audit](number-fidelity-check.md), [the previous recommendation](parser-selection-2026-10-06.md), the retained visual review, operational scripts and local run logs. The older GitHub branch reports are not the basis of this decision.

On this date, regenerated both finalists' v1/v2/v3 JSON and Markdown reports with the existing `cap-slice-score --clean`, using local caches and CPU only. **All six totals reproduce exactly.** Also rescored the two reference parsers in memory with the same existing functions; their totals reproduce. No source facts, implementation or scores were edited. For every finalist level disagreement, rendered its source PDF page with PyMuPDF at **200 dpi**, inspected the image, and compared cached page text with chunks regenerated from the **whole document**. Ground truth remained the page image. This covered **38 disagreements on 25 distinct pages**, plus four additional headline pages: **29 source pages** in total. This is targeted diagnosis, not a random accuracy sample.

Scratch reports: `/tmp/decision-2026-10-17/v{1,2,3}/{mineru_advanced,paddleocr_vl}.{json,md}`. Scratch page images, raw adapter text, cleaned text and complete covering chunks: `/tmp/decision-2026-10-17/audit/<fact-IDs>/{source.jpg,evidence.json}`; page manifest: `audit_manifest.json`. These scratch files are temporary; the case descriptions below preserve the findings in the repository. They can be regenerated from the local PDFs/caches and unchanged scoring functions.

Example reproduction from the repository root, using the installed environment without dependency installation:

```bash
PYTHONDONTWRITEBYTECODE=1 .venv/bin/cap-slice-score \
  --parser mineru --cache parsed_advanced --clean --name mineru_advanced \
  --facts data/golden/v3_facts.csv --skipped data/golden/v3_skipped.csv \
  --out /tmp/decision-2026-10-17/v3
```

For Paddle use `--parser paddleocr_vl --cache parsed --name paddleocr_vl`; substitute the v2 facts/skipped files, or v1 `parse_facts.csv` with no skipped file. The generated Markdown report title always says “Golden v2”; use its selected input and JSON summary to identify the set.

No Artifact tool is available, and the supplied hosted side-by-side URL was inaccessible through the web reader. The local self-contained [25-page viewer](../review/visual-2026-10-06/index.html) and its [findings](../review/visual-2026-10-06/README.md) were available; fresh source rendering and local caches underpin this review. No cloud objects were fetched or written, and no secrets were read. Initial disk checks were below the 500 MB floor; after the user explicitly instructed continuation and took responsibility for space, writes were limited to small documentation and roughly 8 MB of scratch evidence, without installs.

## Evidence per finalist

| Evidence | MinerU advanced | PaddleOCR-VL-1.6 | Interpretation |
|---|---|---|---|
| Golden v1 | **28/28** | 27/28 | Partly seen during chunker development; weak selection evidence |
| Golden v2 | 133/150 (88.7%) | **138/150 (92.0%)** | Previously unseen documents; current scores still include representation/context effects |
| Golden v3 | 94/123 (76.4%) | **98/123 (79.7%)** | Purposively difficult pages, not a prevalence estimate |
| Pooled descriptive total | 255/301 (84.7%) | **263/301 (87.4%)** | An eight-fact lead for Paddle; correlated facts and unequal strata prevent a population-accuracy claim |
| v3 tables / two-level headers | **56/69; 19/20** | 55/69; 18/20 | Small differences; both get rotated-table facts 10/10 |
| v3 chart points | 10/20 | **13/20** | Metric/title layout matters; both fail some charts badly |
| v2 + v3 image-only facts | 9/10 + 18/27 = 27/37 | **8/10 + 23/27 = 31/37** | Only 12 pages; several score differences are spacing, escapes or chunking |
| Number-fidelity output on 7,318 digital pages | 208,151 page-distinct numbers | 212,610 page-distinct numbers | Same eligible pages, 224 documents |
| Changed-number flags | **458; 22.0 per 10,000 outputs** | 974; 45.8 per 10,000 | About 2.1× more flags for Paddle, not a calibrated rate of financial misstatements |
| Other numbers absent from text layer | **1,144** | 2,682 | Includes estimates, text-layer gaps and tokenization effects |
| Printed numbers missed | 13,234/219,783 = 6.02% | **10,829/219,783 = 4.93%** | Paddle's recall gain is 1.09 percentage points |
| Existing 15-flag audit per finalist | 3 misreads, 8 chart estimates, 3 text-layer gaps, 1 unclear | 7 misreads, 3 chart estimates, 1 text-layer gap, 4 unclear | Small audit; suggests different error mechanisms, with substantial uncertainty |
| Freshly verified financial failures | Hero year shifts and omitted series; invented dashboard N/A; wrong chart-series label | E2E wrong row/year assignments, omitted prior-year figures; changed amounts; APAR EBITDA misread; C2C inventory misread | Neither guarantees row/column fidelity; examples below |
| Freshly verified generation failures | Repeated/variant Ecuador table survives cleanup | Assurance-page repetition survives cleanup | Existing picture stripping does not contain all generated content |
| Full-run coverage | **228/228; 12,980 pages** | **228/228; 12,980 pages** | Final cache coverage and successful run records do not imply content correctness |
| Measured aggregate throughput | **3.9095 pages/s** | 2.5668 pages/s | Sum shard pages over earliest start to latest end, not sum of per-process rates |
| Compute at 11–14M pages, $1.01/hour | **782–995 GPU-hours; $789–1,005** | 1,190–1,515 GPU-hours; $1,202–1,530 | Historical pod price, linear extrapolation; excludes startup, storage, checks, retries and review |
| GPU sampling, unique timestamps | Mean utilization **87.6%**; peak 29,769 MiB | Mean utilization 56.4%; peak **28,054 MiB** | Paddle has utilization headroom, not unlimited VRAM headroom |
| Operations | Four runner processes, one worker each, shared VLM server; peak runner RSS ~12 GB each | Two client processes, one worker each, concurrency 64 per client; peak RSS 12.9/14.5 GB | Both require resource supervision and pinned environments |
| Stack burden | CUDA/Blackwell and vLLM compatibility; memory trimming and process orchestration | Separate `paddle` and `vllm030` environments; layout clients plus VLM server | See [GPU runbook](gpu-run.md), [pod steps](pod-steps.md), [Paddle settings](paddleocr-vl.md), and fixes I13–I16 |

The recorded cost rows round MinerU to $790–1,000 and Paddle to $1,200–1,530. The table above uses the independently reproduced rates. MinerU is **52.3% faster**, with **34.3% lower compute cost**. One GPU would take about 33–41 versus 50–63 continuous days. Parallel GPUs shorten elapsed time only if feed, storage and supervision scale too.

Paddle continuous feeding was never tested. At the same hourly rate it needs approximately **3.91 pages/s**, a **52% gain**, to erase the measured compute gap. Its 56% mean utilization makes improvement plausible, but an imagined gain cannot enter the budget. A throughput tie would remove one reason for MinerU, not resolve digit or column errors. Any future tuning must measure quality again as well as successful pages per billed hour.

Reference only: **MinerU standard 20/28, 119/150, 72/123 = 211/301**, about 10.5 pages/s and $300–380. Its ~5 changed-number flags per 10,000 and speed do not compensate for table collapse and lower fact survival. **Docling 27/28, 111/150, 55/114 = 193/292 scored facts**, about 3.0 pages/s and $1,015–1,290. Operationally that is 193/301 when unavailable facts count as missing. Its final cache covers 226 PDFs / 12,830 pages: one error record and one document absent after reader/OOM failure. Standard's two initial document failures were recovered on retry. These operational histories argue for explicit started/failed/complete accounting rather than trusting a final success count alone.

## Every finalist disagreement

Here **A = MinerU advanced**, **P = Paddle**; `level/chunk` gives the recorded level and zero-based best chunk. `0/—` means no value match. Source names below are exact filenames under the symbol's indicated document folder; pages are one-based **PDF pages**.

There are **32 full-credit disagreements**: A alone passes 12 facts and P alone passes 20. Six further facts differ below L4. Both pass 243 facts and both miss full credit on 26. These counts reproduce the eight-fact pooled margin. They are not counts of genuine reading errors.

Primary diagnostic grouping of the 38 differences: **3 misread/corrupt-text cases; 11 dropped-content cases (one caused by chunking); 3 wrong-row/column cases; 7 structure/context cases; 14 formatting/scorer cases.** Cases can have secondary defects, as recorded below. Do not turn these selected cases into an adjusted accuracy leaderboard: that would ignore shared failures and over-weight related facts on the same page.

### Misread text or amount

| Fact | Source | A | P | Image and chunk finding |
|---|---|---|---|---|
| V045 | E2E results `2026-04-20_Q4-FY2025-26-quarterly.pdf` p.4 | 4/7 | 0/— | Image `(1,26,245.03)`; Paddle writes `(1,262,245.03)` in chunk 20. Genuine changed amount; comma normalization cannot fix it. |
| V050 | Same results p.2 | 0/— | 4/15 | Image `premium of INR 2,490 per share`; A chunk 3 has `JNR 2,490per share`, matching defects in the embedded OCR layer. The digits 2,490 are correct: this is corrupt text/spacing, not a wrong premium amount. Evidence against unconditional trust in a text layer. |
| W061 | APAR concall `Feb-2020-a.pdf` p.1 | 4/0 | 1/0 | Both retain Harishkumar Malsatter; Paddle reads the printed `Assistant Manager` as `Assistantant Manager`. Genuine role-label misread, not a numeric error. |

### Dropped content

| Fact | Source | A | P | Image and chunk finding |
|---|---|---|---|---|
| V032 | APAR AR `FY2012-13.pdf` p.105 | 4/351 | 0/— | Printed auditor membership `033013` survives in A; Paddle omits the membership/name detail. |
| V033 | Same p.105 | 4/351 | 0/— | Printed registration `109982W` survives in A; Paddle omits it. A nevertheless misassigns the CEO detail elsewhere on this page; these two successes do not certify the whole table. |
| W018 | APAR presentation `May-2018.pdf` p.23 | 4/53 | 0/— | Printed FY15 EBITDA margin `5.0%`; Paddle drops the margin series. A retains it, but calls the column `Growth Rate (%)` despite the EBITDA-margin caption. |
| W050 | APAR concall `Nov-2017-a.pdf` p.1 | 0/— | 4/0 | `SEC/2511/2017` is correct in A's cached page but disappears from its chunks 0–2. **Chunker deletion**, not parser failure. |
| W058 | Hero AR `FY2012-13.pdf` p.165 | 0/— | 4/422 | Image CFO `RAVI SUD`; A omits the name; Paddle retains it amid spurious signature text. |
| W059 | Same p.165 | 0/— | 1/422 | Image `PRADEEP DINODIA`; A omits it. Paddle retains the name but drops `Audit Committee Chairman` and collapses the signature block; neither preserves the complete association. |
| W094 | Hero AR `FY2012-13.pdf` p.30 | 0/— | 1/37 | Printed FY2009–10 EPS `111.8`; A omits the EPS series. Paddle keeps the correct year/value but places the metric name on the preceding row, failing same-row scoring. |
| W096 | Same p.30 | 0/— | 1/37 | Printed FY2009–10 dividend `5,500%`; A omits the series. Paddle retains it with the metric name on the preceding row. |
| W097 | Hero AR `FY2011-12.pdf` p.34 | 0/— | 1/29 | Printed FY2011–12 sales `6,235,205`; A shifts the series and drops the final value. Paddle retains the value under the correct year, with a separate metric-title row. |
| W100 | Same p.34 | 0/— | 1/30 | Printed FY2009–10 dividend/share `110`; A omits the series; Paddle retains it under the correct year. Its low score is the title/value row separation. |
| W116 | E2E AR `2021-08-25_FY2020-21.pdf` p.52 | 4/151 | 0/— | Printed FY2020 profit `(93,533,720)` is omitted by Paddle's collapsed surplus table (chunk 149). A retains the loss on its own row. |

### Wrong row or column

| Fact | Source | A | P | Image and chunk finding |
|---|---|---|---|---|
| F13 | E2E AR `2023-09-21_FY2022-23.pdf` p.124 | 4/247 | 1/237 | Printed after-tax profit `990.99` is on an unlabelled row in Paddle; its profit label instead receives tax subtotal `332.63`. Both numbers exist, but the association is wrong. |
| W098 | Hero AR `FY2011-12.pdf` p.34 | 3/29 | 1/29 | Printed profit after tax `1,928` belongs to FY2010–11. A puts the unit into the first year's cell, moves 1,928 to FY2011–12, and drops the final year's profit. Paddle is semantically better here despite its **lower** score: its title is on a separate row, while the values and years are correct. |
| W114 | E2E AR `2021-08-25_FY2020-21.pdf` p.52 | 4/153 | 1/151 | Printed short-term leave provision `159,894` belongs to March 2021. Paddle assigns the amounts to gratuity and shifts subsequent labels. A retains the right row and year. |

### Table structure and chunk context

These remain real pipeline defects even where the parser read the target correctly. They should not be counted as digit-reading errors.

| Fact | Source | A | P | Image and chunk finding |
|---|---|---|---|---|
| V040 | Esconet results `2025-11-14_H1-FY26-half-yearly-SME.pdf` p.5 | 4/7 | 2/7 | Both pages have cash `3,132.97` in March 2025. Paddle's extra title row pushes the date row beyond the chunker's three repeated header rows; its final table part loses the year header. |
| V106 | APAR presentation `May-2023.pdf` p.17 | 2/19 | 4/21 | Both retain Power and Telecom Cables `101.4` under Q3 FY23. Image footer supplies INR crore; A's table chunk lacks it. P carries units but also the prior slide's section title. |
| V107 | Same p.17 | 2/19 | 4/21 | Both retain finance costs `45.8` under Q4 FY22; same units/context issue. The raw score difference does not indicate a different numerical reading. |
| V111 | Hero concall `Feb-2026.pdf` p.15 | 1/29 | 4/35 | Both read the PLI question and one-model answer. A represents dialogue as a table; splitting separates question and answer. Its cached page also duplicates the pair. Neither output fully preserves the unrelated ABS discussion on the source page. |
| W019 | APAR presentation `May-2018.pdf` p.23 | 4/51 | 2/34 | Both correctly retain FY18 exports `2,087`. P's units line occurs later in reading order, so the exports chunk lacks `Rs crore`; not a numeric error. |
| W039 | E2E AR `2019-07-24_FY2018-19.pdf` p.3 | 4/0 | 1/1 | Both read Statutory Auditors / B. B. & Associates. P's chunk 1 loses the role heading and inherits `Bankers`; parser reading is correct. |
| W040 | Same p.3 | 1/0 | 4/0 | Both read Company Secretary / Neha Baid. A's chunk 0 loses the correct heading and puts `Secretarial Auditors` above her name. A context failure with potential semantic consequences. |

### Formatting or scorer artifacts

| Fact | Source | A | P | Image and chunk finding |
|---|---|---|---|---|
| V037 | E2E AR `2024-08-20_FY2023-24.pdf` p.17 | 1/16 | 4/18 | A writes `SrishtiBaweja`; P writes `Srishti Baweja`. Both preserve the printed COO & Whole Time Director role. Spacing defect, not a lost identity. |
| V070 | APAR presentation `Nov-2017-a.pdf` p.35 | 1/83 | 4/79 | Both retain H1FY18 `1,061.5` correctly. A's label uses literal `&amp;` instead of `&`. |
| V096 | APAR presentation `Feb-2020-a.pdf` p.38 | 1/96 | 4/99 | Both retain 9M FY19 `1,933.6` correctly; same entity mismatch. Other rows on this page have their own structure risks. |
| V108 | APAR presentation `Feb-2022.pdf` p.26 | 1/47 | 4/43 | Both retain 9MFY21 `1,645.2` correctly; same entity mismatch. |
| V148 | Hero AR `FY2016-17.pdf` p.80 | 0/— | 4/235 | A chunk 225 uses curly `arm’s`; P uses straight `arm's`. Both preserve the related-party statement. |
| W004 | E2E presentation `May-2021.pdf` p.23 | 0/— | 4/20 | Dec'20 `21%`: A chunk 20 writes 21 under `Value (%)`; P writes `21%`. Equivalent target. |
| W005 | Same p.23 | 0/— | 4/20 | Feb'21 `23%`: same percentage representation issue. |
| W027 | APAR presentation `Aug-2020.pdf` p.22 | 1/65 | 4/42 | Both retain Transformer & Specialty Oils `3.9%` in Q4 FY20. A uses `&amp;`; P uses `&`. |
| W036 | E2E presentation `Jan-2025.pdf` p.29 | 2/34 | 4/35 | Both read Q1FY25 `749,690` on the raster chart; A escapes `\~ARPU`, so the literal context fails. |
| W037 | Same p.29 | 2/34 | 4/35 | Both read Q3FY24 `406,307`; same escape issue. |
| W038 | Same p.29 | 2/34 | 4/35 | Both read Q3FY23 `285,521`; same escape issue. These three facts do not establish a scanned-chart reading advantage for P. |
| W060 | APAR concall `Feb-2020-a.pdf` p.1 | 0/— | 4/0 | A chunk 0 writes `EarningsConference` and `January24,2020`; P uses spaces. The printed date and meaning survive in both. |
| W106 | APAR presentation `Feb-2018.pdf` p.35 | 1/81 | 4/78 | Both retain segment results `132.5` in 9MFY17; A's literal `&amp;` prevents the label match. |
| W121 | E2E AR `2022-07-29_FY2021-22.pdf` p.91 | 4/309 | 1/289 | Both retain `5.14% to 6.43%` under March 2022; label differs only by en dash versus hyphen in `Risk-free`. |

Two especially important lessons follow. **A low score can conceal a correct table** (Paddle's Hero dashboard), and **a higher partial score can reward a worse association** (W098). The fourteen formatting cases also include genuine output-readability defects; calling them artifacts does not make the current pipeline adequate. No hypothetical score corrections were applied.

## Headline cases re-verified beyond the score table

The disagreement table already covers E2E FY2020–21 p.52, E2E April-2026 results p.4, APAR May-2018 p.23, and both Hero dashboards. Their source renders confirm the prior reports, with the qualifications recorded above.

Four additional pages were independently rendered at 200 dpi and compared with both cached `pages.json` outputs:

| Source PDF / page | Fresh finding |
|---|---|
| `data/E2E/annual_reports/2023-09-21_FY2022-23.pdf` p.125 | Source cash-flow subtotals for 2023/2022 are **3,552.93 / 2,588.52**, **(2,065.18) / (1,919.21)**, **(240.78) / (200.69)**. A retains the pairs. P inserts A/B/C into the 2023 column, puts the current amount under 2022 and omits all three prior-year subtotals. |
| `data/C2C/annual_reports/2025-09-08_FY2024-25.pdf` p.104 | Image finished goods **5,882.60**; P writes **5,892.60**, even while retaining the correct total. P also drops rightmost ageing totals and puts prior-year related-party **65.06** in an extra numeric column. A preserves these values. The source's ageing “Total” heading itself is awkward; preserving that layout is not a semantic repair. |
| `data/APARINDS/investor_presentations/Aug-2024.pdf` p.123 | The source contains assurance-document thumbnails and scope descriptions. P produces **62,253 characters**, with `Page 1 of 2` repeated 372 times, `Account 1` 371 times, and unrelated sphere-volume prose. A also generates unsupported thumbnail descriptions, but shared removal rules reduce its 10,071 raw characters to 597; P retains 61,659 cleaned characters and the repetition. The removal-rule check used the complete document without optional PDF-unit restoration, which cannot remove these loops. This demonstrates useful containment on this page, not blind trust in A. |
| `data/APARINDS/investor_presentations/Sep-2024.pdf` p.140 | Source trade-flow map plus CBAM bullets; A produces an extensive Ecuador table, including eleven identical `Ecuador / 3.3%` rows and extrapolated percentage sequences. It is ordinary table text and survives the existing cleanup. P retains the main text without that table. |

Hero FY2012–13 p.30 explicitly has metric titles and actual plotted/printed series, **not N/A data cells**. A invents N/A cells in title rows and omits EPS/dividend series. Hero FY2011–12 p.34 is the stronger counterexample: A's unit-as-first-value error silently shifts the years. Both failures survive candidate chunking. They rule out describing MinerU's harmful output as exclusively isolated in removable picture blocks.

The 30-number audit's five existing contact sheets were also opened. They support the report's warning that some flags are charts, text-layer gaps or unclear crops. Their small size does not justify converting 22 versus 46 flags into precise audited error rates.

## What the number check establishes—and what it does not

The [method](number-fidelity-check.md) compares **sets of unsigned normalized numbers per page**, with at least three digits. It ignores sign, Indian/Western comma grouping, row position, column position and repeated occurrences. Its digital-page filter requires at least 300 text characters, image coverage below 10%, and at least five source numbers; 7,318 of 12,980 pages qualify after common-cache restrictions. It neither tests scans nor measures whether a financial tuple is correct.

Therefore:

- Fewer flags favor A's **observed end-to-end numeric fidelity on eligible digital pages**, while P's lower omission rate is a real opposing signal. The 1.09-point recall gain does not outweigh the numerical/structural risk for this application.
- A number moved into the wrong year or row can pass completely. So can a wrong sign, or a spurious occurrence of a number printed elsewhere on the page. Both finalists have source-confirmed errors in this blind spot.
- “Changed” means proximity to some source number, not demonstrated causation. Chart estimates often resemble axis ticks. The 15-per-parser audit classifies 11/15 A and 10/15 P flags as errors, but has wide uncertainty and does not audit the much larger “other” category.
- The check is selected toward digital, low-image pages and five issuers. Its rates cannot be projected unchanged to scan-heavy historical filings, photographed statements, regional-language content or the entire exchange population.

### MinerU native-text provenance remains unresolved

Inspected **all 228 advanced `meta.json` files**: 214 say `parse_mode=txt`, 14 `ocr`; all specify advanced tier. The adapter records this from `middle.extensions.mineru`. **No `mineru_middle.json` files are present in the local full advanced cache**, even though metadata lists them as saved raw files. `pages.json` is rendered adapter text and carries no per-span origin. Selected raw excerpts embedded in the previous viewer do not provide corpus-wide provenance.

Consequently, metadata establishes the selected mode, **not the fraction of characters or cells copied from native text**. Matching native text is not proof of copying; a VLM can reproduce it. The visibly defective prose on E2E results p.2 is consistent with using its bad embedded OCR layer, but does not establish a corpus-wide mechanism. Do not call A an image-only measurement or claim its lower flag rate will hold on scans. Record per-block extraction origin/server activity in a later validation run if available; this review neither fetched cloud raw data nor started another run.

## Risks, routing and confidence

**Scanned financial evidence is insufficient for generalization.** The 37 v2/v3 image-only facts cover just four plus eight pages, many containing letters, signatures or designed slides rather than financial statements. Three v3 scan-slide losses for A are the same escaped-title issue on one page. V1 contributes six statement facts from a development document, and the additional scanned cash-flow case favors A, but neither is a broad independent financial-scan evaluation. P's 31/37 versus A's 27/37 is evidence to investigate, not an automatic scan-routing rule.

**A targeted scanned-statement check is required before scaling**, although it need not delay choosing A as the provisional engineering default. Begin with unused pages in the existing caches, with image-grounded tuples; before 11–14M-page deployment, broaden to issuers and scan styles outside this five-company pilot. Confidence is especially low for degraded scans and regional-language material.

**A hybrid is a hypothesis, not the selected production design.** Native text is valuable as a digital-page validation channel, and a fast path for ordinary prose may eventually save money. The current evidence does not validate a router: standard/Docling retain digits but lose structure; embedded OCR can be wrong; the low-text threshold includes blanks/vector outlines; and neither finalist universally wins charts or scans. Do not route all “digital” pages to standard, all low-text pages to Paddle, or choose whichever output looks longer. A reviewed Paddle fallback for flagged dashboards is plausible; accepting whichever candidate contains a number is not verification. Dual parsing the whole corpus is unjustified by current evidence and roughly adds both compute budgets.

**Retrieval and answer accuracy remain unmeasured.** L4 tests the best single chunk covering a fact's page, assuming perfect retrieval. Non-table prose/Q&A need only the label and value in a chunk; chart-point/key-value facts get full credit at L3. Even L4 is not exhaustive semantic table validation. Shared missing context, false continuations, incorrect group headers and invented facts outside the golden list can escape every aggregate score. Nothing has been embedded, and current production indexing still uses the baseline flattening path.

## Required gates before scaling

These are proposed acceptance conditions, **not implemented or passed fixes**. Preserve the tested parser/model/tier and raw output, source PDF hash, page/block geometry, cleanup/chunker versions and rejection reasons. Any future model, renderer, serving or decoding change needs revalidation.

| Gate | Required behavior | Acceptance evidence before scale |
|---|---|---|
| Generated content and charts | Keep descriptions/estimates separate from issuer evidence. Exclude decorative-photo numbers and chart values inferred from geometry from factual financial chunks. Retain printed chart labels only with verified category/series associations. Ordinary generated tables need region provenance too; `<details>` stripping alone is insufficient. | Reject/quarantine the APAR Ecuador table and assurance loops, plus the prior review's decorative-tablet examples; retain valid labelled APAR charts. Audit false exclusions as well as surviving unsupported content. If provenance cannot distinguish an estimated chart table reliably, quarantine it rather than index it as exact data. |
| Repetition and output growth | Detect exact and variant row/prose loops, implausible output expansion and missing expected regions. Bound retries; persistent suspects remain quarantined with visible missing-coverage status. | Both finalists' known loops must be caught. Legitimate repeated labels, subtotals and continued tables must survive. Measure false rejection, retry cost and final missing pages. A repetition penalty alone is not a quality guarantee. |
| Digital numeric validation | Compare against **nearby source spans in the same region/row**, including signs, decimal points, units and periods. A one-digit difference may be corrected only when source-layer quality and unique spatial correspondence are verified; preserve before/after provenance. | Validate precision of proposed corrections against page images, including C2C 5,882.60, known faulty embedded OCR, and multiple nearby similar values. Never snap to the nearest number anywhere on a page or silently repair printed inconsistencies. Uncertain mismatches are flags, not corrections. |
| Row/year/column integrity | Check header/body widths, hierarchy, note/marker columns, unit placement, year ordering and subsection identity. Use totals/roll-forwards where applicable as alarms, not proofs. Retain original cell geometry/HTML for source checks. | Catch A's Hero shift and P's E2E A/B/C/leave-provision failures; keep valid rotated/grouped tables. Quarantine ambiguous associations. Numeric agreement or balanced totals alone must not release a table. |
| Chunk context and continuation | Carry the correct local title, year, unit and subsection through splits; stop stale captions and unrelated same-width table joins. Preserve compact label/value and Q&A pairs and semantic identifiers. | Source-check V040, V106/107, V111, W019, W039/040, W050 and the prior review's continuation/key-value cases. No wrong `Bankers`/secretarial role, previous-slide units or auditor heading should supply an answer's semantics. |
| Fair evaluation | Normalize harmless entities, escapes, punctuation and equivalent percentages consistently; keep original numbers and wrong columns distinguishable. Review source/chunk evidence for every score change. | The 14 listed artifacts become regression cases alongside true failures; rescore v1/v2/v3 equally for every finalist. Do not tune and claim fresh validation on those same facts. |
| Independent financial check | Test complete **label/value/sign/unit/year/column tuples**, and count unsupported extra tuples and omissions, not just named-value recall. Include digital, bad-OCR, scanned, chart and continued/grouped tables; sample across documents/issuers. | Suggested minimum before broad rollout: 100 scanned financial pages from at least 30 documents/20 issuers, with at least 500 image-labelled tuples, plus a separate digital/chart sample of at least 500 tuples. Freeze sample before output review. All known critical cases must be corrected or quarantined; no unflagged material digit/sign/year/row error in the release audit; report omissions, quarantine rate and document-clustered uncertainty. This is a release gate, not proof of zero errors in millions of pages. |
| Operational completeness | Persist started/failed/quarantined/complete states; verify expected unique page IDs/counts and source hashes. Use process memory/time limits, bounded retry/resume and full manifests. Test actual CUDA/model activity, not only health flags. | Pilot restart/OOM/timeout tests leave no silently skipped documents or stuck shards. Resource limits respect container RAM; both peak VRAM and RAM fit. Budget checks/retries/review, not just successful-parser throughput. |
| Retrieval, then indexing | Follow the agreed plan: source-page questions across the whole pilot, chunking experiments judged by retrieval, then embedding choice/indexing. Version every indexed payload so corrected output can replace old vectors. | Freeze roughly 100 representative questions with cross-company/year distractors; measure source-page recall@k, correct year/units and answer numeric correctness, with rejection/abstention tracked. Predeclare acceptable retrieval targets. Parser L4 alone cannot pass this gate. |

The proposed sample sizes are engineering minimums, not statistical certification. Multiple facts on one page are correlated; a clean 500-tuple audit does not imply a 0.6% upper error bound for this corpus without independence and sampling assumptions. If these gates cannot contain silent column errors at an acceptable omission/quarantine rate, stop expansion and reassess the parser or introduce source-image verification at answer time.

## What would change the decision

Switch the default toward Paddle if an independently sampled, image-grounded financial-tuple audit shows equal or fewer **unflagged material numeric/association errors**, with better recall, after applying the same allowed cleanup/checks to both. A scan-heavy target corpus with a demonstrated Paddle advantage could justify routing or a different default. Its current dashboard counterexamples warrant that investigation.

Reassess MinerU if chart-estimated ordinary tables cannot be reliably separated from evidence, if its year shifts recur after quality checks, or if broader scans reveal that the digital fidelity advantage depended on native text. Improved Paddle throughput near or above 3.91 pages/s would remove the cost advantage, but speed alone would not settle the financial-quality tradeoff.

Adopt a hybrid only after a frozen routing experiment shows better quality/cost **including route mistakes, validation, retries and missing content**. A strong failure detector with a source-verified fallback could be more valuable than a small raw-score gain. Reopen either parser choice if retrieval tests reverse the answer-quality outcome, or if a version change materially alters results.

**Decision for review:** MinerU advanced is the better-supported default for the present financial Q&A objective, with moderate confidence. Paddle remains credible and superior on some important layouts. Release confidence depends on evidence that the proposed gates work, especially on scanned statements, generated chart tables and silent row/year shifts.
