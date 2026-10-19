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
| `docs/plan.md` | Agreed plan for scaling to all 12,980 pages (golden set → GPU parse with Docling + MinerU → parser choice → retrieval → chunking → embeddings) |
| `docs/architecture.md` | **Map of all components and their status** (Mermaid diagram + table) — update it whenever a component is added, replaced or changes status |
| `docs/document-sourcing-report.md` | Findings report: sources, workarounds, ToS, scaling issues, open questions |
| `docs/pdf-parsers-pymupdf4llm-vs-docling.md` | Explainer: what PyMuPDF4LLM and Docling do, their models, how each does OCR, and our measured results |
| `docs/media/pymupdf4llm-vs-docling.mp4`, `tools/explainer_video/` | 3-min captioned video of both parsers on one scanned page (real outputs), and the scripts that build it |
| `data/<SYMBOL>/<doc_type>s/` | Downloaded documents, e.g. `data/E2E/annual_reports/`. Files named `<filed_date>_<period>.pdf`. Gitignored — re-create with the downloader |
| `data/download_manifest.csv` | One row per download attempt: result, HTTP code, bytes, sha256, local path |
| `src/cap_slice/downloader.py` | Downloads every matrix row that has a URL (`uv run cap-slice-download`) |
| `src/cap_slice/extract.py` → `chunk.py` → `embed.py` → `vectorstore.py` | Indexing pipeline stages; `index.py` runs them (`uv run cap-slice-index`) |
| `src/cap_slice/parsing/`, `structured_chunk.py`, `compare_parsers.py` | Parser comparison: Option 1 (`pymupdf_text`), Option 2 (`pymupdf4llm`), Option 3 (`docling`), shared structure-aware chunker, runner `uv run cap-slice-compare` |
| `data/golden/` | Golden sets — v1: `compare_docs.csv` + `parse_facts.csv` (28 facts, 5 docs, partly seen during chunker fixes); **v2: `v2_facts.csv` (150 facts, 61 pages, 45 unseen docs)** + page inventory and sampling. All read off page images, never from a parser. See `data/golden/README.md` |
| `tools/golden/inventory.py` | Page inventory of all PDFs + seeded stratified sample of candidate pages for golden facts |
| `review/` | Parser-comparison outputs (committed): `README.md` verdict, `COMPARISON.md` scores, `<option>/<doc>/parsed.md` (raw parser output), `chunks.md` (what would be embedded), `parsed.json` (parse cache — `cap-slice-compare` reuses it; `--reparse` to redo) |
| `src/cap_slice/batch_parse.py` (`cap-slice-parse`) | Batch runner for any parser: per-document cache in `parsed/<parser>/<doc_id>/` (pages.json + raw JSON + meta.json), resume, per-run logs and GPU sampling in `_runs/` |
| `src/cap_slice/parsing/mineru_vlm.py`, `html_table.py` | MinerU 4 adapter (MinerU2.5-Pro via a VLM server; tier `standard`/`advanced`) and HTML-table → pipe-table converter |
| `src/cap_slice/parsing/paddleocr_vl.py`, `tools/gpu/setup_paddleocr_vl.sh`, `docs/paddleocr-vl.md` | Option 5: PaddleOCR-VL-1.6 (layout model + 0.9B VLM on vLLM 0.30), settings from the co-founder's `main-sirisha` evaluation; own envs `paddle` + `vllm030` |
| `src/cap_slice/periods.py` (`cap-slice-periods`), `data/period_overrides.csv` | Period normaliser: `fiscal_year` / `period_kind` / `period` for every document (label, event-month rule, or checked override), and a check against the periods the documents state → `review/periods/` |
| `src/cap_slice/retrieval_score.py`, `retrieval_bm25.py`, `query_reader.py` (`cap-slice-retrieval-score`, `-retrieval-bm25`, `-query-reader`) | Retrieval experiments: scorer for the 200-question set, BM25 baseline with filter setups (`--filter`, `--soft`), rules-based question reader → `review/retrieval/`, `review/query_reader/` |
| `src/cap_slice/score.py` (`cap-slice-score`) | Scores a parser's cache against golden v2 (default) or v1 (`--facts data/golden/parse_facts.csv --out review/v1`) → `review/<set>/<parser>.md` |
| `docker/`, `tools/gpu/`, `docs/gpu-run.md` | Pinned GPU environments (`docker/requirements-*-{cu130,cu128}.txt`), Dockerfiles, RunPod setup (`setup_runpod.sh`: venvs, since pods can't run Docker), session scripts (`session.sh`: smoke / bench / full runs for all four parsers / `compare`), benchmark builder/report, `full_report.py` (exhaustive comparison of the full runs → `review/gpu/COMPARISON.md`), and the copy-paste runbook |
| `parsed*/` | Batch caches (gitignored; synced with rsync) |
| `data/qdrant/` | Local Qdrant store (gitignored; re-create with `cap-slice-index`) |
| `PROGRESS.md` | Living status + decision log |
| `bugs_resolved.md` | Parser/chunker/scorer/indexing bugs with root cause and fix — read the Lessons first; add an entry whenever you fix one |

Tooling: Python 3.12, `uv` for env/deps (`uv run`, `uv add`).

**Disk:** keep C: above **500 MB** free (user's floor, 2026-10-03). The Linux disk is a virtual disk (`ext4.vhdx`, ~100 GB) on the Windows C: drive. It grows but never shrinks on its own, and on 2026-09-28 C: reached **~210 MB free**. Check `df -h /mnt/c` before any install or large write; don't trust the ~900 GB Linux `df -h /` shows. PyTorch must be CPU-only (configured in `pyproject.toml` via the `pytorch-cpu` index). Docling added ~2 GB (packages + ~0.5 GB models in `~/.cache/huggingface`).

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

## Parser comparison

```bash
uv run cap-slice-compare                                  # all options x golden docs (uses parse cache)
uv run cap-slice-compare --option pymupdf4llm --doc e2e_pres --reparse
```

- Options: `baseline` (extract.py + chunk.py), `pymupdf_text` (Option 1), `pymupdf4llm` (Option 2, layout model + RapidOCR), `docling` (Option 3, layout + TableFormer + RapidOCR, CPU PyTorch). Options 1–3 share `structured_chunk.py`, so differences come from the parser.
- **Parsing is slow for Options 2–3** (3.3 and 15.2 s/page on this laptop; Docling ~95 min for the 375 golden pages, peak 6.1 GB RAM). Run them in the background, one option per process, and rely on the `parsed.json` caches (they store the measured parse time and date) — re-scoring after chunker changes needs no re-parse.
- Don't re-parse Option 2 without pinning its OCR backend: since Docling's install, PyMuPDF4LLM picks `rapidocr` 3.9 instead of `rapidocr_onnxruntime` (`bugs_resolved.md` P6).
- Golden set: `data/golden/compare_docs.csv` (5 docs) and `parse_facts.csv` (28 facts). **Facts are read off rendered page images, never from a parser's output** — keep it that way when adding facts.
- Levels: L1 value in a chunk covering the fact's page; L2 label and value on the same row; L3 + period header and unit in the same chunk; L4 + value under the right column. Each fact is tested against every chunk of its document that covers its page and scores the best single chunk (assumes perfect retrieval). Definitions in `compare_parsers.py`.
- Always open the chunks behind a score change before trusting it — several "improvements" during development were bugs (see `bugs_resolved.md`).
