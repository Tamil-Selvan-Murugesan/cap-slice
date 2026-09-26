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

**Current phase: research, not building.** We are mapping data sources, workarounds, ToS/subscription constraints, and scaling issues on a 5-company pilot. Code so far: a downloader for URLs already in the matrix (no discovery), and an indexing pipeline (extract → chunk → embed → Qdrant). Don't build discovery/crawler infrastructure unless `PROGRESS.md` says that decision has been made.

## Repo layout

| Path | What it is |
|---|---|
| `data/document_availability_matrix.csv` | Pilot catalog: one row per document, 5 companies |
| `docs/document-sourcing-report.md` | Findings report: sources, workarounds, ToS, scaling issues, open questions |
| `data/<SYMBOL>/<doc_type>s/` | Downloaded documents, e.g. `data/E2E/annual_reports/`. Files named `<filed_date>_<period>.pdf`. Gitignored — re-create with the downloader |
| `data/download_manifest.csv` | One row per download attempt: result, HTTP code, bytes, sha256, local path |
| `src/cap_slice/downloader.py` | Downloads every matrix row that has a URL (`uv run cap-slice-download`) |
| `src/cap_slice/extract.py` → `chunk.py` → `embed.py` → `vectorstore.py` | Indexing pipeline stages; `index.py` runs them (`uv run cap-slice-index`) |
| `data/qdrant/` | Local Qdrant store (gitignored; re-create with `cap-slice-index`) |
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

**NSE annual reports up to FY2022-23 are ZIPs, not PDFs.** `archives.nseindia.com/annual_reports/` serves `.zip` files, each wrapping a single PDF, for FY2022-23 and earlier; from FY2023-24 they're plain PDFs. Seen for both `AR_` and `SME_AR_` (E2E FY2017-18–FY2022-23, APAR FY2011-12). One ZIP had a nested path inside (`<name>.zip/<file>.pdf`), so match on `.pdf` rather than exact names. BSE's `bseplus/AnnualReport/` serves PDFs for all years. *(verified 2026-09-23)*

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
company,symbol,listing_tier,doc_type,period_label,filed_date,primary_exchange,host_domain,url,fetch_status,notes,download_status
```

| Column | Allowed values / format |
|---|---|
| `listing_tier` | `NSE Mainboard`, `NSE SME` |
| `doc_type` | `annual_report`, `periodic_results`, `shareholding_pattern`, `concall_transcript`, `investor_presentation` |
| `period_label` | `FY2020-21`, `Q2 FY24`, `H1 FY25` |
| `filed_date` | `YYYY-MM-DD` |
| `primary_exchange` | `NSE`, `BSE`, `other` (company site) — derived from the host, never an aggregator |
| `fetch_status` | `200` (verified this session), `untested`, `blocked`, `not found` |
| `download_status` | `yes` (file present under `data/<SYMBOL>/<doc_type>s/`), `no` — set by the downloader from what's on disk |

## Verifying a URL

```bash
curl -s -o /dev/null -m 20 -L \
  -w "%{http_code}|%{content_type}|%{size_download}\n" \
  -A "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36" \
  "<url>"
```

Expect `200|application/pdf|<bytes>`.

## Downloader

```bash
uv run cap-slice-download --dry-run            # list targets, fetch nothing
uv run cap-slice-download                      # everything with a URL
uv run cap-slice-download --symbol E2E --doc-type annual_report
uv run cap-slice-download --refresh-status     # recompute download_status only
```

- Sequential, 3 s between requests (`--delay`). Existing files are skipped, so re-running resumes.
- Checks the first bytes of each response: only real PDF (`%PDF`) or ZIP (`PK`) files are saved; HTML decoy/error pages count as failures (recorded as `not found`).
- ZIPs holding exactly one PDF are unpacked in place (ZIP deleted, PDF kept under the same name). Anything else stays a ZIP and is reported. Any ZIPs already on disk are unpacked at the start of every run.
- Writes `fetch_status` back to the matrix: `200` on success, `blocked` on 401/403, `not found` on 404/410 (`--no-update-matrix` to skip).

## Indexing pipeline

```bash
uv run cap-slice-index --dry-run               # extract + chunk only; no API calls
VOYAGE_API_KEY=... uv run cap-slice-index      # embed + store every download_status=yes row
uv run cap-slice-search "capex guidance" --symbol E2E
```

- **Extract** (`extract.py`): PyMuPDF text per page. Pages under 50 chars count as having no text layer and are left out; a document where more than half the pages have none is skipped as "needs OCR". No OCR yet.
- **Chunk** (`chunk.py`): paragraph-aware, ~500 words with 75-word overlap; each chunk keeps `page_start`/`page_end`. Filings average ~1.56 Voyage tokens per word (≈840 tokens per chunk), more for number-heavy text. **Known limitation:** tables are flattened into running text — see `PROGRESS.md`.
- **Embed** (`embed.py`): Voyage AI, `voyage-finance-2` by default (1024-dim, 120K tokens per request; `VOYAGE_MODEL` to override), `input_type="document"` for chunks and `"query"` for searches, batched by token count (≤100K tokens per request, counted locally).
- **Store** (`vectorstore.py`): Qdrant collection `filings`, cosine distance. Local folder `data/qdrant/` by default; set `QDRANT_URL` for a server (payload indexes on `symbol`, `doc_type`, `period_label`, `doc_id` are only created there). Point IDs are UUIDv5 of `doc_id#chunk_index`; `doc_id` is the file path under `data/` without extension.
- **Re-runs** skip a document if its file's sha256 is already stored *and* all its chunks are present (`n_chunks`), so an interrupted run only redoes the document it was on; a changed file has its old chunks deleted and new ones written. `--reindex` forces re-embedding. Changing the embedding model means starting a new collection — vectors from different models can't be mixed.
- Each point's payload carries company, symbol, tier, doc type, period, filed date, source URL, local path, pages, chunk text and model name.
