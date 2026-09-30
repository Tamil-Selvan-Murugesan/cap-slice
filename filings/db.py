"""SQLite state and short, durable checkpoints shared by both collectors."""
from __future__ import annotations

import fcntl
import hashlib
import json
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path



def now():
    return datetime.now(timezone.utc).isoformat(timespec='seconds')


def encode(value):
    return json.dumps(value, ensure_ascii=False, default=str)


def file_digest(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


class Database:
    """One writer command per database; readers can use SQLite concurrently."""
    def __init__(self, path):
        self.path = Path(path).resolve()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.lock = self.path.with_suffix(self.path.suffix + '.lock').open('a')
        try:
            fcntl.flock(self.lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            self.lock.close()
            raise RuntimeError(f'Another pipeline writer is using {self.path}') from None
        self.conn = sqlite3.connect(self.path, timeout=30)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute('PRAGMA journal_mode=WAL')
        self.conn.execute('PRAGMA foreign_keys=ON')
        self.conn.executescript(Path(__file__).with_name('schema.sql').read_text())
        self.recover_interrupted()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.conn.close()
        self.lock.close()

    def recover_interrupted(self):
        # The exclusive process lock proves any previous running writer is gone.
        with self.conn:
            self.conn.execute("UPDATE download_attempts SET status='interrupted', finished_at=?, error='Writer stopped before checkpoint' WHERE status='downloading'", (now(),))
            self.conn.execute("UPDATE documents SET download_status='pending' WHERE download_status='downloading'")
            self.conn.execute("UPDATE company_runs SET status='interrupted', finished_at=? WHERE status IN ('running','queued')", (now(),))
            self.conn.execute("UPDATE collection_runs SET status='interrupted', finished_at=? WHERE status='running'", (now(),))

    def start_run(self, exchange, mode, threshold=0.05, options=None):
        run_id = str(uuid.uuid4())
        with self.conn:
            self.conn.execute('INSERT INTO collection_runs VALUES (?,?,?,?,?,?,?,?,?)',
                              (run_id, mode, exchange, now(), None, 'running', threshold, encode(options or {}), None))
        return run_id

    def start_company(self, run_id, exchange, symbol, queued=False):
        with self.conn:
            return self.conn.execute('INSERT INTO company_runs(run_id,exchange,symbol,started_at,status) VALUES (?,?,?,?,?)',
                                     (run_id, exchange, symbol, now(), 'queued' if queued else 'running')).lastrowid

    def finish_company(self, company_id, interrupted=False):
        row = self.conn.execute('SELECT * FROM company_run_summary WHERE id=?', (company_id,)).fetchone()
        status = 'interrupted' if interrupted else 'completed_with_errors' if row['files_failed'] or row['discovery_status']=='failed' else 'completed'
        with self.conn:
            self.conn.execute('UPDATE company_runs SET status=?,finished_at=? WHERE id=?', (status, now(), company_id))

    def finish_run(self, run_id, interrupted=False, error=None):
        bad = self.conn.execute("SELECT 1 FROM company_runs WHERE run_id=? AND status!='completed' LIMIT 1", (run_id,)).fetchone()
        status = 'interrupted' if interrupted else 'completed_with_errors' if bad or error else 'completed'
        with self.conn:
            if interrupted:
                self.conn.execute("UPDATE company_runs SET status='interrupted',finished_at=? WHERE run_id=? AND status IN ('running','queued')", (now(),run_id))
            self.conn.execute('UPDATE collection_runs SET status=?,finished_at=?,error=? WHERE run_id=?', (status, now(), error, run_id))

    def discovery(self, company_id, status, error=None):
        row = self.conn.execute('SELECT discovery_errors_json FROM company_runs WHERE id=?', (company_id,)).fetchone()
        errors = json.loads(row[0])
        if error:
            errors.append(str(error))
        with self.conn:
            self.conn.execute('UPDATE company_runs SET discovery_status=?,discovery_errors_json=? WHERE id=?',
                              ('failed' if errors else status, encode(errors), company_id))

    def record_response(self, company_id, endpoint, params, payload):
        with self.conn:
            self.conn.execute('INSERT INTO source_responses(company_run_id,endpoint,parameters_json,payload_json,recorded_at) VALUES (?,?,?,?,?)',
                              (company_id, endpoint, encode(params), encode(payload), now()))

    def upsert(self, exchange, symbol, row, run_id=None):
        """Preserve every input field, with explicit columns for common queries."""
        row = dict(row)
        source = row.get('source') or {'annual_report':'AnnualReport_New', 'shareholding':'SHPQNewFormat'}.get(row['kind'], 'AnnSubCategoryGetData')
        key = (exchange, symbol, source, str(row['id']), row.get('url') or '')
        old = self.conn.execute('SELECT * FROM documents WHERE exchange=? AND symbol=? AND source=? AND source_id=? AND source_url=?', key).fetchone()
        metadata = json.loads(old['metadata_json']) if old else {}
        metadata.update(row)
        raw = row.get('raw_metadata') or (json.loads(old['raw_metadata_json']) if old else {})
        values = dict(exchange=exchange, symbol=symbol, source=source, source_id=str(row['id']), source_url=key[-1],
                      kind=row['kind'], title=row.get('title') or '', description=row.get('description') or '',
                      subcategory=row.get('subcategory') or '', filing_date=row.get('date') or '',
                      reporting_period=row.get('period') or '', filing_status=row.get('status') or '',
                      fallback_url=row.get('fallback_url') or '', metadata_json=encode(metadata), raw_metadata_json=encode(raw),
                      updated_at=now(), last_seen_run_id=run_id)
        with self.conn:
            if old:
                if row.get('detail_file') and not old['detail_path']:
                    values['detail_path'] = row['detail_file']
                if any(old[k] != values[k] for k in ('kind','title','description','filing_date','reporting_period','filing_status','raw_metadata_json')):
                    values.update(selected_to_ingest=0, selection_reason='Metadata changed; awaiting curation')
                    self.conn.execute('DELETE FROM document_chunks WHERE document_id=?', (old['id'],))
                self.conn.execute('UPDATE documents SET '+','.join(f'{k}=?' for k in values)+' WHERE id=?', (*values.values(), old['id']))
                return old['id']
            values.update(first_seen_at=now(), first_seen_run_id=run_id,
                          file_path=row.get('file'), detail_path=row.get('detail_file'), sha256=row.get('sha256'))
            if not key[-1] and not row.get('detail_file'):
                values.update(download_status='unavailable', last_error='No usable source URL')
            return self.conn.execute('INSERT INTO documents('+','.join(values)+') VALUES ('+','.join('?' for _ in values)+')', tuple(values.values())).lastrowid

    def row(self, document_id):
        item = self.conn.execute('SELECT * FROM documents WHERE id=?', (document_id,)).fetchone()
        row = json.loads(item['metadata_json'])
        row.update(symbol=item['symbol'], exchange=item['exchange'], source=item['source'], id=item['source_id'],
                   kind=item['kind'], title=item['title'], description=item['description'], url=item['source_url'],
                   file=item['file_path'], detail_file=item['detail_path'], sha256=item['sha256'],
                   url_used=item['url_used'], content_type=item['content_type'],
                   _db_id=item['id'], _download_status=item['download_status'], raw_metadata=json.loads(item['raw_metadata_json']))
        row.pop('error', None)
        if item['download_status'] in ('pending','downloading','failed','unavailable'):
            row['error'] = item['last_error'] or item['download_status']
        return row

    def enqueue(self, company_id, document_id):
        with self.conn:
            self.conn.execute('INSERT OR IGNORE INTO run_documents(company_run_id,document_id) VALUES (?,?)', (company_id, document_id))

    def outcome(self, company_id, document_id, outcome):
        with self.conn:
            self.conn.execute('UPDATE run_documents SET outcome=? WHERE company_run_id=? AND document_id=?', (outcome, company_id, document_id))

    def _save_file(self, document_id, row, status, error=None):
        path = Path(row['file']) if row.get('file') else None
        self.conn.execute('''UPDATE documents SET file_path=?,detail_path=?,sha256=?,byte_size=?,
            content_type=?,url_used=?,download_status=?,last_error=?,updated_at=?,
            selected_to_ingest=0,selection_reason='Awaiting curation' WHERE id=?''',
            (str(path) if path else None,row.get('detail_file'),row.get('sha256'),
             path.stat().st_size if path and path.is_file() else None,row.get('content_type'),row.get('url_used'),
             status,error,now(),document_id))
        self.conn.execute('DELETE FROM document_chunks WHERE document_id=?', (document_id,))

    def save_file(self, document_id, row, status, error=None):
        with self.conn:
            self._save_file(document_id,row,status,error)

    def complete_download(self, company_id, document_id, attempt_id, row, outcome, error=None):
        # Document, attempt and run counter move together in one commit.
        with self.conn:
            self._save_file(document_id,row,'failed' if error else 'downloaded',error)
            if outcome=='downloaded' and not error:
                self.conn.execute('UPDATE documents SET downloaded_at=? WHERE id=?', (now(),document_id))
            if attempt_id:
                record = self.conn.execute('SELECT byte_size FROM documents WHERE id=?',(document_id,)).fetchone()
                self.conn.execute('UPDATE download_attempts SET finished_at=?,status=?,error=?,url_used=?,byte_size=?,sha256=? WHERE id=?',
                    (now(),'failed' if error else 'completed',error,row.get('url_used'),record[0],row.get('sha256'),attempt_id))
            self.conn.execute('UPDATE run_documents SET outcome=? WHERE company_run_id=? AND document_id=?',
                              (outcome,company_id,document_id))

    def begin_attempt(self, company_id, document_id):
        with self.conn:
            self.conn.execute("UPDATE documents SET download_status='downloading',last_error=NULL,selected_to_ingest=0,selection_reason='Download in progress' WHERE id=?", (document_id,))
            self.conn.execute('DELETE FROM document_chunks WHERE document_id=?', (document_id,))
            return self.conn.execute("INSERT INTO download_attempts(company_run_id,document_id,started_at,status) VALUES (?,?,?,'downloading')", (company_id,document_id,now())).lastrowid

    def end_attempt(self, attempt_id, row, status, error=None):
        path = Path(row['file']) if row.get('file') else None
        with self.conn:
            self.conn.execute('UPDATE download_attempts SET finished_at=?,status=?,error=?,url_used=?,byte_size=?,sha256=? WHERE id=?',
                              (now(),status,error,row.get('url_used'),path.stat().st_size if path and path.is_file() else None,row.get('sha256'),attempt_id))

    def symbols(self, exchange=None):
        sql = 'SELECT DISTINCT exchange,symbol FROM documents'
        return [tuple(r) for r in self.conn.execute(sql+(' WHERE exchange=?' if exchange else '')+' ORDER BY exchange,symbol', (exchange,) if exchange else ())]
