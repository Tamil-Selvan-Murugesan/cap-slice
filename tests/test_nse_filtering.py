"""Offline regression checks for announcement selection and curation."""
import json
import tempfile
import unittest
from datetime import date
from pathlib import Path
from unittest.mock import Mock, patch

from filings.nse import announcement_rows
from filings.curate import curated_rows
from filings.db import Database
from filings.nse_classification import classify_announcement


def filing(subject, filename, description=''):
    return dict(desc=subject, attchmntText=description,
                attchmntFile='https://nsearchives.nseindia.com/corporate/' + filename)


class SelectionTests(unittest.TestCase):
    def test_ambiguous_subjects(self):
        cases = [
            (filing('General Updates', 'ADISOFT_Investor_Presentation.pdf'), 'investor_presentation'),
            (filing('Outcome of Board Meeting', 'AELFinancialResults31032024.pdf'), 'financial_results'),
            (filing('Reply to Clarification- Financial results', 'Adisoft_Reply.pdf'), 'financial_results'),
            (filing('Analysts/Institutional Investor Meet/Con. Call Updates',
                    'IntimationofInstituitionaInvestorMeet.pdf', 'Call to discuss financial results'), 'announcement'),
            (filing('Trading Window', 'closure.pdf', 'Audited results'), 'announcement'),
            (filing('Updates', 'Credit_Rating_Rationale.pdf'), 'credit_rating'),
            (filing('Analysts/Institutional Investor Meet/Con. Call Updates', 'Transcript.pdf'), 'concall_transcript'),
        ]
        for row, expected in cases:
            with self.subTest(row=row):
                self.assertEqual(classify_announcement(row), expected)

    def test_selection_before_download_preserves_raw_metadata(self):
        rows = [filing('Updates', 'Investor_Presentation.pdf'), filing('Trading Window', 'closure.pdf')]
        with tempfile.TemporaryDirectory() as temp, patch('filings.nse.time.sleep'):
            with Database(Path(temp) / 'pipeline.sqlite3') as db:
                run = db.start_run('NSE', 'collect')
                company = db.start_company(run, 'NSE', 'NEWCO')
                session = Mock()
                session.get.return_value.json.return_value = rows
                session.record_response = lambda url, params, payload: db.record_response(company, url, params, payload)
                result = announcement_rows(session, 'NEWCO', date(2026, 1, 1), date(2026, 1, 2))
                self.assertEqual(len(result), 1)
                self.assertEqual(result[0]['kind'], 'investor_presentation')
                saved = db.conn.execute('SELECT payload_json FROM source_responses').fetchone()[0]
                self.assertEqual(json.loads(saved), rows)
                self.assertEqual(list(Path(temp).rglob('*.json')), [])

    def test_new_company_needs_no_review_entry(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp) / 'NEWCO'
            folder.mkdir()
            pdf = folder / 'presentation.pdf'
            pdf.write_bytes(b'%PDF-1.4 test fixture')
            row = dict(symbol='NEWCO', id='new', kind='announcement',
                       source='getCorporateAnnouncement', title='General Updates',
                       description='Investor presentation', url='https://nsearchives.nseindia.com/corporate/new.pdf',
                       file=str(pdf))
            with Database(Path(temp) / 'pipeline.sqlite3') as db:
                doc_id = db.upsert('NSE', 'NEWCO', row)
                db.save_file(doc_id, row, 'downloaded')
                docs, excluded = curated_rows(Path(temp), ['NEWCO'], db)
            self.assertEqual(len(docs), 1)
            self.assertEqual(docs[0]['kind'], 'investor_presentation')
            self.assertEqual(excluded, [])


if __name__ == '__main__':
    unittest.main()
