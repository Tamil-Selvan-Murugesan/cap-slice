# Do PDF parsers change the numbers? A check against the PDF's own text layer

*2026-10-06 · cap-slice · four parsers on 12,980 pages of Indian company filings*

When you put financial filings into a search or Q&A system, the worst thing a parser can do is not
drop a number — it is to output a **wrong number that looks like any other number**. Accuracy
benchmarks usually check a few hundred hand-picked facts, so a digit changed in a cell nobody wrote a
fact for never shows up. This check measures it across every digital page of the collection, without
hand-labelling anything.

## The idea in one paragraph

Most filings are "digital" PDFs: besides the picture of the page they carry a **text layer**, the
exact characters the publisher typeset. Vision-based parsers (MinerU, PaddleOCR-VL) read the page
**image** instead. So on a digital page we have an answer key for free: every number a parser outputs
should also be in the page's text layer. A number that isn't there was either misread, invented, or —
rarely — the text layer itself is incomplete. We count those, then check a random sample by eye to
see which is which.

## Headline results

7,318 digital pages from 224 documents (annual reports, concall transcripts, investor presentations,
results), 200,000+ numbers per parser:

| Parser | Numbers output | Printed on the page | **Changed** (one digit / decimal off a printed number) | per 10,000 numbers | Other numbers not on the page | Printed numbers missed |
|---|---|---|---|---|---|---|
| **MinerU 4.0.10, advanced tier** (MinerU2.5-Pro VLM) | 208,151 | **99.23 %** | 458 | **22** | 1,144 | 6.0 % |
| **PaddleOCR-VL-1.6** (full pipeline) | 212,610 | 98.28 % | 974 | **46** | 2,682 | **4.9 %** |
| MinerU 4.0.10, standard tier | 200,049 | 98.51 % | 96 | 5 | 2,890 | 10.3 % |
| Docling 2.130 (OCR only on low-text pages) | 203,137 | 99.70 % | 109 | 5 | 500 | 7.9 % |

"Changed" numbers per 10,000, by document type:

| | Annual reports | Concall transcripts | Investor presentations | Results |
|---|---|---|---|---|
| MinerU advanced | 17 | 0 | 61 | 55 |
| PaddleOCR-VL | 36 | 33 | 116 | 0 |
| MinerU standard | 2 | 0 | 25 | 54 |
| Docling | 3 | 120 | 2 | 0 |

(Results pages: only 16 eligible pages, so that column is noisy.)

**What a manual audit of a random sample found** (15 flagged numbers per vision parser, each checked
against the page image — details below):

| Of 15 flagged numbers | MinerU advanced | PaddleOCR-VL |
|---|---|---|
| Misread a printed number (2,852.00 → 2850.00; 394 → 374; 2007 → 2017) | 3 | **7** |
| Wrote a value printed nowhere on the page (estimated from a chart's shape) | **8** | 3 |
| False alarm: the number is printed, the text layer lacks or garbles it | 3 | 1 |
| Can't tell from the image | 1 | 4 |
| **Real parser errors** | **11 / 15** | **10 / 15** |

**Takeaways**

1. **PaddleOCR-VL outputs about twice as many wrong numbers as MinerU advanced** on digital pages (46 vs
   22 flagged per 10,000, and 2.3× as many other numbers not on the page). About 70 % of flags are real
   errors for both, so the comparison holds.
2. **The errors are of different kinds.** PaddleOCR-VL mostly **misreads printed numbers** (digits and
   decimal points). MinerU advanced mostly **turns charts into tables of estimated values** — numbers that
   look like data but were never printed. Both are wrong for a financial index; the second is easier to
   contain (it happens on chart regions).
3. **PaddleOCR-VL misses slightly fewer printed numbers** (4.9 % vs 6.0 %). It finds a little more and
   gets more of it wrong — which is why it can edge ahead on "did this fact survive" benchmarks while
   being worse on "is this number right".
4. **Text-layer-based parsers rarely change digits** (MinerU standard, Docling: ~5 per 10,000) because
   they copy the publisher's characters — but on this collection they break table structure more
   (MinerU standard collapsed some balance sheets into one row), which this check does not see.
5. **Presentations are the weak spot for both vision models** (61 and 116 per 10,000): stylised slides,
   charts and KPI tiles.

## What was compared

| | Version / settings |
|---|---|
| MinerU advanced | MinerU 4.0.10, tier `advanced`, VLM `opendatalab/MinerU2.5-Pro-2605-1.2B` (bf16) served by vLLM 0.28.0; MinerU classified 214 of 228 documents `parse_mode=txt`, 14 `ocr` |
| MinerU standard | same, tier `standard` |
| PaddleOCR-VL | PaddleOCR-VL-1.6 (0.9B), `pipeline_version="v1.6"`, chart recognition on, OCR inside picture blocks on, pages rendered at 200 dpi, VLM served by vLLM ≥ 0.30, 64 region requests in flight per client — the settings of an independent evaluation by a co-founder |
| Docling | 2.130.0, RapidOCR 3.9.2 on GPU, OCR only on pages with < 50 characters of text or ≥ 75 % image cover (otherwise the PDF text is used) |
| Hardware | one RTX 5090 (32 GB) on RunPod, driver 610 / CUDA 13; all parsers ran on the full collection |

Every parser's output went through the same clean-up step before counting (`src/cap_slice/page_clean.py`:
removes MinerU's marked picture descriptions, unwraps layout HTML, normalises LaTeX superscripts), so
the numbers counted are the ones that would be indexed.

## Data

Public filings of five NSE-listed companies (APAR Industries, Hero MotoCorp, E2E Networks, Esconet
Technologies, C2C Advanced Systems), downloaded from the NSE/BSE archives: 228 PDFs, 12,980 pages —
7,586 annual-report pages, 3,126 presentation pages, 2,230 concall-transcript pages, 38 results pages.

## Method, step by step

1. **Pick digital pages** (`data/golden/page_inventory.csv`): not flagged low-text, ≥ 300 characters
   of text, images covering < 10 % of the page. 10,971 pages qualify.
2. **Keep pages every parser produced** (Docling's PDF reader failed on 2 documents) and that have at
   least 5 numbers in the text layer: **7,318 pages, 224 documents**.
3. **Extract numbers** from the text layer (PyMuPDF `get_text()`) and from each parser's cleaned page
   text with one rule: a run of digits with optional thousands separators and decimals
   (`\d[\d,]*(\.\d+)?`), at least 3 digits. Separators and signs are ignored, so Indian and Western
   grouping compare equal ("1,57,280.58" = "157,280.58" = "157280.58"). Numbers are compared **per
   page, as sets** (a number repeated on a page counts once).
4. **Classify each parser number:** on the page → correct. Not on the page → if it has the same length
   as a number printed on that page and differs in exactly one character (a digit or the decimal
   point) or by two swapped neighbouring digits → **changed**; otherwise **other**.
5. **Missed** = printed numbers on the page the parser didn't output.
6. **Audit:** a seeded random sample (seed 20261006) of 15 "changed" numbers per vision parser; for each,
   the line of the page around the matched printed number is rendered at 200 dpi with that number boxed,
   and a person classifies it (misread / chart estimate / text-layer gap / unclear).

## Audit details

All 30 crops are in `review/number_fidelity/audit_sheet_1..5.png`, verdicts in `audit_sample.csv`.
Typical cases:

- **Misread (PaddleOCR-VL):** a share-price table prints `2,852.00`, Paddle wrote `2850.00`; a KPI band
  prints `394`, Paddle wrote `374`; body text "August 9, 2007", Paddle wrote `2017`; "Vision 2020" →
  `2023`; "100-125cc" → `107`.
- **Misread (MinerU advanced):** "a final dividend @ 1,250%" → `2250`; share-price low `2,150.00` →
  `2450.00`; `2705` → `2750`.
- **Chart estimate (mostly MinerU advanced):** on line and bar charts whose data points carry no labels,
  MinerU outputs a table of values (`8320`, `26300.00`, `28300.00`…) read off the chart's shape; the only
  printed numbers nearby are axis ticks (`8300`, `26000.00`, `28000.00`), which is why the check matched
  them.
- **False alarm:** a bar label `3.50*` that the text layer glues to its neighbour as `3.453.50*`; chart
  year labels and axis labels drawn without text in the text layer.

The sample is small: proportions like 3/15 or 7/15 carry wide uncertainty (roughly ±20 points). Read
them as "which kind dominates", not as precise rates.

## What this check does not catch

- **Right number, wrong place.** A printed number moved to the wrong column or row passes. In a separate
  review, PaddleOCR-VL shifted an operating-cash-flow figure one column and dropped the prior year, and
  MinerU filled block titles with invented "N/A" cells; neither shows up here. This check understates
  structural errors.
- **Scanned pages.** No text layer, no answer key. These pages often matter most and need a separate,
  hand-labelled set (our golden v3 includes 27 facts on image-only pages).
- **Text-layer errors.** Occasionally the publisher's text layer is wrong or incomplete (glued labels,
  missing chart labels); those show up as false alarms (4 of 30 in the audit).
- **How MinerU uses the text layer.** MinerU marked most documents `parse_mode=txt`; we did not inspect
  how much of the advanced tier's text comes from the text layer rather than the VLM. The measured rates
  are what each parser delivers end to end.
- **Only five companies**, Indian filings, one GPU type. Rates on other document families will differ.
- The **Docling concall figure** (120 per 10,000) was not investigated; Docling uses the text layer on
  these pages, so it is most likely a tokenisation artefact (hyphenated or joined numbers), not misreads.

## Reproduce

```bash
# parser caches: parsed/<parser>/<doc>/pages.json (cap-slice-parse), PDFs in data/
uv run python tools/golden/number_check.py parsed_advanced/mineru parsed/paddleocr_vl parsed/mineru parsed/docling \
    --out review/number_fidelity                     # ~7 min on a laptop CPU
uv run python tools/golden/number_audit.py review/number_fidelity --per-parser 15
# then look at audit_sheet_*.png and fill the verdict column of audit_sample.csv
```

| File | Content |
|---|---|
| `tools/golden/number_check.py` | the check |
| `tools/golden/number_audit.py` | seeded audit sample + contact sheets |
| `review/number_fidelity/summary.json` | all counts, per parser and document type |
| `review/number_fidelity/flagged.csv` | every "changed" number (1,637): parser, document, page, what the parser wrote, nearest printed number |
| `review/number_fidelity/audit_sample.csv`, `audit_sheet_*.png` | the 30 audited numbers with verdicts and the page crops |

## What we do with it

This result points us towards **MinerU advanced** for this project (the final call is still open). And because even its
rate means hundreds of thousands of altered numbers at our target scale (11–14M pages), the next step is
a post-check on digital pages: snap a parser number that is one digit or one decimal point away from a
number printed nearby to the printed value, and drop chart-estimated tables (or label them as
estimates) before indexing.
