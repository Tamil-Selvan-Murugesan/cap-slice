# Golden set

Ground truth for comparing PDF parsers and chunkers. **Every fact is read by a person/agent off a rendered page image — never copied from any parser's output.** (A parser-derived answer key would grade a parser against its own mistakes.)

| File | What it is |
|---|---|
| `compare_docs.csv`, `parse_facts.csv` | **v1** (2026-09-26): 5 documents, 28 facts. Used while building and fixing the chunker, so it is partly "seen" data; Docling scores 27/28 on it |
| `page_inventory.csv` | One row per page of all 228 downloaded PDFs (12,980 pages): text length, numbers, image cover, keyword flags. Built by `tools/golden/inventory.py` |
| `v2_candidates.csv` | 70 pages drawn by a seeded, stratified sample from documents **not** in v1 |
| `v2_facts.csv` | **v2** (2026-10-02): 150 facts from 61 of those pages |
| `v2_skipped.csv` | 9 sampled pages with no usable fact, with reasons. 8 are image-only decorative slides/photos — kept as **hallucination checks** (a parser should output ~nothing for them) |

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

## Columns (`v2_facts.csv`)
`id, stratum, path, page, kind, label, value, context, unit, note` — same meaning as v1 (`compare_parsers.py` docs), but documents are identified by `path` instead of a v1 doc key. `kind`: `table`, `prose`, `qa`, `chart`. `context` is the column header text that identifies the value's column (empty for prose/qa/chart). `page` is the 1-based PDF page.

## Verification
- Each value was read at high zoom from the rendered image.
- Where the page has a text layer, label and value were cross-checked against it to catch transcription typos: 137 of 140 matched; the 3 mismatches are the PDF with a broken OCR text layer, where the image (and the fact) are right.
- 10 facts on image-only pages could only be checked by eye.

## Adding facts
Render the page (`page.get_pixmap(dpi=150–220)`), read it, append rows, keep IDs unique, re-run the text-layer check. Never use a parser's output to decide a value.

## Status
The scorer (`src/cap_slice/compare_parsers.py`) currently reads v1 only. Wiring v2 in (documents by path) is part of the GPU-run preparation.
