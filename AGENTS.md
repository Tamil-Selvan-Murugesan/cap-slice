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

**Current phase: sourcing research with a matrix-URL downloader.** We are mapping data sources, workarounds, ToS/subscription constraints, and scaling issues on a 5-company pilot. The only code is a downloader for URLs already in the matrix — it does no discovery. Don't build discovery/crawler infrastructure unless `PROGRESS.md` says that decision has been made.

## Repo layout

| Path | What it is |
|---|---|
| `data/document_availability_matrix.csv` | Pilot catalog: document candidates and gap placeholders, 5 companies |
| `docs/document-sourcing-report.md` | Findings report: sources, workarounds, ToS, scaling issues, open questions |
| `data/<SYMBOL>/<doc_type>s/` | Downloaded documents, e.g. `data/E2E/annual_reports/`. Files named `<filed_date>_<period>.pdf`. Gitignored — re-create with the downloader |
| `data/download_manifest.csv` | Latest retained download outcome per URL: result, HTTP code, bytes, sha256, local path |
| `src/cap_slice/downloader.py` | Downloads every matrix row that has a URL (`uv run cap-slice-download`) |
| `docs/pilot-verification-2026-09-23.md` | Independent content checks and scaling findings |
| `PROGRESS.md` | Living status + decision log |

Tooling: Python 3.12, `uv` for env/deps (`uv run`, `uv add`).

## Pilot companies

| Company | NSE symbol | Tier | Listed / history from |
|---|---|---|---|
| Esconet Technologies | ESCONET | NSE SME | Public ltd from Aug 2023; ARs from FY2023-24 |
| E2E Networks | E2E | Mainboard | IPO 2018; SME until mainboard trading began Apr 12, 2022 |
| C2C Advanced Systems | C2C | NSE SME | Listed Dec 3, 2024; FY2024-25 annual report verified |
| APAR Industries | APARINDS | Mainboard | ARs back to 2012 |
| Hero MotoCorp | HEROMOTOCO | Mainboard | ARs back to FY2011-12 |

## Key findings (reconciled 2026-09-23)

The downloader's full-catalog retrieval results are recorded in `data/download_manifest.csv`; independent content checks are in [`docs/pilot-verification-2026-09-23.md`](docs/pilot-verification-2026-09-23.md). Retrieval success does not establish correct document type or complete historical coverage.

**Content validation is separate from retrieval:** C2C's H1 FY2025–26 `periodic_results` candidate (matrix row 76 at verification time) is actually an equity/warrant allotment disclosure. Exclude it from results coverage pending catalog correction. The verification report documents the checks and two APAR additions awaiting catalog reconciliation; the downloader's matrix updates remain authoritative for its retrieval run.

**Two layers, very different access:**

- **Discovery access varies.** Earlier NSE API attempts were blocked; those APIs were not retested in the independent pilot and remain off-limits. The later NSE homepage request returned 403, BSE's homepage returned an HTML shell, and APAR's IR page worked. Hero's 18 catalogued company-hosted transcripts returned 403 in the full downloader run. These are observations about particular URLs, dates and client environments, not universal host guarantees.
- **Archive retrieval works for many discovered URLs.** The independent sample downloaded every selected exchange document using a normal browser User-Agent, without cookies; the full-catalog run also found failed URLs. Common observed patterns:

| Host | Pattern | Used for |
|---|---|---|
| `nsearchives.nseindia.com` | `/corporate/<SYMBOL>_<timestamp>_<desc>.pdf` | NSE corporate filings: concalls, presentations, results outcomes |
| `archives.nseindia.com` | `/annual_reports/AR_<id>_<SYMBOL>_<from>_<to>_A_<id>_<ts>.pdf` | NSE annual reports (mainboard) |
| `archives.nseindia.com` | `/annual_reports/SME_AR_<id>_<SYMBOL>_...pdf` | NSE annual reports (SME) |
| `www.bseindia.com` | `/xml-data/corpfiling/AttachHis/<uuid>.pdf` | BSE filing archive |
| `www.bseindia.com` | `/stockinfo/AnnPdfOpen.aspx?Pname=<uuid>.pdf` | 302 → the `xml-data` URL above; use `curl -L` |

Filenames embed internal IDs/timestamps — **they can't be derived, only discovered.** These patterns are undocumented and could change or become protected without notice.

**Current discovery workaround:** Screener.in (`https://www.screener.in/company/<SYMBOL>/` or `/consolidated/`) lists historical docs and links to the archive URLs above. It is an index only — record the archive URL as the source, not Screener.

**Older sampled NSE annual reports use ZIPs.** The downloader found single-PDF ZIPs for reports through FY2022-23 and plain PDFs in later sampled years; do not assume a universal cutoff. Seen for both `AR_` and `SME_AR_` (E2E FY2017-18–FY2022-23, APAR FY2011-12). One ZIP had a nested path inside (`<name>.zip/<file>.pdf`), so match on `.pdf` rather than exact names. The sampled BSE `bseplus/AnnualReport/` files are PDFs. *(verified 2026-09-23)*

**Use the listing tier applicable to the reporting period:** SME financial results and shareholding patterns have half-yearly frequency under LODR 33(5) and 31(1); mainboard frequency is quarterly. Historical migrations matter (e.g. E2E in 2022). The sampled SME annual reports use the `SME_AR_` prefix.

**Known gaps:**
- Full shareholding history remains unresolved, but an issuer-hosted APAR Reg-31 report for December 2018 was fetched and content-checked on 2026-09-23.
- APAR Q4/FY2024-25 results were found on its company site; full APAR/E2E histories and Hero results remain unresolved. C2C's original results entry is misclassified.
- Hero's sampled company URLs returned 403; APAR's IR page and documents returned 200. Do not exclude all company-owned sites.

## Rules

- **Legal/volume:** NSE ToS prohibits automated/systematic scraping without written consent; bulk/commercial access is via NSE Data & Analytics (paid). This project is **personal research, low volume**. Keep it that way until a decision in `PROGRESS.md` says otherwise.
- Low volume is an operational constraint, not a terms-of-use exemption. Confirm rights and exact historical/document coverage before adopting any bulk route, including Screener or a paid feed.
- **Don't** call `www.nseindia.com/api/*` or try to defeat bot protection (no proxy rotation, no fingerprint spoofing, no challenge solving).
- **Do** throttle: sequential requests, seconds apart, no concurrency against exchange hosts.
- **Never fabricate URLs.** If a document can't be found, record `not found` with a note.
- **Record verification honestly:** only mark `200` if actually fetched this session; otherwise `untested`.
- Keep dated observations separate from historical catalog statuses. Do not infer individual failures from another URL on the same host; HTTP success does not validate company/type/period.
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

Expect a successful PDF or ZIP response, then validate its contents. An HTTP 200 alone is insufficient.

## Downloader

```bash
uv run cap-slice-download --dry-run            # list targets, fetch nothing
uv run cap-slice-download                      # everything with a URL
uv run cap-slice-download --symbol E2E --doc-type annual_report
uv run cap-slice-download --refresh-status     # recompute download_status only
```

- Sequential, 3 s between requests (`--delay`). Existing files are skipped, so re-running resumes.
- Checks the first bytes of each response: only real PDF (`%PDF`) or ZIP (`PK`) files are saved; HTML decoy/error pages count as failures.
- ZIPs holding exactly one PDF are unpacked in place (ZIP deleted, PDF kept under the same name). Anything else stays a ZIP and is reported. Any ZIPs already on disk are unpacked at the start of every run.
- Writes `fetch_status` back to the matrix: `200` on success, `blocked` on 401/403, `not found` on 404/410 (`--no-update-matrix` to skip).

The downloader currently maps an existing local file to `fetch_status=200` without a new HTTP request. Use dated manifest/pilot observations to establish when a URL was actually fetched. `download_status` reflects the files in the worktree where it was computed; gitignored downloads are not automatically shared across worktrees.

## Concurrent work

Two agents may work in separate worktrees. Before committing or rebasing, reread current `main` guidance and progress, preserve the other agent's relevant changes, and reconcile duplicated or superseded claims using dated evidence. Update only your worktree; do not overwrite the other agent's working files.
