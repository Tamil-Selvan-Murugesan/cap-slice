# Parser comparison — Options 1, 2 & 3 vs the current pipeline

Options 1–2 run on 2026-09-26, Docling (Option 3) on 2026-09-28, all with `uv run cap-slice-compare`; all options re-scored on 2026-09-28 with the same chunker version.
Scores and latency are regenerated in [`COMPARISON.md`](COMPARISON.md); this page is the written verdict. Bugs found along the way: [`../bugs_resolved.md`](../bugs_resolved.md).

| Folder | What it is |
|---|---|
| `baseline/` | Current pipeline: `extract.py` + `chunk.py` (500 words, whitespace flattened) |
| `pymupdf_text/` | **Option 1**: PyMuPDF text, line-preserving, column gaps → `\|` cells by our own rules, + structured chunker |
| `pymupdf4llm/` | **Option 2**: PyMuPDF4LLM layout mode → Markdown, RapidOCR for image pages, + structured chunker |
| `docling/` | **Option 3**: Docling (layout model + TableFormer ACCURATE + RapidOCR, CPU PyTorch, default settings) → Markdown, + structured chunker |

Each `<option>/<doc>/` has `parsed.md` (raw parser output per page, **before** chunking), `chunks.md` (exactly what would be embedded) and `parsed.json` (parse cache with the measured parse time). Options 1–3 share the same chunker (`src/cap_slice/structured_chunk.py`), so differences between them come from the parser. The baseline uses the old `chunk.py` and is the "before" reference.

## Verdict

**Docling (Option 3) is the most accurate by a clear margin — 27/28 facts under the right column — but it is ~4.5x slower than PyMuPDF4LLM and ~750x slower than plain PyMuPDF on this laptop.** It is the only option that reads scanned financial tables with their years intact. Use it selectively (see "What this means").

| Facts (28, read off page images) | Baseline | Option 1 | Option 2 | **Option 3 Docling** |
|---|---|---|---|---|
| Value present on the fact's page (≥ L1) | 20 | 20 | 26 | **27** |
| Row intact, label next to value (≥ L2) | 20 | 18 | 23 | **27** |
| + year header and unit in the same chunk (≥ L3) | 19 | 17 | 21 | **27** |
| + value under the right column (L4) | 4 | 15 | 21 | **27** |

## Latency (parsing only; this laptop: Core Ultra 5 135U, 14 logical CPUs, CPU only)

| Document | Pages | Baseline | Option 1 | Option 2 | **Docling** |
|---|---|---|---|---|---|
| E2E FY2024-25 annual report (digital) | 148 | 2.1 s | 2.6 s | 183 s | 1,747 s |
| E2E FY2022-23 (52 low-text pages, scanned statements) | 164 | 3.0 s | 3.8 s | 945 s | 2,824 s |
| C2C concall | 31 | 0.5 s | 0.7 s | 27 s | 390 s |
| E2E presentation (9 image-only slides) | 28 | 0.1 s | 0.1 s | 93 s | 679 s |
| C2C allotment notice | 4 | 0.0 s | 0.0 s | 3 s | 60 s |
| **Total, 375 pages** | | **6 s (0.02 s/page)** | **7 s (0.02 s/page)** | **21 min (3.3 s/page)** | **95 min (15.2 s/page)** |
| Projected, all 12,980 pages | | 3 min | 4 min | ~12 h | **~55 h** |
| Peak process memory | | 193 MB | 193 MB | not measured | **6.1 GB** (+4.7 GB while parsing) |

How to read these:
- **Parse time only** — chunking (≤ 0.2 s per document) and token counting are excluded.
- **Single runs**, not averages. This laptop's timings vary noticeably between runs (the same Docling setting measured 66 s and 104 s on the small C2C doc), so treat differences under ~1.5x as noise.
- Option 2's times are from its 2026-09-26 run (cached); memory wasn't measured then. Re-parsing it now would use a different OCR engine version (`bugs_resolved.md` P6).
- Docling's first document includes its one-off model load (~11 s).
- Projections are **pessimistic for OCR-heavy options**: the golden docs are 17% low-text pages vs 3.4% across the collection.
- A GPU would speed Options 2 and 3 up substantially (their time is almost all neural-network work: layout, table structure, OCR — OCR alone was ~2/3 of Docling's time on the small C2C doc). Not measured here.

Tokens to embed are about the same or lower for Options 1–3 than the baseline (boilerplate removed), so embedding cost does not rise.

## What this means

Docling's accuracy matters most on the pages that are hardest and rarest: scanned statements and complex tables. At ~15 s/page it can't sensibly run on everything on a laptop. The practical design is **routing**: a fast parser (Option 1 or 2) for ordinary pages, Docling only for pages with no text layer (3.4% of the collection) and pages with financial tables — or a rented GPU for a one-off bulk run. This is a proposal to test, not yet measured.

## Where each option improved — and where it didn't

**1. Digital financial tables (E2E FY2024-25, facts F01–F08)**
- Baseline: rows run together; year headers somewhere in the chunk (L3) but no way to tell which column a number is in. Chunk 139 also mixes the auditor's sign-off with the balance sheet.
- Option 1: 7/8 at L4 — after one fix (sub-heading lines like "Current assets" had split the statement into header-less pieces). See `pymupdf_text/e2e_ar_fy25/chunks.md` chunk 221.
- Option 2: 8/8 at L4, clean Markdown tables with the header row. `pymupdf4llm/e2e_ar_fy25/chunks.md` chunks 278 and 281.
- Docling: 8/8 at L4 — its tables are the cleanest (merged header cells handled). It first scored 1/8 because of **our chunker**: Docling places the signature line between the units line and the table, and the caption only took the one block before the table, dropping "INR lakhs" (`bugs_resolved.md` S8, fixed; no other option's scores changed).

**2. Scanned financial statements (E2E FY2022-23, F09–F14) — only Docling passes**
- Baseline and Option 1: no OCR, pages 123–164 are simply missing (0/6).
- Option 2: OCR recovers text on all 52 image pages, but only 4/6 values are found on the scanned pages and none at L3+: RapidOCR drops spaces (`BalanceSheetasatMarch31,2023`) and reads some commas as dots (`6.840.73`); then PyMuPDF4LLM's **table-grid step puts both year columns in one cell** (`1,631.31 384.34`), so the year of each number is lost. (OCR itself read the two values correctly as separate boxes — the merge is a column-detection failure; checked 2026-10-02.) 300 dpi OCR did not fix it. See `pymupdf4llm/e2e_ar_fy23/parsed.md`, page 123.
- **Docling: 5/6 at L4.** Its table model rebuilds the scanned statements as real tables with "As at March 31, 2023 | As at March 31, 2022" columns. See `docling/e2e_ar_fy23/parsed.md` pages 123–124. The one miss, F13, is a genuine OCR error: the double-underlined profit **990.99 was read as `6960969`**. Same OCR engine as Option 2 (RapidOCR) — the difference is Docling's layout and table-structure models deciding *where* cells are before reading them.

**3. Concall transcript (C2C, F15–F18)**
- All four keep each question with its answer (4/4). The gain from Options 1–3 is cleanliness: the 5-line letterhead repeated on every page is removed → 20.5–21.8K tokens vs 26.9K baseline (−19% to −24%).
- Option 1 initially broke this document (two-column layout turned into fake tables); fixed by only treating lines with numbers as table rows.

**4. Presentation with image-only slides (E2E May 2024, F19–F24)**
- Table slide: Options 1–3 all 4/4 at L4 (baseline L3).
- Image-only slide 5 (leadership bios): only the OCR options have it — Options 2 and 3, 2/2 each. Baseline and Option 1: 0/2.

**5. Table continuing across pages (C2C allotment, F25–F28)**
- Options 2 and 3: rows on page 2 keep the header from page 1 (merged by the chunker) → F26, F27 at L4.
- Option 1: its text-based "table" is too broken (multi-line header cells, wrapped names) → L1–L3.
- F25 ("Pravan Holdings / LLP", a name wrapped inside its cell): **only Docling keeps it as one row (L4)**. Options 1 and 2 split it into two rows, so the amount sits on the row labelled "LLP" (L1). The baseline scores L3 only because flattening everything happened to rejoin the name.

## Known issue in the shared chunker (open)
- Since the S8 fix, a table's caption can take up to 60 words of the text before it — which on page 123 of the scanned report pulls in the previous page's auditor sign-off ("Chartered Accountants … UDIN …") ahead of the balance sheet. It doesn't affect scores but adds noise to that chunk. Logged as `bugs_resolved.md` S9.

## How facts are matched to chunks

- Only chunks from the fact's own document **whose page range covers the fact's page** are tested (default since 2026-09-26; `score_fact(..., any_page=True)` turns it off).
- Every such chunk is tested; the fact scores the **best level any single chunk reaches**. Evidence is never combined across chunks. Ties keep the earliest chunk, which is the one tagged `golden facts: Fxx (Ln)` in `chunks.md`.
- This assumes **perfect retrieval**: a score is the ceiling of what the best chunk allows, not what search will return. Search quality needs the next, embedding-based evaluation.
- Why the page rule: without it F13 scored L1 in every option only because the directors' report on another page quotes the same number.

## Caveats
- 28 facts across 5 documents is a small sample; it measures whether information *survives* parsing and chunking, not search quality.
- The same 28 facts guided the chunker fixes and measure the result — some risk of overfitting. Add facts from unseen documents before a final decision.
- Scoring is string-based: an OCR misread counts as missing, which is correct for exact numbers.
- The C2C "H1 FY2025-26 results" file is actually a share-allotment notice — a catalogue error, logged in `PROGRESS.md`.
