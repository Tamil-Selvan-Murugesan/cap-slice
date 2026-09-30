"""Collect BSE filings with SQLite run history and resumable downloads.

Example: venv/bin/python -m filings.bse 543664 --download
"""

from __future__ import annotations

import argparse
import re
import time
from datetime import date, datetime, timedelta
from pathlib import Path
from urllib.parse import urljoin

from bse import BSE
from filings.pipeline import add_pipeline_arguments, run_collection


API = "https://api.bseindia.com/BseIndiaAPI/api"
SITE = "https://www.bseindia.com"


def years_ago(day: date, years: int) -> date:
    try:
        return day.replace(year=day.year - years)
    except ValueError:  # February 29
        return day.replace(year=day.year - years, day=28)


def year_windows(start: date, end: date):
    cursor = start
    while cursor <= end:
        stop = min(end, date(cursor.year, 12, 31))
        yield cursor, stop
        cursor = stop + timedelta(days=1)


def classify(row: dict) -> str | None:
    subject = " ".join(str(row.get(k) or "") for k in ("SUBCATNAME", "NEWSSUB", "HEADLINE")).lower()
    subcat = str(row.get("SUBCATNAME") or "").lower()
    if "transcript" in subject and any(x in subject for x in ("earnings", "concall", "conference call", "investor", "analyst")):
        return "concall_transcript"
    if "investor presentation" in subject or "analyst presentation" in subject:
        return "investor_presentation"
    if "credit rating" in subject or "rating action" in subject or "rating revision" in subject:
        return "credit_rating"
    if subcat == "financial results" or ("financial results" in subject and "intimation" not in subject):
        return "financial_results"
    return None


def request_json(bse: BSE, endpoint: str, code: str) -> dict:
    response = bse.session.get(f"{API}/{endpoint}/w", params={"scripcode": code}, timeout=30)
    response.raise_for_status()
    data = response.json()
    if not isinstance(data, dict):
        raise ValueError(f"Unexpected {endpoint} response for {code}: {type(data).__name__}")
    if hasattr(bse.session, 'record_response'):
        bse.session.record_response(endpoint, {"scripcode": code}, data)
    return data


def collect_announcements(bse: BSE, code: str, start: date, end: date):
    for first, last in year_windows(start, end):
        page = 1
        seen = 0
        while True:
            data = bse.announcements(
                page_no=page,
                from_date=datetime.combine(first, datetime.min.time()),
                to_date=datetime.combine(last, datetime.max.time()),
                scripcode=code,
            )
            if hasattr(bse.session, 'record_response'):
                bse.session.record_response('AnnSubCategoryGetData',
                    dict(scripcode=code, from_date=str(first), to_date=str(last), page=page), data)
            rows = data.get("Table") or []
            total = (data.get("Table1") or [{}])[0].get("ROWCNT", 0)
            for row in rows:
                kind = classify(row)
                attachment = row.get("ATTACHMENTNAME")
                if kind and attachment:
                    name = str(attachment).replace("\\", "/").rsplit("/", 1)[-1]
                    if not re.fullmatch(r"[\w.-]+\.(?:pdf|html?|xml)", name, re.I):
                        continue
                    yield {
                        "kind": kind, "source": "AnnSubCategoryGetData", "raw_metadata": row,
                        "id": str(row.get("NEWSID") or name),
                        "date": str(row.get("NEWS_DT") or row.get("DT_TM") or "")[:10],
                        "period": "",
                        "status": str(row.get("FILESTATUS") or "").strip(),
                        "title": str(row.get("NEWSSUB") or row.get("HEADLINE") or ""),
                        "subcategory": str(row.get("SUBCATNAME") or ""),
                        "url": f"{SITE}/xml-data/corpfiling/AttachHis/{name}",
                        "fallback_url": f"{SITE}/xml-data/corpfiling/AttachLive/{name}",
                    }
            seen += len(rows)
            if not rows or seen >= int(total):
                break
            page += 1
            time.sleep(0.25)


def collect_annual(bse: BSE, code: str, start: date):
    for row in request_json(bse, "AnnualReport_New", code).get("Table") or []:
        year = str(row.get("Year") or "")
        url = str(row.get("PDFDownload") or "").replace("\\", "")
        if year.isdigit() and int(year) >= start.year and url:
            yield {
                "kind": "annual_report", "source": "AnnualReport_New", "raw_metadata": row, "id": f"{year}-{row.get('status')}-{row.get('RN')}",
                "date": str(row.get("Fld_AuthoriseDate") or "")[:10],
                "period": year, "status": str(row.get("status") or ""),
                "title": f"Annual report FY ending {year}", "subcategory": "",
                "url": url, "fallback_url": "",
            }


def collect_shareholding(bse: BSE, code: str, start: date):
    for row in request_json(bse, "SHPQNewFormat", code).get("Table") or []:
        period = str(row.get("qtr") or "")
        try:
            period_date = datetime.strptime(period, "%B %Y").date()
        except ValueError:
            continue
        if period_date < start:
            continue
        rel_url = str(row.get("xbrlurl") or "").replace("\\", "/")
        if not rel_url:
            continue
        yield {
            "kind": "shareholding", "source": "SHPQNewFormat", "raw_metadata": row, "id": str(row.get("XbrlFile") or row.get("qtrid")),
            "date": str(row.get("revised_date_time") or row.get("filing_date_time") or "")[:10],
            "period": period, "status": str(row.get("status") or ""),
            "title": f"Shareholding pattern {period}", "subcategory": "",
            "url": urljoin(SITE, rel_url), "fallback_url": "",
        }


def discovery_sources(bse, code, start, end, folder):
    def snapshot():
        data = {"SlbReportNewbeta": request_json(bse, "SlbReportNewbeta", code),
                "resultsSnapshot": bse.resultsSnapshot(code),
                "retrieved_at": datetime.now().isoformat()}
        bse.session.record_response('resultsSnapshot', {"scripcode": code}, data)
        return []
    return [
        ("results snapshot", snapshot),
        ("annual reports", lambda: collect_annual(bse, code, start)),
        ("shareholding", lambda: collect_shareholding(bse, code, start)),
        ("announcements", lambda: collect_announcements(bse, code, start, end)),
    ]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("scripcodes", nargs="*", help="BSE scrip codes, e.g. 543664")
    parser.add_argument("--output", type=Path, default=Path("data"))
    parser.add_argument("--years", type=int, default=10)
    parser.add_argument("--download", action="store_true", help="Download documents; otherwise discover and checkpoint metadata only")
    add_pipeline_arguments(parser)
    args = parser.parse_args()
    if args.years < 1 or any(not re.fullmatch(r"\d{6}", code) for code in args.scripcodes):
        parser.error("Use --years >= 1 and six-digit BSE scrip codes")
    if not 0 <= args.failure_threshold <= 1:
        parser.error("--failure-threshold must be between 0 and 1")
    retry = args.retry_failed or bool(args.retry_run)
    if not args.scripcodes and not retry:
        parser.error("Specify at least one BSE scrip code")
    today = date.today()
    run_collection('BSE', args.scripcodes, args.output, years_ago(today, args.years), today,
                   args.download or retry, args.db, 'retry' if retry else 'collect',
                   args.failure_threshold, args.retry_run)


if __name__ == "__main__":
    main()
