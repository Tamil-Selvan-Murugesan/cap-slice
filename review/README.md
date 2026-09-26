# Parser comparison — Options 1 & 2 vs the current pipeline

Run on 2026-09-26 with `uv run cap-slice-compare`. Docling (Option 3) is not run yet (disk space).
Scores are regenerated in [`COMPARISON.md`](COMPARISON.md); this page is the written verdict.

| Folder | What it is |
|---|---|
| `baseline/` | Current pipeline: `extract.py` + `chunk.py` (500 words, whitespace flattened) |
| `pymupdf_text/` | **Option 1**: PyMuPDF text, line-preserving, column gaps → `|` cells, + structured chunker |
| `pymupdf4llm/` | **Option 2**: PyMuPDF4LLM layout mode → Markdown, RapidOCR for image pages, + structured chunker |

Each `<option>/<doc>/` has `parsed.md` (raw parser output per page, **before** chunking) and `chunks.md` (exactly what would be embedded). Options 1 and 2 share the same chunker (`src/cap_slice/structured_chunk.py`), so differences between them come from the parser.

## Verdict

**Option 2 (PyMuPDF4LLM) is the best of the three, but not good enough on scanned pages.**

| Facts (28, read off page images) | Baseline | Option 1 | Option 2 |
|---|---|---|---|
| Value present on the fact's page (≥ L1) | 20 | 20 | **26** |
| Row intact, label next to value (≥ L2) | 20 | 18 | **23** |
| + year header and unit in the same chunk (≥ L3) | 19 | 17 | **21** |
| + value under the right column (L4) | 4 | 15 | **21** |

| Speed on this laptop (CPU) | Baseline | Option 1 | Option 2 |
|---|---|---|---|
| 148-page digital annual report | 5 s | 6 s | 183 s |
| 164-page report with 42 scanned pages | 6 s | 6 s | **945 s** |
| All 5 docs (375 pages) | ~13 s | ~14 s | ~21 min |

Tokens to embed are about the same or lower for Options 1 and 2 (boilerplate removed), so embedding cost does not rise.

## Where each option improved — and where it didn't

**1. Digital financial tables (E2E FY2024-25, facts F01–F08)**
- Baseline: rows run together; year headers somewhere in the chunk (L3) but no way to tell which column a number is in. Chunk 139 also mixes the auditor's sign-off with the balance sheet.
- Option 1: 7/8 at L4 — after one fix (sub-heading lines like "Current assets" had split the statement into header-less pieces). See `pymupdf_text/e2e_ar_fy25/chunks.md` chunk 221.
- Option 2: **8/8 at L4**, clean Markdown tables with the header row. `pymupdf4llm/e2e_ar_fy25/chunks.md` chunks 278 and 281.

**2. Scanned financial statements (E2E FY2022-23, F09–F14) — nobody passes**
- Baseline and Option 1: no OCR, pages 123–164 are simply missing (0/6).
- Option 2: OCR recovers text on all 52 image pages, but only 4/6 values are found on the scanned pages and none at L3+: RapidOCR drops spaces (`BalanceSheetasatMarch31,2023`), reads some commas as dots (`6.840.73`), and **puts both year columns in one cell** (`1,631.31 384.34`), so the year of each number is lost. Raising OCR resolution to 300 dpi did not fix it. See `pymupdf4llm/e2e_ar_fy23/parsed.md`, page 123.
- This is the case Docling's table model is supposed to handle — the main reason to still test Option 3.

**3. Concall transcript (C2C, F15–F18)**
- All three keep each question with its answer (4/4). The gain from Options 1/2 is cleanliness: the 5-line letterhead (address, PAN, GST) repeated on every page is removed → 20.8K tokens vs 26.9K baseline (−23%) and no letterhead noise in every chunk.
- Option 1 initially broke this document (two-column layout turned into fake tables); fixed by only treating lines with numbers as table rows.

**4. Presentation with image-only slides (E2E May 2024, F19–F24)**
- Table slide: Options 1 and 2 both 4/4 at L4 (baseline L3).
- Image-only slide 5 (leadership bios): only Option 2 has it (OCR) — 2/2. Baseline and Option 1: 0/2.

**5. Table continuing across pages (C2C allotment, F25–F28)**
- Option 2: rows on page 2 keep the header from page 1 (merged by the chunker) → F26, F27 at L4.
- Option 1: its text-based "table" is too broken (multi-line header cells, wrapped names) → L1–L3.
- **Both** fail F25: the name "Pravan Holdings / LLP" wraps in its cell and both parsers split it into two rows, so the amount sits on the row labelled "LLP". The baseline scores higher here only because flattening everything happened to rejoin the name.

## Issues found along the way (all fixed and re-run)
- Letterhead removal missed variants joined differently per page → fragment-based matching at page edges.
- That rule then deleted a real table row at the bottom of page 1 → table rows are never boilerplate.
- Tiny chunks (4–15 words) from designed pages → tables under 3 rows count as text; prose under 80 words merges forward.
- PyMuPDF4LLM wraps unsure OCR characters in `~~` (e.g. `2,294~~.~~41`) → stripped in cleaning.
- A heading arriving while a chunk was small lost its text; the small-chunk merge also dropped the next chunk's heading → both fixed (fact F24).

## How facts are matched to chunks

- Only chunks from the fact's own document **whose page range covers the fact's page** are tested (default since 2026-09-26; `score_fact(..., any_page=True)` turns it off).
- Every such chunk is tested; the fact scores the **best level any single chunk reaches**. Evidence is never combined across chunks. Ties keep the earliest chunk, which is the one tagged `golden facts: Fxx (Ln)` in `chunks.md`.
- This assumes **perfect retrieval**: a score is the ceiling of what the best chunk allows, not what search will return. Duplicate or garbled copies of a value elsewhere are not penalised. Search quality needs the next, embedding-based evaluation.
- Why the page rule: without it F13 (profit 990.99, scanned P&L on p. 124) scored L1 in every option only because the directors' report on another page quotes the same number. With it, F13 is 0 everywhere; no other score changed.

## Caveats
- 28 facts across 5 documents is a small sample; it measures whether information *survives* parsing and chunking, not search quality (that needs embeddings + a question set).
- Scoring is string-based: an OCR misread counts as missing, which is correct for exact numbers.
- The C2C "H1 FY2025-26 results" file is actually a share-allotment notice — a catalogue error, logged in `PROGRESS.md`.
