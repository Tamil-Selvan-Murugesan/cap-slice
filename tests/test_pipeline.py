import json
import tempfile
import unittest
from contextlib import contextmanager
from datetime import date
from pathlib import Path
from unittest.mock import patch

from filings.pipeline import process_document, run_collection
from filings.db import Database
from filings.curate import build


class Response:
    headers = {'Content-Type':'application/pdf'}
    def __init__(self, parts=None, error=None):
        self.parts = parts or [b'%PDF-1.4\n', b'valid content']
        self.error = error
    def __enter__(self):
        return self
    def __exit__(self,*args):
        pass
    def raise_for_status(self):
        if self.error:
            raise self.error
    def iter_content(self,*args):
        yield from self.parts


class Session:
    def __init__(self, responses):
        self.responses = iter(responses)
        self.calls = []
    def get(self,url,**kwargs):
        self.calls.append(url)
        result = next(self.responses)
        if isinstance(result,BaseException):
            raise result
        return result


class PipelineTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.folder = Path(self.temp.name)
        self.path = self.folder / 'pipeline.sqlite3'
    def tearDown(self):
        self.temp.cleanup()
    def row(self, ident='one', **kwargs):
        return dict(kind='financial_results',id=ident,date='2026-01-01',period='2025',
                    title='Financial results',source='AnnSubCategoryGetData',
                    url=f'https://www.bseindia.com/{ident}.pdf',**kwargs)
    def setup_document(self,db,row=None):
        run = db.start_run('BSE','collect')
        company = db.start_company(run,'BSE','500325')
        ident = db.upsert('BSE','500325',row or self.row(),run)
        db.enqueue(company,ident)
        return run,company,ident

    def test_success_failure_retry_and_reuse(self):
        with Database(self.path) as db:
            run,company,ident = self.setup_document(db)
            session = Session([Response(error=ValueError('HTTP 503'))])
            process_document(db,company,ident,session,self.folder)
            summary = db.conn.execute('SELECT * FROM company_run_summary').fetchone()
            self.assertEqual(summary['files_failed'],1)
            self.assertEqual(summary['retry_recommended'],1)
            db.finish_company(company); db.finish_run(run)
            second = db.start_run('BSE','retry')
            company2 = db.start_company(second,'BSE','500325')
            db.enqueue(company2,ident)
            process_document(db,company2,ident,Session([Response()]),self.folder)
            self.assertEqual(db.conn.execute('SELECT download_status FROM documents').fetchone()[0],'downloaded')
            third = db.start_run('BSE','collect')
            company3 = db.start_company(third,'BSE','500325'); db.enqueue(company3,ident)
            no_requests = Session([])
            process_document(db,company3,ident,no_requests,self.folder)
            self.assertEqual(no_requests.calls,[])
            self.assertEqual(db.conn.execute('SELECT outcome FROM run_documents WHERE company_run_id=?',(company3,)).fetchone()[0],'reused')
            self.assertEqual(db.conn.execute('SELECT COUNT(*) FROM download_attempts').fetchone()[0],2)

    def test_interrupted_file_and_hard_stop_recovery(self):
        def interrupted():
            yield b'%PDF-1.4\n'
            raise KeyboardInterrupt()
        with Database(self.path) as db:
            run,company,ident = self.setup_document(db)
            with self.assertRaises(KeyboardInterrupt):
                process_document(db,company,ident,Session([Response(parts=interrupted())]),self.folder)
            self.assertEqual(db.conn.execute('SELECT outcome FROM run_documents').fetchone()[0],'pending')
            # Simulate a hard stop between an attempt checkpoint and file write.
            db.begin_attempt(company,ident)
        with Database(self.path) as db:
            self.assertEqual(db.conn.execute('SELECT status FROM collection_runs').fetchone()[0],'interrupted')
            self.assertEqual(db.conn.execute('SELECT download_status FROM documents').fetchone()[0],'pending')
            self.assertFalse(list(self.folder.rglob('*.pdf')))
            self.assertFalse(list(self.folder.rglob('*.part')))
            run = db.start_run('BSE','retry'); company = db.start_company(run,'BSE','500325')
            db.enqueue(company,ident)
            process_document(db,company,ident,Session([Response()]),self.folder)
            self.assertEqual(db.conn.execute('SELECT download_status FROM documents').fetchone()[0],'downloaded')

    def test_fallback_and_invalid_pdf(self):
        with Database(self.path) as db:
            _,company,ident = self.setup_document(db,self.row(fallback_url='https://www.bseindia.com/live.pdf'))
            session = Session([Response(parts=[b'<html>error</html>']),Response()])
            process_document(db,company,ident,session,self.folder)
            self.assertEqual(len(session.calls),2)
            self.assertEqual(db.conn.execute('SELECT url_used FROM documents').fetchone()[0],'https://www.bseindia.com/live.pdf')

    def test_upsert_preserves_fields_and_is_repeatable(self):
        folder = self.folder/'500325'; folder.mkdir()
        pdf = folder/'report.pdf'; pdf.write_bytes(b'%PDF-1.4 sample')
        row = self.row(file=str(pdf),custom_unknown_field={'nested':[1,2]},subcategory='Results',url_used='https://example.test/used')
        with Database(self.path) as db:
            db.upsert('BSE','500325',row); db.upsert('BSE','500325',row)
            self.assertEqual(db.conn.execute('SELECT COUNT(*) FROM documents').fetchone()[0],1)
            record = db.conn.execute('SELECT * FROM documents').fetchone()
            self.assertEqual(json.loads(record['metadata_json']),row)
            self.assertIsNone(record['downloaded_at'])
            self.assertEqual(db.conn.execute('SELECT COUNT(*) FROM download_attempts').fetchone()[0],0)

    def test_curation_marks_duplicates_and_inactive_records(self):
        with Database(self.path) as db:
            for ident in ('first','second','inactive'):
                pdf = self.folder/(ident+'.pdf'); pdf.write_bytes(b'%PDF-1.4 duplicate')
                row = self.row(ident,file=str(pdf))
                doc = db.upsert('BSE','500325',row)
                db.save_file(doc,row,'archived' if ident=='inactive' else 'downloaded')
            build(self.folder,['500325'],550,db)
            records = db.conn.execute('SELECT selected_to_ingest,selection_reason FROM documents ORDER BY id').fetchall()
            self.assertEqual([r[0] for r in records],[1,0,0])
            self.assertEqual(records[1][1],'identical file content')
            self.assertEqual(records[2][1],'Not selected for ingestion')

    def test_orchestrator_retry_skips_success_and_discovery(self):
        rows = [self.row('good'), self.row('bad')]
        @contextmanager
        def initial_client(*args):
            session = Session([Response(),Response(error=ValueError('503'))])
            yield session,session
        with patch('filings.pipeline.exchange_client',initial_client), patch('filings.bse.discovery_sources',return_value=[('fixtures',lambda:iter(rows))]):
            first = run_collection('BSE',['500325'],self.folder,date(2020,1,1),date(2026,1,1),True)
        retry_session = Session([Response()])
        @contextmanager
        def retry_client(*args):
            yield retry_session,retry_session
        with patch('filings.pipeline.exchange_client',retry_client), patch('filings.bse.discovery_sources',side_effect=AssertionError('Retry must not discover')):
            run_collection('BSE',[],self.folder,date(2020,1,1),date(2026,1,1),True,mode='retry',retry_run=first)
        self.assertEqual(retry_session.calls,['https://www.bseindia.com/bad.pdf'])

    def test_interruption_keeps_unstarted_companies_visible(self):
        @contextmanager
        def client(*args):
            session = Session([KeyboardInterrupt()])
            yield session,session
        with patch('filings.pipeline.exchange_client',client), patch('filings.bse.discovery_sources',return_value=[('fixtures',lambda:iter([self.row()]))]):
            with self.assertRaises(KeyboardInterrupt):
                run_collection('BSE',['500325','540699'],self.folder,date(2020,1,1),date(2026,1,1),True)
        with Database(self.path) as db:
            records = db.conn.execute('SELECT symbol,status,retry_recommended FROM company_run_summary ORDER BY symbol').fetchall()
            self.assertEqual([tuple(r) for r in records],[('500325','interrupted',1),('540699','interrupted',1)])

    def test_crash_after_file_rename_does_not_redownload(self):
        from filings.pipeline import target_path
        with Database(self.path) as db:
            run,company,ident = self.setup_document(db)
            db.begin_attempt(company,ident)
            path = target_path(db.row(ident),self.folder)
            path.parent.mkdir(parents=True)
            path.write_bytes(b'%PDF-1.4 completed before crash')
        with Database(self.path) as db:
            run = db.start_run('BSE','retry'); company=db.start_company(run,'BSE','500325'); db.enqueue(company,ident)
            no_requests=Session([])
            process_document(db,company,ident,no_requests,self.folder)
            self.assertEqual(no_requests.calls,[])
            self.assertEqual(db.conn.execute('SELECT download_status FROM documents').fetchone()[0],'downloaded')

    def test_exclusive_writer_lock(self):
        with Database(self.path):
            with self.assertRaises(RuntimeError):
                Database(self.path)

class NSEDetailsTests(unittest.TestCase):
    setUp = PipelineTests.setUp
    tearDown = PipelineTests.tearDown
    row = PipelineTests.row
    def test_detail_sections_resume_and_attachment_is_reused(self):
        from filings.nse import prepare_details, SHAREHOLDING_SECTIONS
        details = self.folder / 'details.json'
        details.write_text(json.dumps({'declaration':{'cached':True}}))
        attachment = self.folder/'shares.xml'; attachment.write_text('<xbrl/>')
        row = dict(kind='shareholding',id='shares',date='2026-01-01',period='2025',
                   title='Shares',source='corporate-share-holdings-master',
                   url='https://nsearchives.nseindia.com/shares.xml',file=str(attachment),
                   detail_file=str(details),detail_request={'type':'shareholding','record_id':'shares'})
        with Database(self.path) as db:
            run = db.start_run('NSE','collect'); company = db.start_company(run,'NSE','TESTCO')
            ident = db.upsert('NSE','TESTCO',row,run); db.enqueue(company,ident)
            with patch('filings.nse.get_json',side_effect=[{'ok':True},ValueError('temporary failure')]):
                process_document(db,company,ident,Session([]),self.folder,prepare_details)
            self.assertEqual(set(json.loads(details.read_text())),{'declaration','summary'})
            run2 = db.start_run('NSE','retry'); company2 = db.start_company(run2,'NSE','TESTCO'); db.enqueue(company2,ident)
            with patch('filings.nse.get_json',return_value={'ok':True}) as request:
                process_document(db,company2,ident,Session([]),self.folder,prepare_details)
                self.assertEqual(request.call_count,len(SHAREHOLDING_SECTIONS)-2)
            self.assertEqual(db.conn.execute('SELECT download_status FROM documents').fetchone()[0],'downloaded')

    def test_discovery_failure_is_recorded_and_flagged(self):
        @contextmanager
        def client(*args):
            session = Session([])
            yield session,session
        def broken():
            raise ValueError('listing unavailable')
        with patch('filings.pipeline.exchange_client',client),patch('filings.bse.discovery_sources',return_value=[('annual',broken)]):
            run_collection('BSE',['500325'],self.folder,date(2020,1,1),date(2026,1,1),True)
        with Database(self.path) as db:
            summary = db.conn.execute('SELECT * FROM company_run_summary').fetchone()
            self.assertEqual(summary['retry_recommended'],1)
            self.assertEqual(summary['discovery_status'],'failed')
            self.assertEqual(summary['files_failed'],0)

    def test_threshold_boundary_and_zero_failures(self):
        with Database(self.path) as db:
            run = db.start_run('BSE','collect',threshold=0.1)
            company = db.start_company(run,'BSE','500325')
            db.discovery(company,'completed')
            for i in range(10):
                ident=db.upsert('BSE','500325',self.row(str(i)),run); db.enqueue(company,ident)
                db.outcome(company,ident,'failed' if i==0 else 'reused')
            record=db.conn.execute('SELECT * FROM company_run_summary').fetchone()
            self.assertAlmostEqual(record['failure_rate'],0.1)
            self.assertEqual(record['retry_recommended'],1)


if __name__=='__main__':
    unittest.main()
