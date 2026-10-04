# Project purpose

Build an agent that performs fundamental analysis of a company using a document-backed knowledge source. BSE and NSE are the primary data sources. The intended pipeline is:

Exchange filings → collection → curation → parsing → chunking → embeddings/vector database → retrieval → fundamental-analysis agent with source citations.

The current sample covers five companies. The eventual collection scope is approximately 3,000 companies, so designs must work without an LLM manually finding, classifying or approving every document.

# Start of a session

Read `progress.md` for completed work, current counts, decisions and next steps. Read `README.md` for collection commands and output formats. Inspect the relevant implementation before changing behavior; distinguish implemented functionality from planned work.

# Scope and decisions

- Collect annual reports, shareholding patterns, investor presentations, earnings/conference-call transcripts, credit-rating filings and financial results.
- Both collectors default to a ten-year lookback. This is a search window, not a guarantee of ten years of available filings.
- `filings/bse.py` uses BSE scrip codes. The user manually reviewed the three sample BSE companies and was satisfied with coverage. Preserve that collection scope unless requested otherwise.
- `filings/nse.py` currently targets NSE Emerge/SME. Do not assume it supports all NSE mainboard companies.
- Filter NSE announcement metadata before attachment downloads. Save all raw announcement metadata for auditing. Share the classifier between collection and curation through `filings/nse_classification.py`.
- Metadata classification is not PDF content verification. Avoid claiming complete coverage or fully verified contents based on filenames or subjects alone.
- `config/nse_verified_announcements.json` contains optional existing content-review overrides. Matching hashes allow reviewed titles, periods, categories and supersession decisions. New matching filings must not require a manual review entry.

# Data and ingestion rules

- SQLite (`data/pipeline.sqlite3`) is the source of truth. Use the `ingestion_documents` view (`documents.selected_to_ingest=1`) as the ingestion allowlist. Never ingest by scanning raw download directories or using a separate file index.
- Preserve downloaded source documents and active detail JSON. Store metadata and full exchange responses only in SQLite. Curation should not delete source documents.
- Records with download_status=archived are permanently inactive; never reintroduce them into ingestion or retries.
- Reuse successful downloads; do not rerun network collection merely to rebuild curation or ingestion.
- Retain document IDs, company identifiers, source URLs, hashes, filing dates, reporting periods and page/table references through parsing and chunking so answers can cite their evidence.
- Distinguish filing dates from financial reporting periods and standalone from consolidated accounts.
- Keep revision and deduplication rules. Avoid ingesting multiple representations of the same filing as independent evidence.
- Use SQLite `document_chunks`, joined to selected documents, for the currently processed HTML/iXBRL documents. PDFs still require extraction and chunking. Structured shareholding/results JSON should have an explicit structured-data path rather than blindly embedding raw JSON.
- Do not invent missing numbers or treat missing filings as zero values. Preserve units, accounting basis and table context when extracting financial information.

# Working practices

- Keep changes focused on the user's requested stage. No vector database or embedding model has been selected yet. PDF parsing: PaddleOCR-VL-1.6 on every page (served by vLLM 0.30); evaluation code in `parsing_eval/` and `vlm_bench/`, results in `vlm_bench/notes.md`, generated data in `data/parsing_eval/` (never commit it).
- For collection/filter changes, prefer offline tests and saved exchange responses before requesting new downloads. `venv/bin/python -m unittest tests.test_nse_filtering` runs the existing NSE regression checks.
- After changes affecting curation, run `venv/bin/python -m filings.curate` and inspect SQLite selection counts and affected records. Both collectors also curate automatically after a run.
- Update `progress.md` after meaningful milestones with what changed, how it was verified, remaining limitations and the next useful action. Keep durable project rules in this file and session-specific status in `progress.md`.

# Download pipeline

- Shared state and queue logic live in `filings/db.py`, `filings/schema.sql` and `filings/pipeline.py`. Keep exchange discovery in the collector modules.
- Record runs, requested companies, documents and attempts durably. Commit each document completion and its run outcome together. Preserve failures separately from listing/discovery errors.
- Preserve all input metadata in `metadata_json`, raw exchange records in `raw_metadata_json`, and full API payloads in `source_responses`; SQL columns provide convenient querying without discarding unknown fields.
- Default failure threshold is configurable (`--failure-threshold 0.05`). Use explicit bounded retries; never introduce unlimited automatic retry loops.
- `--retry-failed` processes known failed/pending required documents. `--retry-run RUN_UUID` targets flagged companies and rediscovers listings if needed. Completed files must be reused after interruptions.
- One writer per database is enforced with a process lock. Tests must use temporary databases rather than mutating production state.
- Run `venv/bin/python -m unittest discover -s tests -v` for changes to persistence, retries or filtering.

# Repository organization

- Keep runtime code in `filings/` and offline tests in `tests/`.
- Run entry points as modules from the repository root: `python -m filings.bse`, `python -m filings.nse`, `python -m filings.curate`, and `python -m filings.status`.
- `docs/pipeline.md` explains the file-by-file flow. Update it and README commands when changing module layout.
- Keep active optional overrides in `config/`. Remove unused configuration and utilities instead of retaining a second workflow.
- `requirements.txt` records runtime dependencies. Keep databases, downloaded files, virtual environments and caches out of Git.
