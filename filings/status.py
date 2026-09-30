"""Read collection history or the current failed-file queue without changing state."""
import argparse
import sqlite3
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--db',type=Path,default=Path('data/pipeline.sqlite3'))
    parser.add_argument('--run',help='Show companies for a specific run UUID')
    parser.add_argument('--failures',action='store_true',help='Show current failed/unavailable documents')
    args = parser.parse_args()
    if not args.db.is_file():
        parser.error('Database not found; run a collector first')
    with sqlite3.connect(args.db.resolve().as_uri()+'?mode=ro',uri=True) as conn:
        conn.row_factory = sqlite3.Row
        if args.failures:
            query = "SELECT id,exchange,symbol,source_id,download_status,last_error FROM documents WHERE download_status IN ('failed','unavailable') ORDER BY exchange,symbol,id"
            rows = conn.execute(query).fetchall()
        elif args.run:
            rows = conn.execute('''SELECT exchange,symbol,status,discovery_status,files_planned,
                files_downloaded,files_reused,files_failed,files_pending,files_deferred,
                ROUND(failure_rate*100,2) AS failure_percent,retry_recommended,discovery_errors_json
                FROM company_run_summary WHERE run_id=? ORDER BY symbol''',(args.run,)).fetchall()
        else:
            rows = conn.execute('SELECT run_id,mode,exchange,started_at,finished_at,status,error FROM collection_runs ORDER BY started_at DESC, rowid DESC LIMIT 20').fetchall()
        if not rows:
            print('No matching records.')
            return
        print('\t'.join(rows[0].keys()))
        for row in rows:
            print('\t'.join(str(v) if v is not None else '' for v in row))


if __name__=='__main__':
    main()
