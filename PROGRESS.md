# PROGRESS.md

Living status for `cap-slice`. Update at the end of every session. Stable rules and facts are in [`AGENTS.md`](AGENTS.md).

**Last updated:** 2026-09-23

## Current status

**Phase:** research complete for the 5-company pilot; all findable documents downloaded (228 of 267). **Awaiting discussion** of the open questions below before any discovery/crawler build work.

## Done

- **2026-09-21** — Tested direct NSE access: homepage loads, `/api/*` blocked by Akamai even with cookies/headers. BSE main site and company IR pages also 403.
- **2026-09-21** — Found the open archive layer (`nsearchives.nseindia.com`, `archives.nseindia.com`, `bseindia.com/xml-data/corpfiling`); confirmed direct PDF fetch across all 5 companies.
- **2026-09-21** — Built `data/document_availability_matrix.csv`: 267 documents (APAR 121, Hero 66, E2E 58, Esconet 14, C2C 8). 17 URLs verified `200`, 224 `untested`, 18 `blocked`, 8 `not found`.
- **2026-09-21** — Wrote `docs/document-sourcing-report.md` (sources, workarounds, ToS/subscription, scaling issues, open questions).
- **2026-09-23** — Added `AGENTS.md` and this file for hand-offs.
- **2026-09-23** — Wrote `src/cap_slice/downloader.py` (`uv run cap-slice-download`) and created `data/<SYMBOL>/<doc_type>s/` folders. Full run: **228 downloaded** (761 MB), **31 failed** — 18 × 403 (Hero company site), 11 × 404, 2 × HTML page instead of PDF. Matrix `fetch_status` updated from real fetches; added `download_status` column (yes 228 / no 39). Per-attempt log in `data/download_manifest.csv`.
- **2026-09-23** — Found that NSE serves annual reports up to FY2022-23 as ZIPs (recorded in `AGENTS.md`). Downloader now unpacks them; the 7 existing ZIPs were converted, so every downloaded document is now a PDF.

## Open gaps

| Gap | Affects | Status |
|---|---|---|
| Official filed shareholding-pattern PDF not discoverable | All 5 companies | Open — only derived % from Screener |
| Periodic-results PDF not isolated | APAR, Hero MotoCorp (and E2E partially) | Open |
| ~~224 of 267 URLs not individually verified~~ | Matrix | Closed 2026-09-23 — every URL now fetched by the downloader |
| Hero MotoCorp pre-2022 concalls on company site | 18 rows | `blocked` (403) — confirmed again by downloader |
| 13 matrix URLs were wrong (11 × 404, 2 × HTML page) | APAR: AR FY2022-23; presentations Feb 2023 (d), Aug 2022 (b), Aug 2021, Nov 2018 (a)/(b), Jan 2018; concalls Feb 2018, Mar 2017, Jun 2016. Hero: concall Jul 2023; presentations Sep 2018, Aug 2018 | Open — need re-discovery of the correct URLs |

## Open questions (for discussion)

1. Keep Screener.in as the discovery dependency, or build a primary-source discovery path (e.g. browser automation against NSE/BSE filing search)?
2. Accept "derived data only" for shareholding pattern, or find a dedicated discovery path?
3. At what volume does NSE Data & Analytics' paid route make more sense than the workaround? (3–4k companies × 10 years ≈ 150k–250k docs.)
4. How to discover periodic results for large mainboard companies, given pattern-matching didn't isolate them?

## Next steps

1. Discuss the open questions above.
2. Re-discover the 13 wrong URLs (see Open gaps).
3. ~~Commit the downloader, matrix update, and docs~~ — done 2026-09-23 (`dee24b8`).

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
| 2026-09-23 | Split stable guidance (`AGENTS.md`) from living status (`PROGRESS.md`) | Keeps rules readable; progress can grow without burying them |
