"""Common download queue, checkpoints and bounded retry runs."""
from __future__ import annotations

import hashlib
import importlib
import json
import re
import time
from contextlib import contextmanager
from pathlib import Path
from urllib.parse import urlparse

from filings.db import Database, file_digest, now


def atomic_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + '.part')
    temporary.write_text(json.dumps(value, indent=2))
    temporary.replace(path)


def target_path(row, folder):
    suffix = Path(urlparse(row.get('url') or '').path).suffix.lower()
    if suffix not in ('.pdf','.html','.htm','.xml','.zip','.xlsx','.xls'):
        suffix = '.bin'
    # Match legacy filenames so existing successful files remain reusable.
    limit = 100 if row['exchange']=='BSE' else 130
    name = re.sub(r'[^a-zA-Z0-9_.-]+', '_', f"{row.get('date') or row.get('period') or ''}_{row['id']}").strip('._')[:limit] or 'filing'
    return Path(folder) / row['kind'] / (name + suffix)


def valid_file(path, expected_hash=None):
    path = Path(path) if path else None
    if not path or not path.is_file() or not path.stat().st_size:
        return False
    with path.open('rb') as stream:
        first = stream.read(1000)
    if path.suffix.lower()=='.pdf' and not first.lstrip().startswith(b'%PDF'):
        return False
    if path.suffix.lower() in ('.xml','.html','.htm') and b'<' not in first:
        return False
    if path.suffix.lower()=='.zip' and not first.startswith(b'PK'):
        return False
    return not expected_hash or file_digest(path)==expected_hash


def download_file(session, row, folder):
    """Atomic file replacement; a stopped download leaves only a .part file."""
    target = Path(row['file']) if row.get('file') else target_path(row, folder)
    row['file'] = str(target)
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_name(target.name + '.part')
    errors = []
    for url in dict.fromkeys(filter(None, (row.get('url'), row.get('fallback_url')))):
        try:
            if row['exchange']=='NSE':
                from filings.nse import valid_url
                if not valid_url(url):
                    raise ValueError('Source URL is not an allowed NSE URL')
            with session.get(url, stream=True, timeout=90) as response:
                response.raise_for_status()
                digest = hashlib.sha256()
                with temporary.open('wb') as output:
                    for chunk in response.iter_content(65536):
                        if chunk:
                            output.write(chunk)
                            digest.update(chunk)
                # Validate with the actual extension, before publishing the file.
                with temporary.open('rb') as stream:
                    first = stream.read(1000)
                suffix = target.suffix.lower()
                if not first:
                    raise ValueError('Empty document')
                if suffix=='.pdf' and not first.lstrip().startswith(b'%PDF'):
                    raise ValueError('Response is not a PDF')
                if suffix in ('.xml','.html','.htm') and b'<' not in first:
                    raise ValueError('Response is not XML/HTML')
                if suffix=='.zip' and not first.startswith(b'PK'):
                    raise ValueError('Response is not a ZIP')
                temporary.replace(target)
                row.update(sha256=digest.hexdigest(),url_used=url,content_type=response.headers.get('Content-Type'))
                return
        except Exception as exc:
            errors.append(f'{url}: {exc}')
        finally:
            temporary.unlink(missing_ok=True)
            time.sleep(0.2)
    raise ValueError('; '.join(errors) or 'No usable source URL')


@contextmanager
def exchange_client(exchange, folder):
    if exchange=='NSE':
        from filings.nse import session
        with session() as client:
            yield client, client
    else:
        from bse import BSE
        from requests.adapters import HTTPAdapter
        from urllib3.util.retry import Retry
        with BSE(folder) as client:
            client.session.mount('https://', HTTPAdapter(max_retries=Retry(total=3,backoff_factor=1,status_forcelist=(429,500,502,503,504))))
            yield client, client.session


def process_document(db, company_id, document_id, session, folder, prepare=None, add_extra=None):
    row = db.row(document_id)
    row.pop('error', None)
    if not row.get('file') and row.get('url'):
        row['file'] = str(target_path(row, folder))
    reusable = valid_file(row.get('file'), row.get('sha256'))
    # Prepare also uses cached detail JSON, and can discover a notes attachment.
    needs_detail = bool(row.get('detail_request'))
    attempt = None
    try:
        if not reusable or needs_detail:
            attempt = db.begin_attempt(company_id, document_id)
        if prepare:
            for extra in prepare(session, row, folder):
                if add_extra:
                    add_extra(extra)
        fetched = False
        if row.get('url') and not reusable:
            download_file(session, row, folder)
            fetched = True
        elif reusable:
            row['sha256'] = file_digest(row['file'])
        elif not row.get('detail_file') or not Path(row['detail_file']).is_file():
            raise ValueError('No usable source URL or detail file')
        if not row.get('url') and row.get('detail_file'):
            # A structured-only source is complete after its JSON is available.
            row['file'] = row['detail_file']
            row['sha256'] = file_digest(row['file'])
        outcome = 'downloaded' if fetched or row.pop('_details_fetched',False) else 'reused'
        db.complete_download(company_id,document_id,attempt,row,outcome)
    except Exception as exc:
        if attempt is None:
            attempt = db.begin_attempt(company_id,document_id)
        db.complete_download(company_id,document_id,attempt,row,'failed',str(exc))
    except BaseException:
        # A complete file may already exist if interruption occurred after rename.
        # Next run checks/reuses it; no successful file is deleted here.
        if attempt:
            db.end_attempt(attempt,row,'interrupted','Command interrupted')
        with db.conn:
            db.conn.execute("UPDATE documents SET download_status='pending' WHERE id=?", (document_id,))
        raise


def download_candidate(row):
    if row.get('_download_status') == 'archived':
        return False
    kind = row['kind']
    if row.get('source')=='getCorporateAnnouncement':
        from filings.nse_classification import classify_announcement
        kind = classify_announcement(row.get('raw_metadata') or {
            'desc':row.get('title'),'attchmntText':row.get('description'),'attchmntFile':row.get('url')})
    return kind in {'annual_report','shareholding','financial_results','concall_transcript','investor_presentation','credit_rating'}


def run_collection(exchange, symbols, folder, start, end, get_files, db_path=None,
                   mode='collect', threshold=0.05, retry_run=None):
    folder = Path(folder).resolve()
    folder.mkdir(parents=True, exist_ok=True)
    adapter = importlib.import_module('filings.' + exchange.lower())
    with Database(db_path or folder / 'pipeline.sqlite3') as db:
        rediscover = set()
        if retry_run:
            rediscover = {r['symbol'] for r in db.conn.execute("SELECT symbol FROM company_run_summary WHERE run_id=? AND exchange=? AND discovery_status IN ('pending','running','failed')", (retry_run,exchange))}
            symbols = [r['symbol'] for r in db.conn.execute('SELECT symbol FROM company_run_summary WHERE run_id=? AND exchange=? AND retry_recommended=1', (retry_run,exchange))]
            if not symbols:
                raise ValueError('No companies flagged for this run and exchange')
        elif not symbols:
            symbols = [symbol for _,symbol in db.symbols(exchange)]
        if not symbols:
            raise ValueError('No companies selected; run collection first')
        run_id = db.start_run(exchange,mode,threshold,dict(symbols=symbols,start=str(start),end=str(end),download=get_files,retry_run=retry_run))
        print(f'Run {run_id} | {exchange} | {mode}', flush=True)
        companies = {symbol:db.start_company(run_id,exchange,symbol,queued=True) for symbol in dict.fromkeys(symbols)}
        active_company = None
        try:
            for symbol in dict.fromkeys(symbols):
                active_company = companies[symbol]
                company_id = active_company
                with db.conn:
                    db.conn.execute("UPDATE company_runs SET status='running',started_at=? WHERE id=?", (now(),company_id))
                company_folder = folder / symbol
                company_folder.mkdir(parents=True,exist_ok=True)
                def register(row):
                    doc_id = db.upsert(exchange,symbol,row,run_id)
                    db.enqueue(company_id,doc_id)
                company_mode = 'collect' if symbol in rediscover else mode
                try:
                    # Retry uses only the durable queue, without repeating discovery.
                    if company_mode=='retry':
                        db.discovery(company_id,'not_requested')
                        for item in db.conn.execute("SELECT id FROM documents WHERE exchange=? AND symbol=? AND download_status IN ('pending','failed','unavailable')", (exchange,symbol)).fetchall():
                            if download_candidate(db.row(item['id'])):
                                db.enqueue(company_id,item['id'])
                    with exchange_client(exchange,folder) as (client,http):
                        http.record_response = lambda endpoint,params,payload: db.record_response(company_id,endpoint,params,payload)
                        if company_mode=='collect':
                            db.discovery(company_id,'running')
                            for label, discover in adapter.discovery_sources(client,symbol,start,end,company_folder):
                                try:
                                    for row in discover():
                                        register(row)
                                except Exception as exc:
                                    db.discovery(company_id,'failed',f'{label}: {exc}')
                            db.discovery(company_id,'completed')
                            # Previously failed/pending records may be absent from a new listing.
                            for item in db.conn.execute("SELECT id FROM documents WHERE exchange=? AND symbol=? AND download_status IN ('pending','failed','unavailable')", (exchange,symbol)).fetchall():
                                if download_candidate(db.row(item['id'])):
                                    db.enqueue(company_id,item['id'])
                        while True:
                            item = db.conn.execute("SELECT document_id FROM run_documents WHERE company_run_id=? AND outcome='pending' ORDER BY document_id LIMIT 1", (company_id,)).fetchone()
                            if not item:
                                break
                            if not get_files:
                                db.outcome(company_id,item[0],'deferred')
                                continue
                            process_document(db,company_id,item[0],http,company_folder,
                                             getattr(adapter,'prepare_details',None),register)
                except Exception as exc:
                    db.discovery(company_id,'failed',str(exc))
                db.finish_company(company_id)
                summary = dict(db.conn.execute('SELECT * FROM company_run_summary WHERE id=?', (company_id,)).fetchone())
                print(f"{symbol}: {summary['files_downloaded']} downloaded, {summary['files_reused']} reused, {summary['files_failed']} failed, {summary['files_pending']} pending; retry={bool(summary['retry_recommended'])}", flush=True)
                active_company = None
        except BaseException as exc:
            if active_company:
                db.finish_company(active_company,interrupted=True)
            db.finish_run(run_id,interrupted=True,error=str(exc) or type(exc).__name__)
            raise
        try:
            from filings.curate import build
            build(folder, symbols, 550, db)
        except Exception as exc:
            db.finish_run(run_id,error=f'Curation failed: {exc}')
            raise
        db.finish_run(run_id)
        return run_id


def add_pipeline_arguments(parser):
    parser.add_argument('--db',type=Path,help='SQLite path (default: OUTPUT/pipeline.sqlite3)')
    parser.add_argument('--retry-failed',action='store_true',help='Retry failed/pending files from SQLite without discovery')
    parser.add_argument('--retry-run',help='Retry files for companies flagged in a previous run')
    parser.add_argument('--failure-threshold',type=float,default=0.05,help='Failure fraction that flags a retry (default 0.05)')
