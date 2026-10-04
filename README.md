# BSE/NSE document collection pipeline

Collect exchange filings for a future fundamental-analysis agent. SQLite is the source of truth for run history, document metadata, download checkpoints, ingestion selection and HTML chunks. Source documents remain files on disk.

The current sample has five companies: BSE 543664 (Kaynes), 540699 (Dixon), 500325 (Reliance), and NSE Emerge AIMTRON and ADISOFT. NSE mainboard support is not implemented.

## Setup

Use Python 3.11 or newer on Linux/WSL (the writer lock uses `fcntl`). Run commands from the repository root.

```bash
python3 -m venv venv
venv/bin/python -m pip install -r requirements.txt
```

SQLite and the test runner are part of Python; no database server is required.

## Repository layout

```text
filings/                 Runtime package
  bse.py                 BSE discovery and command entry point
  nse.py                 NSE SME discovery and command entry point
  nse_classification.py  Shared NSE category rules
  pipeline.py            Shared download queue, retries and orchestration
  db.py                  Durable state and checkpoint operations
  schema.sql             SQLite tables and views
  curate.py              Ingestion selection and existing HTML chunking
  status.py              Read-only history/reporting command
config/                  Optional active review overrides
tests/                  Offline regression tests
docs/pipeline.md        Detailed flow and file guide
parsing_eval/            PDF parser evaluation: page profiling, CPU baselines, eval-set builders
vlm_bench/               GPU benchmark of OCR vision models (RunPod) + full-corpus PaddleOCR-VL run
requirements.txt         Pinned direct dependencies
AGENTS.md                Project instructions
progress.md              Current state and next steps
data/                    Local documents/database and data/parsing_eval/ outputs (ignored by Git)
```

The normal flow is **exchange adapter → shared queue/downloader → SQLite checkpoints → curation → ingestion view**. See [the pipeline walkthrough](docs/pipeline.md) for what each file and main function does.


## Normal collection

```bash
venv/bin/python -m filings.bse 543664 540699 500325 --years 10 --download
venv/bin/python -m filings.nse AIMTRON ADISOFT --years 10 --download
```

Default database: `data/pipeline.sqlite3`. Override with `--db PATH`. `--output DIR` controls the document directory and the default database location. Paths stored for new downloads are absolute.

Both collectors default to a ten-year lookback. This is a search window, not a guarantee that all ten years of filings exist. Omit `--download` to discover and checkpoint metadata only; attachment and detail-JSON tasks remain deferred for a later download run.

The pipeline discovers filings, saves their records, processes each queued document, then automatically runs curation for the affected companies. Successful existing files are validated and reused. New files are written to `.part` and atomically renamed. Each completion commits document status, attempt history and run outcome together.

All indexing metadata and original API responses are stored in SQLite. On disk, keep downloaded attachments and NSE detail JSON used as document content. Back up the database together with these source files.

## History and retries

```bash
# Recent runs
venv/bin/python -m filings.status

# Per-company counts, failure rates and discovery errors for a run
venv/bin/python -m filings.status --run RUN_UUID

# Current failed or unavailable document records
venv/bin/python -m filings.status --failures

# Retry only failed/pending required documents, without listing discovery
venv/bin/python -m filings.bse 500325 --retry-failed
venv/bin/python -m filings.nse AIMTRON ADISOFT --retry-failed

# Omit symbols to retry known companies for that exchange
venv/bin/python -m filings.nse --retry-failed

# Retry companies flagged by a previous run
venv/bin/python -m filings.bse --retry-run RUN_UUID
venv/bin/python -m filings.nse --retry-run RUN_UUID
```

`--retry-run` also repeats discovery for flagged companies whose listing discovery failed or never finished. `--retry-failed` works only from known document records; it cannot discover filings that were never listed. To refresh listings, rerun the normal collection command. Successful files will still be reused.

The configurable default `--failure-threshold 0.05` flags a company when:

- at least one document failed, and `failed / (downloaded + reused + failed) >= 0.05`; or
- downloads remain pending; or
- discovery failed or was interrupted/not started.

`--failure-threshold 0` flags any failure. The threshold is saved on each run. Retries are explicit, bounded runs; there is no unlimited automatic retry loop. HTTP requests also have a bounded transport retry policy for transient failures.

Counts refer to document tasks, not HTTP requests: `files_downloaded` counts records completed with new attachment/detail data; `files_reused` counts records completed from existing files; `files_failed` counts unsuccessful tasks; `files_pending` counts unfinished tasks; `files_deferred` counts deferred document tasks. Discovery errors are separate from download failures, so an API listing failure is never reported as a successful empty collection.

### Stopping and resuming

Ctrl+C preserves all committed progress. A process killed abruptly may remain marked `running` until the next writer starts; the next writer marks its unfinished run/attempts interrupted. Completed files are reused, including a file renamed just before a crash. A partially downloaded file restarts from byte zero; byte-range resumption is not implemented. Previously successful files are not downloaded again merely because the command stopped.

One writer command can use a database at a time, enforced with a process lock (Linux/WSL). Read-only SQLite queries can run concurrently under WAL mode. Use SQLite's backup facility for a live backup; do not copy only the `.sqlite3` file while a writer is active.

## Database layout

Full definitions are in `filings/schema.sql`.

| Table/view | Purpose |
| --- | --- |
| `collection_runs` | Run UUID, mode and options, exchange, timestamps, status, threshold, options and run-level error |
| `company_runs` | One row per requested company/run, lifecycle state, discovery state and errors |
| `company_run_summary` (view) | Per-company download/reuse/failure/pending/deferred counts, failure rate and retry recommendation |
| `documents` | Every document record, metadata, latest download state and ingestion decision |
| `run_documents` | Per-run document queue and outcome; supports accurate counts and checkpoints |
| `download_attempts` | Processing-attempt history with start/end times, status, error, actual URL, bytes and hash |
| `source_responses` | Original API payloads and request parameters, tied to a company run |
| `document_chunks` | Existing HTML/iXBRL chunks and their source/table metadata |
| `ingestion_documents` (view) | Only documents with `selected_to_ingest = 1` |

### Document columns

- Identity: `id` (database primary key), `exchange`, `symbol`, `source`, `source_id`, `source_url`. A unique constraint on the exchange/company/source/source ID/URL prevents repeat collection from inserting the same record twice.
- Filing metadata: `kind`, `title`, `description`, `subcategory`, `filing_date`, `reporting_period`, `filing_status`, `fallback_url`.
- Complete metadata: `metadata_json` preserves input fields, including fields without dedicated SQL columns; `raw_metadata_json` preserves the original exchange record where available. `source_responses` retains complete listing/detail responses. Metadata JSON inside SQLite preserves nested data without requiring a constantly changing schema.
- Download state: `file_path`, `detail_path`, `sha256`, `byte_size`, `content_type`, `url_used`, `download_status`, `last_error`, `downloaded_at`.
- Audit: `first_seen_at`, `updated_at`, `first_seen_run_id`, `last_seen_run_id`. Original download times for the initial sample are unknown and remain null.
- Ingestion: `selected_to_ingest` (0/1), `selection_reason`, `canonical_document_id`, `corpus_id`, `retrieval_title`, `curated_kind`, `curated_period`, `ingestion_path`, `ingestion_sha256`, `ingestion_format`, `processing`, `aliases_json`, `source_ids_json`.

Original classification/metadata remains available even when curation changes the category or title. `corpus_id` retains the prior content-based ingestion identity; it differs from the database record `id`. Curation recalculates selection, so manual edits to selection columns will be replaced on the next curation run.

Examples:

```sql
SELECT run_id, symbol, files_downloaded, files_reused, files_failed,
       files_pending, failure_rate, retry_recommended
FROM company_run_summary ORDER BY started_at DESC;

SELECT id, symbol, curated_kind, retrieval_title, ingestion_path, processing
FROM ingestion_documents;

SELECT symbol, selection_reason, COUNT(*)
FROM documents WHERE selected_to_ingest = 0
GROUP BY symbol, selection_reason;

SELECT a.*, d.symbol, d.source_id
FROM download_attempts a JOIN documents d ON d.id = a.document_id
ORDER BY a.id DESC;
```

## Curation and ingestion

```bash
# Rebuild decisions and chunks offline, using SQLite and existing files
venv/bin/python -m filings.curate
```

Use `ingestion_documents`, or `SELECT * FROM documents WHERE selected_to_ingest=1`, as the ingestion allowlist. Never scan raw download directories to build the vector corpus.

Curation keeps the six required categories, chooses the latest annual/shareholding revisions, chooses the latest integrated financial filing per period/accounting basis, prefers rendered iXBRL over alternate representations, and removes exact-content duplicates within a company. Excluded records remain in `documents` with their reason. Selection and chunk replacement occur in one transaction.

`document_chunks` currently contains only HTML/iXBRL chunks. The parser skips styles/scripts/hidden headers and splits between table rows (default target 550 words). PDFs are parsed with PaddleOCR-VL-1.6 (see `parsing_eval/README.md`, `vlm_bench/README.md` and `vlm_bench/notes.md`); page/section-aware chunking is still to be built. Structured shareholding/financial JSON is better queried through a structured-data path than embedded as raw JSON. An embedding model, vector database and analysis agent are still to be implemented.

`config/nse_verified_announcements.json` provides optional existing content-review overrides, applied only when the hash matches. New NSE filings are classified automatically from metadata and need no manual review entry. This is not automatic PDF content verification.


## Sources and selection

BSE uses the installed `bse` package for announcement listings and recent results snapshots, plus BSE website APIs for annual reports and shareholding. The six categories are annual reports, shareholding patterns, investor presentations, call transcripts, credit-rating disclosures and financial results. BSE snapshot JSON is recent structured data, not a ten-year structured-results history.

NSE uses `GetQuoteApi` for announcement/annual-report listings and quote summaries, `corporate-share-holdings-master` / `corporate-share-holdings-sme` for ownership, `corporates-financial-results` / `corporates-financial-results-data` for legacy results and `integrated-filing-results` for newer results. Announcements are requested in 180-day windows. Integrated results are paginated in batches of 100.

NSE announcement filtering uses subject, attachment description and filename before downloading. `filings/nse_classification.py` recognizes transcripts, investor/analyst presentations, credit-rating phrases and financial-results phrases. It rejects results references in meeting invitations/notices. Annual reports, ownership and structured results use dedicated endpoints. Broad or misleading metadata can still produce missed filings or false positives.

## Offline tests

```bash
venv/bin/python -m unittest discover -s tests -v
```

Tests use temporary databases/files and fake network responses; they do not contact the exchanges.
