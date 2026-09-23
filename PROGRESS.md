# PROGRESS.md

Living status for `cap-slice`. Update at the end of every session. Stable rules and facts are in [`AGENTS.md`](AGENTS.md).

**Last updated:** 2026-09-23

## Current status

**Phase:** sourcing research with a working matrix-URL downloader. All 259 catalogued URLs were attempted: 228 downloaded and 31 failed; eight additional rows are gap placeholders. Independent content verification found a misclassified C2C filing and two additional APAR sources. Download success is not validated historical coverage. Discovery/crawler infrastructure remains undecided.

## Done

- **2026-09-21** — Tested direct NSE access: homepage loads, `/api/*` blocked by Akamai even with cookies/headers. BSE main site and company IR pages also 403.
- **2026-09-21** — Found the open archive layer (`nsearchives.nseindia.com`, `archives.nseindia.com`, `bseindia.com/xml-data/corpfiling`); confirmed direct PDF fetch across all 5 companies.
- **2026-09-21** — Built `data/document_availability_matrix.csv`: 267 catalog entries (APAR 121, Hero 66, E2E 58, Esconet 14, C2C 8). 17 URLs verified `200`, 224 `untested`, 18 `blocked`, 8 `not found`.
- **2026-09-21** — Wrote `docs/document-sourcing-report.md` (sources, workarounds, ToS/subscription, scaling issues, open questions).
- **2026-09-23** — Added `AGENTS.md` and this file for hand-offs.
- **2026-09-23** — Wrote `src/cap_slice/downloader.py` (`uv run cap-slice-download`) and created `data/<SYMBOL>/<doc_type>s/` folders. Full run: **228 downloaded** (761 MB), **31 failed** — 18 × 403 (Hero company site), 11 × 404, 2 × HTML page instead of PDF. Matrix `fetch_status` updated from real fetches; added `download_status` column (yes 228 / no 39). Latest retained outcome per URL in `data/download_manifest.csv`.
- **2026-09-23** — Found ZIP delivery for sampled NSE annual reports through FY2022-23 (recorded in `AGENTS.md`). Downloader now unpacks them; the 7 existing ZIPs were converted, so every downloaded document is now a PDF.

- **2026-09-23** — Independently tested 24 URLs across all five issuers: 17 PDFs, one ZIP, three HTML responses and three 403s. Parsed all 18 downloaded documents and spot-checked contents. Found C2C's results candidate is an allotment disclosure; verified APAR results/shareholding documents and corrected historical listing guidance. The checks and two proposed additions are documented in [`docs/pilot-verification-2026-09-23.md`](docs/pilot-verification-2026-09-23.md) alongside terms, feed pricing and scaling findings.
- **2026-09-23** — Reconciled verification work with main's downloader commits during rebase. Preserved the downloader, matrix and manifest; replaced superseded verification-gap notes with full-run outcomes and retained semantic-validation gaps. Downloader work was committed in `dee24b8`.

- **2026-09-23** — Limited this branch’s commit to the four reconciled Markdown files as requested; raw pilot artifacts retained outside the repository.

## Open gaps

| Gap | Affects | Status |
|---|---|---|
| Full shareholding history | All 5 companies | APAR December 2018 issuer-hosted Reg-31 report verified; remaining coverage unresolved |
| Periodic-results coverage and classification | All 5 companies | APAR Q4/FY25 found; C2C H1 FY26 candidate is an allotment disclosure and must be excluded from results coverage |
| Content validation | 228 downloaded candidates | HTTP/file-signature checks complete for successful downloads; independent sample is not a full semantic audit |
| Hero company-hosted transcripts | 18 catalogued URLs | All returned 403 in the full downloader run; independent sample also found a blocked shareholding URL |
| 13 other failed catalogued URLs | APAR: AR FY2022-23; presentations Feb 2023 (d), Aug 2022 (b), Aug 2021, Nov 2018 (a)/(b), Jan 2018; concalls Feb 2018, Mar 2017, Jun 2016. Hero: concall Jul 2023; presentations Sep 2018, Aug 2018 | 11 returned 404; two returned HTML. Need alternative/correct URLs; failure alone does not establish the cause |
| Catalog reconciliation | Two new APAR documents and historical tier metadata | Additions remain separate; E2E became mainboard in April 2022 and C2C listed in December 2024 |

## Open questions (for discussion)

1. Which authorized discovery sources should support historical collection: company IR, exchange feeds, or an aggregator with agreed rights?
2. Are issuer-hosted filing copies and structured exchange formats acceptable, or must documents be exchange-hosted PDFs?
3. What licensed product covers historical backfill, original attachments, SME issuers and the intended downstream use? The old 150k–250k estimate needs revision using company/type/period coverage.
4. How should content classification, historical tier changes and completeness be validated before expanding the pilot?

## Next steps

1. Reconcile C2C's misclassified filing and the two APAR additions with the catalog; audit a bounded set of company/type/period combinations.
2. Re-discover alternatives for the 13 failed URLs and determine an authorized route for blocked Hero documents.
3. Confirm bulk-use rights and historical attachment coverage before choosing discovery infrastructure.

## Decision log

| Date | Decision | Why |
|---|---|---|
| 2026-09-21 | Personal research, low volume only | NSE ToS prohibits automated scraping; bulk/commercial needs the paid route |
| 2026-09-21 | No crawler yet — build an availability matrix first | Understand sources and failure modes before investing in infrastructure |
| 2026-09-21 | Don't use Screener as the source of record — record the underlying NSE/BSE archive URL | Goal is to understand primary sources, not depend on an aggregator |
| 2026-09-21 | Periodic results follow the listing tier: quarterly for mainboard, half-yearly for SME | That's what each tier actually files |
| 2026-09-23 | Build a downloader for matrix URLs only (no discovery) | User wants the pilot documents on disk; stays within low-volume, sequential, throttled rules |
| 2026-09-23 | Folders keyed by NSE symbol: `data/<SYMBOL>/<doc_type>s/`; downloads gitignored | Preserves the existing folder convention; historical symbol/tier aliases need separate metadata; binaries stay outside git |
| 2026-09-23 | Unpack single-PDF ZIPs, keep only the PDF | One consistent format for later parsing; the ZIP adds nothing |
| 2026-09-23 | Split stable guidance (`AGENTS.md`) from living status (`PROGRESS.md`) | Keeps rules readable; progress can grow without burying them |
| 2026-09-23 | Document dated semantic-verification findings alongside the downloader manifest | Full retrieval results supersede sampling gaps, while content checks can reject successfully downloaded candidates |
| 2026-09-23 | Reconcile shared guidance against main during concurrent agent work | Preserve complementary findings and remove stale or duplicated status without overwriting another worktree |
