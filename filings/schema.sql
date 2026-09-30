PRAGMA foreign_keys = ON;
CREATE TABLE IF NOT EXISTS collection_runs (
    run_id TEXT PRIMARY KEY,
    mode TEXT NOT NULL,
    exchange TEXT NOT NULL,
    started_at TEXT NOT NULL,
    finished_at TEXT,
    status TEXT NOT NULL,
    failure_threshold REAL NOT NULL CHECK(failure_threshold BETWEEN 0 AND 1),
    options_json TEXT NOT NULL,
    error TEXT
);
CREATE TABLE IF NOT EXISTS company_runs (
    id INTEGER PRIMARY KEY,
    run_id TEXT NOT NULL REFERENCES collection_runs(run_id),
    exchange TEXT NOT NULL,
    symbol TEXT NOT NULL,
    started_at TEXT NOT NULL,
    finished_at TEXT,
    status TEXT NOT NULL,
    discovery_status TEXT NOT NULL DEFAULT 'pending',
    discovery_errors_json TEXT NOT NULL DEFAULT '[]',
    UNIQUE(run_id, exchange, symbol)
);
CREATE TABLE IF NOT EXISTS documents (
    id INTEGER PRIMARY KEY,
    exchange TEXT NOT NULL,
    symbol TEXT NOT NULL,
    source TEXT NOT NULL,
    source_id TEXT NOT NULL,
    source_url TEXT NOT NULL DEFAULT '',
    kind TEXT NOT NULL,
    title TEXT NOT NULL DEFAULT '',
    description TEXT NOT NULL DEFAULT '',
    subcategory TEXT NOT NULL DEFAULT '',
    filing_date TEXT NOT NULL DEFAULT '',
    reporting_period TEXT NOT NULL DEFAULT '',
    filing_status TEXT NOT NULL DEFAULT '',
    fallback_url TEXT NOT NULL DEFAULT '',
    metadata_json TEXT NOT NULL,
    raw_metadata_json TEXT NOT NULL DEFAULT '{}',
    file_path TEXT,
    detail_path TEXT,
    sha256 TEXT,
    byte_size INTEGER,
    content_type TEXT,
    url_used TEXT,
    download_status TEXT NOT NULL DEFAULT 'pending'
        CHECK(download_status IN ('pending','downloading','downloaded','failed','unavailable','archived')),
    last_error TEXT,
    downloaded_at TEXT,
    first_seen_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    first_seen_run_id TEXT REFERENCES collection_runs(run_id),
    last_seen_run_id TEXT REFERENCES collection_runs(run_id),
    selected_to_ingest INTEGER NOT NULL DEFAULT 0 CHECK(selected_to_ingest IN (0,1)),
    selection_reason TEXT NOT NULL DEFAULT 'Awaiting curation',
    canonical_document_id INTEGER REFERENCES documents(id),
    corpus_id TEXT,
    retrieval_title TEXT,
    curated_kind TEXT,
    curated_period TEXT,
    ingestion_path TEXT,
    ingestion_sha256 TEXT,
    ingestion_format TEXT,
    processing TEXT,
    aliases_json TEXT NOT NULL DEFAULT '[]',
    source_ids_json TEXT NOT NULL DEFAULT '[]',
    UNIQUE(exchange, symbol, source, source_id, source_url)
);
CREATE INDEX IF NOT EXISTS documents_queue ON documents(exchange, symbol, download_status);
CREATE INDEX IF NOT EXISTS documents_ingestion ON documents(selected_to_ingest);
CREATE TABLE IF NOT EXISTS run_documents (
    company_run_id INTEGER NOT NULL REFERENCES company_runs(id),
    document_id INTEGER NOT NULL REFERENCES documents(id),
    outcome TEXT NOT NULL DEFAULT 'pending',
    PRIMARY KEY(company_run_id, document_id)
);
CREATE TABLE IF NOT EXISTS download_attempts (
    id INTEGER PRIMARY KEY,
    company_run_id INTEGER NOT NULL REFERENCES company_runs(id),
    document_id INTEGER NOT NULL REFERENCES documents(id),
    started_at TEXT NOT NULL,
    finished_at TEXT,
    status TEXT NOT NULL,
    error TEXT,
    url_used TEXT,
    byte_size INTEGER,
    sha256 TEXT
);
CREATE TABLE IF NOT EXISTS source_responses (
    id INTEGER PRIMARY KEY,
    company_run_id INTEGER NOT NULL REFERENCES company_runs(id),
    endpoint TEXT NOT NULL,
    parameters_json TEXT NOT NULL,
    payload_json TEXT NOT NULL,
    recorded_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS document_chunks (
    chunk_id TEXT PRIMARY KEY,
    document_id INTEGER NOT NULL REFERENCES documents(id),
    corpus_id TEXT NOT NULL,
    section TEXT,
    table_number INTEGER,
    row_start INTEGER,
    row_end INTEGER,
    text TEXT NOT NULL,
    metadata_json TEXT NOT NULL
);
DROP VIEW IF EXISTS company_run_summary;
CREATE VIEW company_run_summary AS
WITH counts AS (
 SELECT c.*, r.failure_threshold,
    COUNT(q.document_id) AS files_planned,
    SUM(CASE WHEN q.outcome='downloaded' THEN 1 ELSE 0 END) AS files_downloaded,
    SUM(CASE WHEN q.outcome='reused' THEN 1 ELSE 0 END) AS files_reused,
    SUM(CASE WHEN q.outcome='failed' THEN 1 ELSE 0 END) AS files_failed,
    SUM(CASE WHEN q.outcome='pending' THEN 1 ELSE 0 END) AS files_pending,
    SUM(CASE WHEN q.outcome='deferred' THEN 1 ELSE 0 END) AS files_deferred
 FROM company_runs c JOIN collection_runs r USING(run_id)
 LEFT JOIN run_documents q ON q.company_run_id=c.id GROUP BY c.id
), rates AS (
 SELECT *, CASE WHEN files_downloaded+files_reused+files_failed > 0
   THEN 1.0*files_failed/(files_downloaded+files_reused+files_failed) ELSE 0 END AS failure_rate
 FROM counts
)
SELECT *, CASE WHEN files_pending>0 OR discovery_status IN ('failed','running') OR (status IN ('interrupted','queued') AND discovery_status='pending') OR
 (files_failed>0 AND failure_rate>=failure_threshold) THEN 1 ELSE 0 END AS retry_recommended
FROM rates;
CREATE VIEW IF NOT EXISTS ingestion_documents AS
SELECT * FROM documents WHERE selected_to_ingest=1;
