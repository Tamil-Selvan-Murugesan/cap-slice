"""Collect NSE Emerge filings and attachments for one or more SME symbols."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import time
from datetime import date, datetime, timedelta
from pathlib import Path
from urllib.parse import urlparse

from filings.nse_classification import classify_announcement
from filings.pipeline import add_pipeline_arguments, run_collection, atomic_json

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

BASE = "https://www.nseindia.com"
QUOTE_API = BASE + "/api/NextApi/apiClient/GetQuoteApi"
ALLOWED_HOSTS = {"nsearchives.nseindia.com", "archives.nseindia.com", "www.nseindia.com"}
SHAREHOLDING_SECTIONS = (
    "declaration", "summary", "promoter", "public-shareholder",
    "non-public-shareholder", "beneficial-owners", "clarifications",
    "foreign-ownership-limits",
)
def years_ago(day: date, years: int) -> date:
    try:
        return day.replace(year=day.year - years)
    except ValueError:
        return day.replace(year=day.year - years, day=28)


def windows(start: date, end: date):
    cursor = start
    while cursor <= end:
        stop = min(cursor + timedelta(days=179), end)
        yield cursor, stop
        cursor = stop + timedelta(days=1)


def iso_date(value: object) -> str:
    value = str(value or "").strip()
    for fmt in ("%Y-%m-%d %H:%M:%S", "%d-%b-%Y %H:%M:%S", "%d-%b-%Y", "%d-%B-%Y"):
        try:
            return datetime.strptime(value[:len(datetime.now().strftime(fmt))], fmt).date().isoformat()
        except ValueError:
            pass
    return value[:10] if re.fullmatch(r"\d{4}-\d{2}-\d{2}.*", value) else ""


def safe_name(value: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_.-]+", "_", value).strip("._")[:130] or "filing"


def session() -> requests.Session:
    s = requests.Session()
    s.headers.update({
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/131.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": BASE + "/companies-listing/corporate-filings-announcements",
    })
    retry = Retry(total=3, backoff_factor=1, status_forcelist=(429, 500, 502, 503, 504))
    s.mount("https://", HTTPAdapter(max_retries=retry))
    warm = s.get(BASE + "/companies-listing/corporate-filings-announcements", timeout=30)
    warm.raise_for_status()
    return s


def get_json(s: requests.Session, path: str, params: dict) -> object:
    url = QUOTE_API if path == "quote" else BASE + "/api/" + path
    response = s.get(url, params=params, timeout=35)
    response.raise_for_status()
    data = response.json()
    if hasattr(s, 'record_response'):
        s.record_response(url, params, data)
    time.sleep(0.2)
    return data


def write_json(path: Path, data: object) -> None:
    atomic_json(path, data)


def valid_url(value: object) -> str:
    url = str(value or "").strip()
    parsed = urlparse(url)
    if parsed.scheme == "https" and parsed.hostname in ALLOWED_HOSTS and not parsed.path.endswith("/-"):
        return url
    return ""


def announcement_rows(s: requests.Session, symbol: str, start: date, end: date) -> list[dict]:
    found = {}
    for first, last in windows(start, end):
        result = get_json(s, "quote", {
            "functionName": "getCorporateAnnouncement",
            "symbol": symbol, "marketApiType": "sme", "subject": "",
            "fromDate": first.strftime("%d-%m-%Y"),
            "toDate": last.strftime("%d-%m-%Y"),
        })
        if not isinstance(result, list):
            raise ValueError(f"Unexpected announcement response for {symbol}")
        for item in result:
            identifier = str(item.get("seq_id") or item.get("attchmntFile") or "")
            if identifier:
                found[identifier] = item
    rows = []
    for item in found.values():
        kind = classify_announcement(item)
        if kind == "announcement":
            continue
        url = valid_url(item.get("attchmntFile"))
        rows.append({
            "exchange": "NSE", "symbol": symbol, "kind": kind, "raw_metadata": item,
            "id": str(item.get("seq_id") or hashlib.sha256(url.encode()).hexdigest()[:16]),
            "date": iso_date(item.get("sort_date") or item.get("dt")),
            "period": "", "status": "", "title": str(item.get("desc") or ""),
            "description": str(item.get("attchmntText") or ""),
            "source": "getCorporateAnnouncement", "url": url,
        })
    return rows


def annual_rows(s: requests.Session, symbol: str, start: date) -> list[dict]:
    result = get_json(s, "quote", {
        "functionName": "getCorpAnnualReport", "symbol": symbol, "marketApiType": "sme",
    })
    if not isinstance(result, list):
        raise ValueError(f"Unexpected annual report response for {symbol}")
    rows = []
    for item in result:
        year = str(item.get("toYr") or "")
        url = valid_url(item.get("fileName"))
        if year.isdigit() and int(year) >= start.year and url:
            rows.append({
                "exchange": "NSE", "symbol": symbol, "kind": "annual_report", "raw_metadata": item,
                "id": Path(urlparse(url).path).stem,
                "date": iso_date(item.get("anReportCreateDate")),
                "period": year, "status": str(item.get("submission_type") or ""),
                "title": f"Annual report FY ending {year}",
                "source": "getCorpAnnualReport", "url": url,
            })
    return rows


def shareholding_rows(s: requests.Session, symbol: str, start: date, folder: Path) -> list[dict]:
    get_json(s, "quote", {
        "functionName": "getShareHoldingPatternCorp", "symbol": symbol,
        "type": "W", "noOfRecords": "100",
    })
    filings = get_json(s, "corporate-share-holdings-master", {"index": "sme", "symbol": symbol})
    if not isinstance(filings, list):
        raise ValueError(f"Unexpected full shareholding response for {symbol}")
    rows = []
    for item in filings:
        period = iso_date(item.get("date"))
        if not period or period < start.isoformat():
            continue
        identifier = str(item.get("recordId") or "")
        detail_path = folder / "shareholding" / (safe_name(identifier) + "_details.json")
        rows.append({
            "exchange": "NSE", "symbol": symbol, "kind": "shareholding",
            "id": identifier, "date": iso_date(item.get("submissionDate")),
            "period": period, "status": str(item.get("revisedStatus") or ""),
            "title": f"Shareholding pattern {period}", "source": "corporate-share-holdings-master",
            "url": valid_url(item.get("xbrl")), "detail_file": str(detail_path),
            "raw_metadata": item,
            "detail_request": {"type": "shareholding", "record_id": identifier},
        })
    return rows


def financial_rows(s: requests.Session, symbol: str, start: date, folder: Path):
    get_json(s, "quote", {
        "functionName": "getFinancialResultData", "symbol": symbol,
        "marketApiType": "sme", "noOfRecords": "100",
    })
    legacy = get_json(s, "corporates-financial-results", {"index": "sme", "symbol": symbol})
    if not isinstance(legacy, list):
        raise ValueError(f"Unexpected legacy results response for {symbol}")
    for item in legacy:
        filing_date = iso_date(item.get("filingDate"))
        if filing_date and filing_date < start.isoformat():
            continue
        identifier = str(item.get("seqNumber") or item.get("params") or "")
        params = {
            "index": "sme", "symbol": symbol, "audited": item.get("audited"),
            "relatingTo": item.get("relatingTo"), "from_date": item.get("fromDate"),
            "to_date": item.get("toDate"), "bank": item.get("bank"),
            "cumulative": item.get("cumulative"), "consolidated": item.get("consolidated"),
            "indas": item.get("indAs"), "timestamp": item.get("params"),
            "seqNumber": identifier,
        }
        detail_path = folder / "financial_results" / (safe_name(identifier) + "_details.json")
        # Detail fetch is a checkpointed queue task, so an API failure can be retried.
        yield {
            "exchange": "NSE", "symbol": symbol, "kind": "financial_results",
            "id": identifier + "-xbrl", "date": filing_date,
            "period": str(item.get("period") or item.get("toDate") or ""),
            "status": str(item.get("audited") or ""),
            "title": f"Financial results {item.get('period') or ''} (xbrl)",
            "source": "corporates-financial-results", "url": valid_url(item.get("xbrl")),
            "detail_file": str(detail_path), "raw_metadata": item,
            "detail_request": {"type": "financial_results", "params": params},
        }
    page = 1
    integrated = []
    while True:
        result = get_json(s, "integrated-filing-results", {
            "index": "sme", "symbol": symbol, "page": page, "size": 100,
        })
        if not isinstance(result, dict) or not isinstance(result.get("data"), list):
            raise ValueError(f"Unexpected integrated filing response for {symbol}")
        batch = result["data"]
        integrated.extend(batch)
        if len(batch) < 100:
            break
        page += 1
    for item in integrated:
        if "financial" not in str(item.get("type") or "").lower():
            continue
        period = iso_date(item.get("qe_Date"))
        if period and period < start.isoformat():
            continue
        identifier = str(item.get("seq_Id") or "")
        for label, key in (("xbrl", "xbrl"), ("ixbrl", "ixbrl"), ("pdf", "pdf_attach")):
            url = valid_url(item.get(key))
            if url:
                yield {
                    "exchange": "NSE", "symbol": symbol, "kind": "financial_results",
                    "id": identifier + "-" + label,
                    "date": iso_date(item.get("creation_Date") or item.get("broadcast_Date")),
                    "period": period, "status": str(item.get("type_Sub") or ""),
                    "title": f"Integrated financial results {period} {item.get('consolidated') or ''} ({label})",
                    "source": "integrated-filing-results", "url": url, "raw_metadata": item,
                }


def prepare_details(session, row, folder):
    request = row.get('detail_request')
    if not request:
        return []
    path = Path(row['detail_file'])
    details = json.loads(path.read_text()) if path.is_file() else {}
    if request['type'] == 'shareholding':
        for section in SHAREHOLDING_SECTIONS:
            if section not in details:
                row['_details_fetched'] = True
                details[section] = get_json(session, 'corporate-share-holdings-sme',
                    {'ndsId': request['record_id'], 'index': section})
                write_json(path, details)
        return []
    if not path.is_file():
        row['_details_fetched'] = True
        details = get_json(session, 'corporates-financial-results-data', request['params'])
        write_json(path, details)
    url = valid_url(details.get('attachment_filename')) if isinstance(details, dict) else ''
    if not url:
        return []
    # Notes are a separate representation, retaining a link to the same detail JSON.
    extra = {k:v for k,v in row.items() if k not in ('_db_id','file','sha256','detail_request','error','_details_fetched')}
    extra.update(id=str(row['id']).rsplit('-',1)[0]+'-notes',url=url,
                 title=str(row['title']).replace('(xbrl)','(notes)'))
    return [extra]


def discovery_sources(session, symbol, start, end, folder):
    return [
        ('announcements', lambda: announcement_rows(session,symbol,start,end)),
        ('annual reports', lambda: annual_rows(session,symbol,start)),
        ('shareholding', lambda: shareholding_rows(session,symbol,start,folder)),
        ('financial results', lambda: financial_rows(session,symbol,start,folder)),
    ]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("symbols", nargs="*", help="NSE Emerge symbols, e.g. AIMTRON ADISOFT")
    parser.add_argument("--years", type=int, default=10)
    parser.add_argument("--output", type=Path, default=Path("data"))
    parser.add_argument("--download", action="store_true")
    add_pipeline_arguments(parser)
    args = parser.parse_args()
    symbols = [symbol.upper() for symbol in args.symbols]
    if args.years < 1 or any(not re.fullmatch(r"[A-Z0-9]{2,20}", symbol) for symbol in symbols):
        parser.error("Use --years >= 1 and valid NSE symbols")
    if not 0 <= args.failure_threshold <= 1:
        parser.error("--failure-threshold must be between 0 and 1")
    retry = args.retry_failed or bool(args.retry_run)
    if not symbols and not retry:
        parser.error("Specify at least one NSE symbol")
    today = date.today()
    run_collection('NSE', symbols, args.output, years_ago(today, args.years), today,
                   args.download or retry, args.db, 'retry' if retry else 'collect',
                   args.failure_threshold, args.retry_run)


if __name__ == "__main__":
    main()
