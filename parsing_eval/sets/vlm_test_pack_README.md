# Vision-model test pack

Hard pages from our 10-document parser sample (BSE/NSE filings). Use it to compare
vision models (accuracy and throughput) on a rented GPU.

## Contents

| Path | What |
|---|---|
| `images/<doc_id>_p<NNN>.png` | One page each, rendered at 200 DPI. **Feed these to every model** so all models see identical input. |
| `pdfs/*.pdf` | The same pages as subset PDFs, for models/pipelines that take PDFs. |
| `manifest.json` | Per page: category, why it is hard, and what a correct output must get right. |
| `questions.json` | 25 questions with verified answers over all 10 sample documents. Questions whose evidence page is in `images/` can be scored against model output from this pack. |

`<NNN>` is the 1-based page number in the **original** filing, matching `questions.json`.

15 pages across 7 documents:

| Doc | Company / type | Pages | Category |
|---|---|---|---|
| 719 | Aimtron audited results | 2, 3, 4 | Scanned tables, no text layer |
| 344 | Dixon Q3 FY22 results | 1, 3, 6 | Scan with a wrong embedded OCR layer; standalone (3) vs consolidated (6) |
| 310 | Dixon credit-rating letter | 1 | Scan with a wrong embedded OCR layer (A1+ read as "Al+") |
| 534 | Adisoft investor presentation | 26, 27, 28, 31 | Charts and KPI tiles; numbers exist only in images |
| 220 | Reliance investor presentation | 20, 65 | Bar charts; chart + table |
| 1 | Reliance annual report | 98 | Born-digital 2-up spread; EPS and signatory block |
| 712 | Aimtron call transcript | 7 | Speaker / text two-column layout |

## How to run

1. Use one prompt per model that asks for **markdown with tables** (headings as `#`,
   tables as markdown or HTML). Keep the prompt identical across pages; record it.
2. Run every image in `images/`. One page per request, plus a batched run if the
   serving stack supports it (throughput differs a lot).
3. Save raw output as `results/<model>/<doc_id>_p<NNN>.md`.

## What to report

**Throughput** (`results/<model>/timing.csv`):

```
model, gpu, precision, batch_size, image, seconds, input_tokens, output_tokens, peak_vram_gb
```

Plus model load time, and pages per hour at the best batch size.

**Accuracy**, two ways:

1. **Per-page checks:** for each page, mark each item in `manifest.json` → `check` as
   pass/fail (e.g. 719 p3: is 49.06 on "(a) Short term borrowings"?).
2. **Questions:** for questions whose evidence pages are all in this pack, answer
   from the model's markdown only. Score 1 if the answer matches `questions.json`
   (numbers exact, including decimals and units), else 0.

Questions answerable from the pack: Q02, Q03, Q04, Q06, Q07, Q08, Q09, Q10, Q11, Q12,
Q15, Q16, Q17, Q18, Q19, Q20, Q22, Q23, Q24 (19 of 25). The others need pages outside the pack
(born-digital, handled by the text-layer parser) and are for the full pipeline test.

Watch especially for: dropped or moved decimals, values shifted to the wrong row,
merged rows, ₹ symbol and units, chart values attached to the wrong period, and
invented numbers (a value that does not appear on the page at all).
