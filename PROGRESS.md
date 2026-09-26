# PROGRESS.md

Living status for `cap-slice`. Update at the end of every session. Stable rules and facts are in [`AGENTS.md`](AGENTS.md).

**Last updated:** 2026-09-26

## Current status

**Phase:** five-company acquisition and indexing prototype. All 259 catalogued URLs were attempted; 228 PDFs are present and hash-verified, but coverage and document classification remain incomplete. The indexing pipeline is uncommitted; its full local dry run and temporary Qdrant checks passed on 2026-09-26. No live embeddings or retrieval-quality evaluation are established. See the validation review below before paid indexing or discovery/crawler build work.

## Done

- **2026-09-21** — Tested direct NSE access: homepage loads, `/api/*` blocked by Akamai even with cookies/headers. BSE main site and company IR pages also 403.
- **2026-09-21** — Found the open archive layer (`nsearchives.nseindia.com`, `archives.nseindia.com`, `bseindia.com/xml-data/corpfiling`); confirmed direct PDF fetch across all 5 companies.
- **2026-09-21** — Built `data/document_availability_matrix.csv`: 267 documents (APAR 121, Hero 66, E2E 58, Esconet 14, C2C 8). 17 URLs verified `200`, 224 `untested`, 18 `blocked`, 8 `not found`.
- **2026-09-21** — Wrote `docs/document-sourcing-report.md` (sources, workarounds, ToS/subscription, scaling issues, open questions).
- **2026-09-23** — Added `AGENTS.md` and this file for hand-offs.
- **2026-09-23** — Wrote `src/cap_slice/downloader.py` (`uv run cap-slice-download`) and created `data/<SYMBOL>/<doc_type>s/` folders. Full run: **228 downloaded** (761 MB), **31 failed** — 18 × 403 (Hero company site), 11 × 404, 2 × HTML page instead of PDF. Matrix `fetch_status` updated from real fetches; added `download_status` column (yes 228 / no 39). Per-attempt log in `data/download_manifest.csv`.
- **2026-09-23** — Found that NSE serves annual reports up to FY2022-23 as ZIPs (recorded in `AGENTS.md`). Downloader now unpacks them; the 7 existing ZIPs were converted, so every downloaded document is now a PDF.
- **2026-09-23** — Wrote the indexing pipeline (`extract.py`, `chunk.py`, `embed.py`, `vectorstore.py`, `index.py`; CLIs `cap-slice-index`, `cap-slice-search`). Dry run over all 228 PDFs: 12,980 pages, **13,441 chunks = 11.0M tokens** (exact count with Voyage's tokenizer; annual reports 8.4M), no extraction failures, no document mostly scanned. Qdrant store tested locally with dummy vectors (insert, skip-if-indexed, replace-on-change, filtered search). Fixed: a run interrupted mid-upsert would have left a partial document marked as done — now `has_doc` checks stored count against `n_chunks`.

- **2026-09-26** — Validated the repo end to end. Matrix (267 rows), files on disk (228 PDFs, all start `%PDF`, no orphans), `download_status` and manifest sha256s all agree. Pipeline compiles, dry run and Qdrant checks pass. Fixed: (a) embedding batches were a fixed 64 chunks — worst case ~166K tokens, over Voyage's 120K cap — now sized by token count (≤100K); (b) the 2 URLs that returned HTML were left `untested` — now `not found`, and the downloader records such responses that way. Matrix `fetch_status` is now 228 `200` / 21 `not found` / 18 `blocked`.

## Open gaps

| Gap | Affects | Status |
|---|---|---|
| Official filed shareholding-pattern PDF not discoverable | All 5 companies | Open — only derived % from Screener |
| Periodic-results PDF not isolated | APAR, Hero MotoCorp (and E2E partially) | Open |
| ~~224 of 267 URLs not individually verified~~ | Matrix | Closed 2026-09-23 — every URL now fetched by the downloader |
| **Tables are flattened.** `chunk.py` joins all whitespace, so balance-sheet rows run together, numbers lose their column headers (which year) and units, and chunks straddle pages/sections (e.g. E2E FY2024-25 chunk 139 = auditor sign-off + balance sheet). PyMuPDF `find_tables()` out of the box also failed on that page (whole table merged into one cell) | All financial tables — mostly annual reports and results | Open — fix before paying to embed; evaluate a layout-aware parser (e.g. Docling) |
| 441 of 12,980 pages (3.4%) have no text layer — 273 mostly covered by one image, 118 small images only, 42 blank, 8 text-as-vector-outlines; includes E2E AR FY2022-23 pp. 123–164 (likely financial statements) | Search won't find that content | Open — needs OCR |
| Hero MotoCorp pre-2022 concalls on company site | 18 rows | `blocked` (403) — confirmed again by downloader |
| 13 matrix URLs were wrong (11 × 404, 2 × HTML page) | APAR: AR FY2022-23; presentations Feb 2023 (d), Aug 2022 (b), Aug 2021, Nov 2018 (a)/(b), Jan 2018; concalls Feb 2018, Mar 2017, Jun 2016. Hero: concall Jul 2023; presentations Sep 2018, Aug 2018 | Open — need re-discovery of the correct URLs |

## Open questions (for discussion)

1. Keep Screener.in as the discovery dependency, or build a primary-source discovery path (e.g. browser automation against NSE/BSE filing search)?
2. Accept "derived data only" for shareholding pattern, or find a dedicated discovery path?
3. At what volume does NSE Data & Analytics' paid route make more sense than the workaround? (3–4k companies × 10 years ≈ 150k–250k docs.)
4. How to discover periodic results for large mainboard companies, given pattern-matching didn't isolate them?

## Next steps

1. Fix table/structure handling (see Open gaps), then run `cap-slice-index` with a Voyage API key (start with `--symbol C2C` to check cost/quality), then try `cap-slice-search`.
2. Decide on OCR for text-less pages (see Open gaps).
3. Discuss the open questions above.
4. Re-discover the 13 wrong URLs (see Open gaps).
5. ~~Commit the downloader, matrix update, and docs~~ — done 2026-09-23 (`dee24b8`).

## Decision log

| Date | Decision | Why |
|---|---|---|
| 2026-09-21 | Personal research, low volume only | NSE ToS prohibits automated scraping; bulk/commercial needs the paid route |
| 2026-09-21 | No crawler yet — build an availability matrix first | Understand sources and failure modes before investing in infrastructure |
| 2026-09-21 | Don't use Screener as the source of record — record the underlying NSE/BSE archive URL | Goal is to understand primary sources, not depend on an aggregator |
| 2026-09-21 | Periodic results follow the listing tier: quarterly for mainboard, half-yearly for SME | That's what each tier actually files |
| 2026-09-23 | Build a downloader for matrix URLs only (no discovery) | User wants the pilot documents on disk; stays within low-volume, sequential, throttled rules |
| 2026-09-23 | Folders keyed by NSE symbol: `data/<SYMBOL>/<doc_type>s/`; downloads gitignored | Symbol is unique and stable; 761 MB of binaries don't belong in git |
| 2026-09-23 | Unpack single-PDF ZIPs, keep only the PDF | One consistent format for later parsing; the ZIP adds nothing |
| 2026-09-23 | Embeddings: Voyage `voyage-finance-2`; vector DB: Qdrant (local mode first) | User's choice; finance-tuned model, and Qdrant's local mode uses the same client code as a server later |
| 2026-09-23 | Split stable guidance (`AGENTS.md`) from living status (`PROGRESS.md`) | Keeps rules readable; progress can grow without burying them |


## Validation review — 2026-09-26

This review checks the current working tree, including the other agent's uncommitted indexing pipeline. The earlier reconciled verification report remains on `tamil/codex-pilot-verification` (`a6ca47b`) and has not been integrated into main. Preserve the indexing work when reconciling those documentation changes.

**Verified locally:** all 228 downloaded files exist, begin with PDF signatures, and match the SHA-256 values in `data/download_manifest.csv`. They total 799,182,012 bytes and 12,980 PDF pages. The catalog has 267 rows: 259 URLs and eight gap placeholders. The recorded downloader outcomes are 228 successes, 18 HTTP 403s, 11 HTTP 404s, and two HTTP 200 responses containing HTML. These are historical network results; this review did not re-fetch exchange URLs.

**Coverage is still incomplete:** downloaded labels comprise 43 annual reports, four periodic-results candidates, 86 transcripts and 95 presentations; no shareholding reports are in the current downloaded catalog. 198 downloaded rows have no filing date. These counts describe catalog labels, not content-validated coverage.

**Reconfirmed content corrections:** C2C's four-page H1 FY2025–26 results candidate is an equity/warrant allotment disclosure and should not enter a financial-results index under that label. C2C's FY2024–25 annual report dates listing to December 3, 2024; E2E's FY2022–23 annual report dates mainboard trading to April 12, 2022. Main's guidance still needs those historical corrections. The earlier pilot also found issuer-hosted APAR results and shareholding reports; those sources have not been incorporated into this catalog or re-fetched in this review.

**Fresh full dry run:** all 228 PDFs completed extraction/chunking with zero failures and no whole-document OCR skips: 12,980 pages, 13,441 chunks, and 441 low-text pages omitted (3.4%). This independently reproduces the previously recorded chunk/page totals, but does not establish correct table interpretation or complete page coverage. No embeddings were generated.

**Indexing validation:** local Qdrant tests with temporary dummy vectors passed partial-document detection, complete-document detection, hash-change detection, replacement, and symbol-filtered search. There is no `data/qdrant/` store in this checkout. No live embedding/search API calls were made; actual retrieval quality and paid indexing remain unvalidated. The earlier 11.0M-token count has not been independently recounted in this review.

**Extraction issues reproduced:** E2E FY2022–23 PDF pages 123–164 are all omitted by the current extraction threshold (52 of 164 pages omitted overall), but the document is not rejected by the majority-page OCR rule. E2E FY2024–25 chunk 139 spans PDF pages 106–108 and combines auditor text with flattened balance-sheet content. Pages below 50 characters should be described as low-text/omitted, not automatically classified as scans or proven to lack a text layer.

**Additional code limitations:** document skipping keys on file hash and stored chunk count, not parser/chunker version, metadata or embedding model. A parser or metadata correction therefore requires deliberate reindexing; model compatibility is documented but not enforced against an existing collection. A focused chunking check also showed that `chunk_words=100` still produced one 250-word chunk because paragraph splitting uses the module-level size.

**Recommended order:** (1) reconcile the two agents' documentation and correct catalog labels/history; (2) preserve financial-table headers, units and section boundaries and recover relevant omitted pages with OCR; (3) add regression checks and version-aware indexing; (4) evaluate a small, approved embedding run against representative questions with known source pages; (5) commit the reviewed pipeline, expand validated coverage, and confirm source/access rights before bulk discovery. The existing research-stage restriction on crawler development remains in force.

No implementation changes, commits, paid calls or new research artifacts were made by this validation review; its only repository edit is this progress update.
