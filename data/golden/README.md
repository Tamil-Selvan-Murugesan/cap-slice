# Golden set

Ground truth for comparing PDF parsers and chunkers. **Every fact is read by a person/agent off a rendered page image — never copied from any parser's output.** (A parser-derived answer key would grade a parser against its own mistakes.)

| File | What it is |
|---|---|
| `compare_docs.csv`, `parse_facts.csv` | **v1** (2026-09-26): 5 documents, 28 facts. Used while building and fixing the chunker, so it is partly "seen" data; Docling scores 27/28 on it |
| `page_inventory.csv` | One row per page of all 228 downloaded PDFs (12,980 pages): text length, numbers, image cover, keyword flags. Built by `tools/golden/inventory.py` |
| `v2_candidates.csv` | 70 pages drawn by a seeded, stratified sample from documents **not** in v1 |
| `v2_facts.csv` | **v2** (2026-10-02): 150 facts from 61 of those pages |
| `v2_skipped.csv` | 9 sampled pages with no usable fact, with reasons. 8 are image-only decorative slides/photos — kept as **hallucination checks** (a parser should output ~nothing for them) |
| `v3_pages.csv`, `v3_facts.csv`, `v3_skipped.csv` | **v3** (2026-10-05): the **hard** set — 123 facts from 26 pages of 21 documents (charts, image-only pages, rotated and two-level tables, dense notes) + 3 decorative hallucination-check slides. Built by `tools/golden/v3_candidates.py` |

## v2 at a glance

| | |
|---|---|
| Facts | 150 (100 table, 27 prose, 20 question/answer, 3 chart labels) |
| Pages / documents / companies | 61 / 45 / 5 (APAR 74 facts, Hero 50, E2E 16, C2C 6, Esconet 4) |
| Overlap with v1 | None (v1 documents excluded) |
| Image-only pages (no text layer) | 10 facts on 4 pages — scanned Form A pages, scanned cover letter, white-on-blue image text |
| Hard cases deliberately included | two-level/grouped table headers (11 facts tagged `TWO-LEVEL HEADER`), rotated table, two-page spreads with 4–6 small tables, period only in the table title, repeated row labels across sections, row labels that are dates or numeric ranges, negative values in parentheses or with minus, Indian vs Western digit grouping, values printed without commas among comma'd neighbours, footnote markers on values, letter-spaced fonts, chart data labels, three-column prose, side-by-side tables, Q&A split across speakers, **a PDF whose embedded OCR text layer is wrong** (8 facts) |

### Strata (how pages were sampled)
`tools/golden/inventory.py`, seed `20261002`, at most 2 pages per document per stratum:

| Stratum | Picked | Facts | Pool it was drawn from |
|---|---|---|---|
| `digital_statement` | 12 | 28 | text layer + statement keywords |
| `low_text_numeric` | 12 | 10 | < 50 chars of text and an image covering > 50% of the page |
| `results_columns` | 8 | 27 | results/period keywords and ≥ 40 numbers |
| `segment_or_continued` | 8 | 24 | segment or "(contd.)" pages with ≥ 30 numbers |
| `slide_numbers` | 10 | 20 | presentation pages with ≥ 8 numbers |
| `concall_qa` | 10 | 22 | transcript pages with a "?" |
| `prose_footnote` | 10 | 19 | annual-report prose pages with footnote markers |

Keyword strata are imperfect: some "statement" pages turned out to be auditor-report or policy prose, and 8 of 12 low-text pages were decorative. Facts were taken from whatever the page actually contains; the stratum records why the page was drawn, not what's on it.

## v3 at a glance (the hard set)

| | |
|---|---|
| Facts | 123: 69 table, 30 prose, 20 `chart_point` (chart category → value), 4 `kv` (two-column key/value table) |
| Pages / documents / companies | 26 / 21 / 5 (APAR 64, E2E 27, Hero 24, Esconet 5, C2C 3) |
| Overlap | None with v1/v2 documents, nor with the 3 documents shown in the parser side-by-side review (no parser output was looked at for these pages) |
| Image-only pages | 27 facts on 8 pages: scanned exchange letters, a scanned Form A with signatures across names, text only inside pictures (white on blue, tight letter spacing), a low-resolution raster bar chart |
| Hard cases | bar/line/donut charts with values only as data labels (series matched by legend colour; combined bar+line; white on dark blue), 10 facts on **rotated** tables, 20 **two-level** headers (incl. three plants × Current/Previous year), identically named columns, repeated row labels across sections, chart+table "decade at a glance" blocks whose metric name is only in the block title, stacked rows inside one cell, ranges as values, Indian vs Western grouping of the same figure in consecutive years, values printed without commas, printed inconsistencies kept as printed |

**How pages were chosen:** `tools/golden/v3_candidates.py` (seed `20261005`) draws 20 random pages from each of five hard pools (`scan_doc`, `scan_slide`, `slide_numbers`, `dense_table`, `continued_segment`; at most 2 pages per document per pool) and renders them as labelled thumbnail sheets; the hard pages were then **picked by eye** (purposive). Values were read off 130–400 dpi renders (rotated pages rotated first), never from a parser.

**Verification:** 93 of 96 facts on pages with a text layer match it; the 3 others are text-layer quirks where the fact follows the image (ligatures "ﬁ" in "beneﬁts"/"Proﬁt"; two chart labels glued into "3.453.50*"). 27 facts on image-only pages were checked by eye only.

**Scoring additions (`compare_parsers.py`):** `chart_point` and `kv` are scored like a table row (label and value on one line, then context and unit in the chunk), and reaching L3 is full credit since there is no column to check. Where a column name repeats (two "% Change" columns, "High Price" under BSE and NSE) the fact uses a column whose name is unique, or the first of the repeats.

## Columns (`v2_facts.csv`, `v3_facts.csv`)
`id, stratum, path, page, kind, label, value, context, unit, note` — same meaning as v1 (`compare_parsers.py` docs), but documents are identified by `path` instead of a v1 doc key. `kind`: `table`, `prose`, `qa`, `chart`. `context` is the column header text that identifies the value's column (empty for prose/qa/chart). `page` is the 1-based PDF page.

## Verification
- Each value was read at high zoom from the rendered image.
- Where the page has a text layer, label and value were cross-checked against it to catch transcription typos: 137 of 140 matched; the 3 mismatches are the PDF with a broken OCR text layer, where the image (and the fact) are right.
- 10 facts on image-only pages could only be checked by eye.

## Adding facts
Render the page (`page.get_pixmap(dpi=150–220)`), read it, append rows, keep IDs unique, re-run the text-layer check. Never use a parser's output to decide a value.

## Status
The scorer (`src/cap_slice/compare_parsers.py`) currently reads v1 only. Wiring v2 in (documents by path) is part of the GPU-run preparation.
