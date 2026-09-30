# Progress

Last updated: 2026-09-30.

## Goal and scope

Build a fundamental-analysis agent grounded in company filings: collection → curation → parsing → chunking → embeddings/vector database → retrieval → analysis with source citations. BSE and NSE are the primary sources. The target scope is approximately 3,000 companies; the current sample covers five.

## Implemented download pipeline

- Runtime package: `filings/`; offline regression tests: `tests/`.
- BSE sample: 543664 (Kaynes), 540699 (Dixon), 500325 (Reliance). The user reviewed these companies and was satisfied with collection scope.
- NSE sample: AIMTRON and ADISOFT. The adapter currently supports Emerge/SME; mainboard support is not implemented.
- Both collectors default to ten years of discovery. Availability may be shorter.
- Six categories: annual reports, shareholding, investor presentations, call transcripts, credit ratings and financial results.
- NSE filters announcement metadata before downloading. Full responses, including rejected announcement metadata, are retained in SQLite.
- SQLite stores run history, company outcomes, document metadata, attempt history, full API responses, curation decisions and HTML chunks.
- Downloads use temporary files and atomic renames. Each completed task is checkpointed. Valid existing files are reused after interruption.
- Explicit failed-file and run-based retries; configurable default failure threshold is 5%. Discovery failures and unfinished work also flag retries.
- A process lock allows one writer; interrupted runs are recovered on the next writer startup.
- Curation selects required categories, handles revisions and alternate formats, and removes identical-content duplicates. Both collectors invoke it automatically.
- Optional hash-matched content-review overrides remain in `config/nse_verified_announcements.json`; automatic selection for new companies requires no review entry.

## Current local data

`data/pipeline.sqlite3` is the only metadata index. Downloaded documents and NSE detail JSON remain on disk; back them up together with SQLite.

| Metric | Count |
| --- | ---: |
| Document records | 775 |
| Downloaded records | 736 |
| Failed records | 32 |
| Permanently inactive records, excluded from ingestion | 7 |
| Selected documents | 476 |
| PDF documents awaiting extraction | 369 |
| Structured JSON documents | 84 |
| HTML/iXBRL documents | 23 |
| HTML chunks | 306 |

Selected documents by company: Reliance 197, Dixon 146, Kaynes 91, AIMTRON 33, ADISOFT 9.

Existing sample files were imported offline. Original download timestamps were unavailable and remain null; the recorded initial run describes the import rather than claiming new downloads. Original API fields never saved during initial collection cannot be reconstructed. Future runs retain full responses.

## Latest cleanup and verification

Removed unused configuration and utilities, duplicate file indexes, and disk copies of listing responses after verifying all original metadata fields and saved responses exist in SQLite. Collectors now store listing responses only in SQLite. Active NSE detail JSON remains document content required by curation and retry processing.

- All 15 offline tests passed, covering filtering, full-response retention, metadata preservation, retries, interruptions, writer locking, discovery failures, thresholds and curation.
- Offline curation: 476 selected documents, 292 ordinary exclusions, 306 HTML chunks. Seven inactive records remain excluded separately.
- Compared every ingestion-view row, chunk row and run-history row before and after cleanup: unchanged.
- SQLite integrity and foreign-key checks passed.
- No live exchange downloads were run. The 32 existing failures remain unresolved.
- No Git commit or push was performed.

## Commands

Run from the repository root:

```bash
venv/bin/python -m filings.status
venv/bin/python -m filings.status --failures
venv/bin/python -m filings.bse 543664 540699 500325 --years 10 --download
venv/bin/python -m filings.nse AIMTRON ADISOFT --years 10 --download
venv/bin/python -m filings.nse --retry-failed
venv/bin/python -m filings.bse --retry-run RUN_UUID
venv/bin/python -m filings.curate
venv/bin/python -m unittest discover -s tests -v
```

See `README.md` for schema fields and command options; `docs/pipeline.md` explains each runtime module.

## Next stage and limitations

Use SQLite `ingestion_documents` as the parsing/ingestion allowlist. Never scan all downloaded files for ingestion. Existing HTML chunks are in `document_chunks`; PDFs still require parsing and chunking. Structured results/shareholding JSON needs an explicit structured-data path.

No PDF parser, embedding model, vector database or analysis-agent implementation has been selected. Preserve filing dates, reporting periods, accounting basis, units, source URLs, hashes and page/table references through parsing. Metadata classification is not PDF content verification and does not guarantee complete exchange coverage.

Before large-scale collection, a small live smoke run can verify current exchange responses. Partial attachments restart from byte zero; successful files are reused. The next useful work is designing PDF extraction and chunking using the selected documents.
