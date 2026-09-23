# AGENTS.md

Guidance for any agent (or human) picking up this repo. Stable facts and rules live here; current status lives in [`PROGRESS.md`](PROGRESS.md).

**Start of session:** read this file, then `PROGRESS.md`.
**End of session:** update `PROGRESS.md` (status, what changed, next steps, any decisions with a date and reason). Update this file only if a rule or durable fact changed.

---

## Purpose

`cap-slice` fetches five document types for NSE-listed Indian companies:

1. Annual reports
2. Periodic results — quarterly (mainboard) or half-yearly (NSE SME)
3. Shareholding patterns
4. Concall transcripts
5. Investor presentations

Target: roughly 2015–2026 (or from listing date if later), eventually for ~3,000–4,000 companies.

**Current phase: research, not building.** We are mapping data sources, workarounds, ToS/subscription constraints, and scaling issues on a 5-company pilot before writing any fetcher. Don't start building crawler infrastructure unless `PROGRESS.md` says that decision has been made.

## Repo layout

| Path | What it is |
|---|---|
| `data/document_availability_matrix.csv` | Pilot catalog: one row per document, 5 companies |
| `docs/document-sourcing-report.md` | Findings report: sources, workarounds, ToS, scaling issues, open questions |
| `src/cap_slice/` | Python package (still the `uv init` stub — no fetcher code yet) |
| `PROGRESS.md` | Living status + decision log |

Tooling: Python 3.12, `uv` for env/deps (`uv run`, `uv add`).

## Pilot companies

| Company | NSE symbol | Tier | Listed / history from |
|---|---|---|---|
| Esconet Technologies | ESCONET | NSE SME | Public ltd from Aug 2023; ARs from FY2023-24 |
| E2E Networks | E2E | Mainboard | IPO 2018 |
| C2C Advanced Systems | C2C | NSE SME | FY2025-26 only |
| APAR Industries | APARINDS | Mainboard | ARs back to 2012 |
| Hero MotoCorp | HEROMOTOCO | Mainboard | ARs back to FY2011-12 |

## Key findings (durable — verified 2026-09-21)

**Two layers, very different access:**

- **Discovery layer is bot-walled.** `www.nseindia.com` (incl. `/api/*`) sits behind Akamai Bot Manager — session cookies + full browser headers still get a decoy "Resource not found" page or 403. `www.bseindia.com` main site and company IR sites (TCS, Hero MotoCorp) also 403.
- **Archive layer is open.** Direct PDF URLs return `200 application/pdf` with plain `curl` and a browser User-Agent — no cookies, no session:

| Host | Pattern | Used for |
|---|---|---|
| `nsearchives.nseindia.com` | `/corporate/<SYMBOL>_<timestamp>_<desc>.pdf` | NSE corporate filings: concalls, presentations, results outcomes |
| `archives.nseindia.com` | `/annual_reports/AR_<id>_<SYMBOL>_<from>_<to>_A_<id>_<ts>.pdf` | NSE annual reports (mainboard) |
| `archives.nseindia.com` | `/annual_reports/SME_AR_<id>_<SYMBOL>_...pdf` | NSE annual reports (SME) |
| `www.bseindia.com` | `/xml-data/corpfiling/AttachHis/<uuid>.pdf` | BSE filing archive |
| `www.bseindia.com` | `/stockinfo/AnnPdfOpen.aspx?Pname=<uuid>.pdf` | 302 → the `xml-data` URL above; use `curl -L` |

Filenames embed internal IDs/timestamps — **they can't be derived, only discovered.** These patterns are undocumented and could change or become protected without notice.

**Current discovery workaround:** Screener.in (`https://www.screener.in/company/<SYMBOL>/` or `/consolidated/`) lists historical docs and links to the archive URLs above. It is an index only — record the archive URL as the source, not Screener.

**SME vs mainboard is a fork, not a filter:** SME companies file half-yearly (not quarterly) and use the `SME_AR_` annual-report prefix.

**Known gaps:**
- Official filed shareholding-pattern PDF (Reg-31) not found for any pilot company — Screener only has derived percentages.
- Periodic-results PDFs couldn't be isolated for large mainboard companies (APAR, Hero) among surrounding filings.
- Company-owned IR sites 403 — not a usable fallback.

## Rules

- **Legal/volume:** NSE ToS prohibits automated/systematic scraping without written consent; bulk/commercial access is via NSE Data & Analytics (paid). This project is **personal research, low volume**. Keep it that way until a decision in `PROGRESS.md` says otherwise.
- **Don't** call `www.nseindia.com/api/*` or try to defeat bot protection (no proxy rotation, no fingerprint spoofing, no challenge solving).
- **Do** throttle: sequential requests, seconds apart, no concurrency against exchange hosts.
- **Never fabricate URLs.** If a document can't be found, record `not found` with a note.
- **Record verification honestly:** only mark `200` if actually fetched this session; otherwise `untested`.
- Send a normal browser User-Agent — plain `curl` without one fails on `nsearchives` (HTTP/2 error).

## Data conventions

`data/document_availability_matrix.csv` columns:

```
company,symbol,listing_tier,doc_type,period_label,filed_date,primary_exchange,host_domain,url,fetch_status,notes
```

| Column | Allowed values / format |
|---|---|
| `listing_tier` | `NSE Mainboard`, `NSE SME` |
| `doc_type` | `annual_report`, `periodic_results`, `shareholding_pattern`, `concall_transcript`, `investor_presentation` |
| `period_label` | `FY2020-21`, `Q2 FY24`, `H1 FY25` |
| `filed_date` | `YYYY-MM-DD` |
| `primary_exchange` | `NSE`, `BSE`, `other` (company site) — derived from the host, never an aggregator |
| `fetch_status` | `200` (verified this session), `untested`, `blocked`, `not found` |

## Verifying a URL

```bash
curl -s -o /dev/null -m 20 -L \
  -w "%{http_code}|%{content_type}|%{size_download}\n" \
  -A "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36" \
  "<url>"
```

Expect `200|application/pdf|<bytes>`.
