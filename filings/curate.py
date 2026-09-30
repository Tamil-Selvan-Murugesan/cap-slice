"""Build a nonduplicated, analysis-focused document index and HTML chunks.

Reads SQLite document records. Source documents remain on disk.
Writes ingestion selection and HTML chunks back to SQLite.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import defaultdict
from html.parser import HTMLParser
from itertools import groupby
from pathlib import Path

from filings.nse_classification import classify_announcement
from filings.db import Database, encode

KEEP_KINDS = {
    "annual_report", "shareholding", "investor_presentation",
    "concall_transcript", "credit_rating", "financial_results",
}
KIND_PRIORITY = {
    "annual_report": 0, "concall_transcript": 4,
    "investor_presentation": 5, "credit_rating": 6,
    "shareholding": 7, "financial_results": 8,
}
COMPANIES = {
    "543664": "Kaynes Technology", "540699": "Dixon Technologies",
    "500325": "Reliance Industries", "AIMTRON": "Aimtron Electronics",
    "ADISOFT": "Adisoft Technologies",
}
KIND_TITLES = {
    "annual_report": "Annual report", "shareholding": "Shareholding pattern",
    "investor_presentation": "Investor presentation",
    "concall_transcript": "Earnings call transcript",
    "credit_rating": "Credit rating", "financial_results": "Financial results",
}
GENERIC_SUBJECTS = {
    "outcome of board meeting", "general updates", "updates",
    "analysts/institutional investor meet/con. call updates",
}


def clean(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def retrieval_title(row: dict) -> str:
    symbol = row["symbol"]
    company = COMPANIES.get(symbol, symbol)
    kind = KIND_TITLES[row["kind"]]
    source_title = clean(str(row.get("title") or ""))
    detail = source_title if source_title.lower() not in GENERIC_SUBJECTS else ""
    parts = [f"{company} ({symbol})"]
    if row.get("_reviewed_title") or (detail and detail.lower().startswith(kind.lower())):
        parts.append(detail)
    else:
        parts.append(kind)
        if detail:
            parts.append(detail)
    period = str(row.get("period") or "")
    if period and period not in " ".join(parts):
        parts.append(f"period {period}")
    date = str(row.get("date") or "")
    if date:
        parts.append(f"filed {date}")
    return " — ".join(parts)


def path_for(row: dict) -> Path | None:
    # NSE's detail JSON is easier to use than its shareholding/legacy-results XML.
    if row.get("exchange") == "NSE" and row["kind"] == "shareholding":
        detail = row.get("detail_file")
        if detail and Path(detail).is_file():
            return Path(detail)
    if row.get("source") == "corporates-financial-results":
        detail = row.get("detail_file")
        if detail and Path(detail).is_file():
            return Path(detail)
    file = row.get("file")
    return Path(file) if file and Path(file).is_file() else None


def choose_best(rows: list[dict], reason: str, excluded: list[dict], key):
    groups = defaultdict(list)
    for row in rows:
        groups[key(row)].append(row)
    kept = []
    for items in groups.values():
        best = max(items, key=lambda r: (
            "revis" in str(r.get("status", "")).lower(),
            r.get("date") or "",
            r.get("id") or "",
        ))
        kept.append(best)
        for item in items:
            if item is not best:
                excluded.append({"symbol": item["symbol"], "kind": item["kind"],
                                 "db_id": item.get("_db_id"), "id": item.get("id"), "file": item.get("file"),
                                 "reason": reason, "kept_id": best.get("id"), "kept_db_id": best.get("_db_id")})
    return kept


def curated_rows(data_dir: Path, symbols: list[str], db: Database) -> tuple[list[dict], list[dict]]:
    selected = []
    excluded = []
    review_path = Path(__file__).resolve().parents[1] / "config" / "nse_verified_announcements.json"
    verified_nse = json.loads(review_path.read_text()) if review_path.is_file() else {}
    for symbol in symbols:
        document_rows = [db.row(r[0]) for r in db.conn.execute(
            'SELECT id FROM documents WHERE symbol=? ORDER BY id', (symbol,))]
        reviews = verified_nse.get(symbol, {})
        active_replacements = set()
        for candidate in document_rows:
            review = reviews.get(str(candidate.get("id")))
            file = candidate.get("file")
            if (review and not candidate.get("error") and file and Path(file).is_file()
                    and hashlib.sha256(Path(file).read_bytes()).hexdigest() == review["sha256"]):
                active_replacements.update(review.get("supersedes", []))
        for original in document_rows:
            # Inactive records must never re-enter ingestion.
            if original.get("_download_status") == "archived":
                continue
            row = {"symbol": symbol, **original}
            if row.get("source") == "getCorporateAnnouncement" and row.get("exchange") == "NSE":
                if str(row.get("id")) in active_replacements:
                    excluded.append({"symbol": symbol, "kind": row.get("kind"),
                                     "db_id": row.get("_db_id"), "id": row.get("id"), "file": row.get("file"),
                                     "reason": "superseded verified NSE filing"})
                    continue
                path = path_for(row)
                if row.get("error") or not path:
                    excluded.append({"symbol": symbol, "kind": row.get("kind"),
                                     "db_id": row.get("_db_id"), "id": row.get("id"), "file": row.get("file"),
                                     "reason": "missing or failed source"})
                    continue
                metadata = row.get("raw_metadata") or {
                    "desc": row.get("title"),
                    "attchmntText": row.get("description"),
                    "attchmntFile": row.get("url"),
                }
                row["kind"] = classify_announcement(metadata)
                review = reviews.get(str(row.get("id")))
                # Existing content reviews enrich matching files; new filings
                # are selected automatically using the collector's same rules.
                if review and hashlib.sha256(path.read_bytes()).hexdigest() == review["sha256"]:
                    row["_source_title"] = row.get("title") or ""
                    row["kind"] = review["kind"]
                    row["title"] = review["title"]
                    row["period"] = review["period"]
                    row["_reviewed_title"] = True
            if row.get("kind") not in KEEP_KINDS:
                excluded.append({"symbol": symbol, "kind": row.get("kind"),
                                 "db_id": row.get("_db_id"), "id": row.get("id"), "file": row.get("file"),
                                 "date": row.get("date"), "title": row.get("title"),
                                 "source_url": row.get("url"),
                                 "reason": "outside current document allowlist"})
                continue
            path = path_for(row)
            if row.get("error") or not path:
                excluded.append({"symbol": symbol, "kind": row.get("kind"),
                                 "db_id": row.get("_db_id"), "id": row.get("id"), "file": row.get("file"),
                                 "reason": "missing or failed source"})
                continue
            row["_path"] = path
            selected.append(row)

    # The same integrated filing is distributed as XBRL XML, iXBRL HTML
    # and sometimes a PDF. Use the rendered iXBRL for retrieval.
    integrated = defaultdict(list)
    other = []
    for row in selected:
        if row.get("source") == "integrated-filing-results":
            integrated[(row["symbol"], str(row["id"]).rsplit("-", 1)[0])].append(row)
        elif row.get("source") == "corporates-financial-results":
            integrated[(row["symbol"], str(row["id"]).rsplit("-", 1)[0])].append(row)
        else:
            other.append(row)
    for items in integrated.values():
        def representation_rank(r):
            suffix = str(r.get("id", "")).rsplit("-", 1)[-1]
            return {"ixbrl": 3, "pdf": 2, "xbrl": 1, "notes": 0}.get(suffix, 0)
        best = max(items, key=representation_rank)
        other.append(best)
        for item in items:
            if item is not best:
                excluded.append({"symbol": item["symbol"], "kind": item["kind"],
                                 "db_id": item.get("_db_id"), "id": item.get("id"), "file": item.get("file"),
                                 "reason": "alternate representation of filing",
                                 "kept_id": best.get("id"), "kept_db_id": best.get("_db_id")})
    selected = other

    # Keep the newest revision of each annual report and shareholding period.
    stable = [r for r in selected if r["kind"] not in {"annual_report", "shareholding"}]
    for kind in ("annual_report", "shareholding"):
        stable.extend(choose_best([r for r in selected if r["kind"] == kind],
                                  "superseded filing", excluded,
                                  lambda r: (r["symbol"], r.get("period"))))
    selected = stable

    # For integrated financials, distinguish standalone and consolidated,
    # then prefer a revision over the original filing for the same period.
    integrated_financial = [r for r in selected if r.get("source") == "integrated-filing-results"]
    selected = [r for r in selected if r.get("source") != "integrated-filing-results"]
    def basis(row):
        title = str(row.get("title") or "").lower()
        return "standalone" if "standalone" in title else "consolidated" if "consolidated" in title else ""
    selected.extend(choose_best(integrated_financial, "superseded financial filing",
                                excluded, lambda r: (r["symbol"], r.get("period"), basis(r))))

    # Exact-byte deduplication across categories and URLs, scoped per company.
    hashes = defaultdict(list)
    for row in selected:
        path = row["_path"]
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        row["_hash"] = digest
        hashes[(row["symbol"], digest)].append(row)
    documents = []
    for (symbol, digest), items in hashes.items():
        best = min(items, key=lambda r: (KIND_PRIORITY[r["kind"]], r.get("date") or "", r.get("id") or ""))
        aliases = sorted({r["kind"] for r in items} - {best["kind"]})
        documents.append({
            "db_id": best["_db_id"], "document_id": f"{symbol}:{digest[:20]}",
            "symbol": symbol, "kind": best["kind"], "aliases": aliases,
            "date": best.get("date") or "", "period": best.get("period") or "",
            "status": best.get("status") or "", "title": retrieval_title(best),
            "source_title": best.get("_source_title", best.get("title") or ""),
            "source": best.get("source") or "", "source_url": best.get("url") or "",
            "path": str(best["_path"]), "sha256": digest,
            "format": best["_path"].suffix.lower().lstrip("."),
            "processing": (
                "html_chunks" if best["_path"].suffix.lower() in {".html", ".htm"}
                else "pdf_extraction_pending" if best["_path"].suffix.lower() == ".pdf"
                else "structured_only"
            ),
            "source_ids": [str(r.get("id") or "") for r in items],
        })
        for item in items:
            if item is not best:
                excluded.append({"symbol": symbol, "kind": item["kind"],
                                 "db_id": item.get("_db_id"), "id": item.get("id"), "file": item.get("file"),
                                 "reason": "identical file content",
                                 "kept_id": best.get("id"), "kept_db_id": best.get("_db_id")})
    documents.sort(key=lambda r: (r["symbol"], r["kind"], r["period"], r["date"], r["document_id"]))
    return documents, excluded


class FilingHTML(HTMLParser):
    """Extract visible table rows and standalone paragraphs from an iXBRL page."""

    SKIP = {"head", "style", "script", "noscript", "ix:header"}
    VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.skip_depth = 0
        self.table_depth = 0
        self.table_index = 0
        self.row = None
        self.cell = None
        self.cell_is_header = False
        self.rows = []
        self.paragraph_tag = None
        self.paragraph = []
        self.paragraphs = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if self.skip_depth:
            if tag not in self.VOID:
                self.skip_depth += 1
            return
        style = str(attrs.get("style") or "").replace(" ", "").lower()
        if tag in self.SKIP or "display:none" in style or attrs.get("hidden") is not None:
            self.skip_depth = 1
            return
        if tag == "table":
            if self.table_depth == 0:
                self.table_index += 1
            self.table_depth += 1
        elif tag == "tr" and self.table_depth and self.row is None:
            self.row = []
        elif tag in ("td", "th") and self.row is not None and self.cell is None:
            self.cell = []
            self.cell_is_header = tag == "th"
        elif tag in ("p", "h1", "h2", "h3", "h4") and not self.table_depth and self.paragraph_tag is None:
            self.paragraph_tag = tag
            self.paragraph = []

    def handle_data(self, data):
        if self.skip_depth:
            return
        if self.cell is not None:
            self.cell.append(data)
        elif self.paragraph_tag:
            self.paragraph.append(data)

    def handle_endtag(self, tag):
        if self.skip_depth:
            self.skip_depth -= 1
            return
        if tag in ("td", "th") and self.cell is not None and self.row is not None:
            value = clean(" ".join(self.cell))
            self.row.append((value, self.cell_is_header))
            self.cell = None
        elif tag == "tr" and self.row is not None:
            cells = [(text, header) for text, header in self.row if text]
            if cells:
                self.rows.append((self.table_index, cells))
            self.row = None
        elif tag == "table" and self.table_depth:
            self.table_depth -= 1
        elif tag == self.paragraph_tag:
            value = clean(" ".join(self.paragraph))
            if value:
                self.paragraphs.append(value)
            self.paragraph_tag = None
            self.paragraph = []


def html_chunks(document: dict, max_words: int = 550) -> list[dict]:
    parser = FilingHTML()
    parser.feed(Path(document["path"]).read_text(errors="replace"))
    output = []
    context = f"{document['symbol']} | {document['kind']} | {document['period']} | {document['title']}"
    for table, iterator in groupby(parser.rows, key=lambda row: row[0]):
        rows = [cells for _, cells in iterator]
        if not rows:
            continue
        header_lines = []
        for candidate in rows[:4]:
            first = candidate[0][0].lower()
            looks_like_header = len(candidate) >= 3 and (
                first.startswith(("sr", "serial", "searial", "category", "particular",
                                  "name", "details of", "no of voting", "class eg"))
                or all(is_header for _, is_header in candidate)
            )
            if looks_like_header:
                header_lines.append(" | ".join(value for value, _ in candidate))
            elif header_lines:
                break
        header = "\n".join(header_lines)
        block, start, words = [], 1, 0
        for index, cells in enumerate(rows, 1):
            line = " | ".join(value for value, _ in cells)
            count = len(line.split())
            if block and words + count > max_words:
                body = "\n".join(block)
                output.append({"section": f"table {table}", "table": table,
                               "row_start": start, "row_end": index - 1,
                               "text": context + "\n" + (header + "\n" if header and start > 1 else "") + body,
                               "body": body})
                block, start, words = [], index, 0
            block.append(line)
            words += count
        if block:
            body = "\n".join(block)
            output.append({"section": f"table {table}", "table": table,
                           "row_start": start, "row_end": len(rows),
                           "text": context + "\n" + (header + "\n" if header and start > 1 else "") + body,
                           "body": body})
    # Keep narrative outside tables, without the style and hidden XBRL header.
    paragraphs = [p for p in parser.paragraphs if len(p.split()) >= 6]
    if paragraphs:
        block, words = [], 0
        for para in paragraphs:
            count = len(para.split())
            if block and words + count > max_words:
                body = "\n".join(block)
                output.append({"section": "narrative", "table": None, "row_start": None,
                               "row_end": None, "text": context + "\n" + body, "body": body})
                block, words = [], 0
            block.append(para)
            words += count
        if block:
            body = "\n".join(block)
            output.append({"section": "narrative", "table": None, "row_start": None,
                           "row_end": None, "text": context + "\n" + body, "body": body})
    return output


def build(data_dir: Path, symbols: list[str], max_words: int, db: Database) -> None:
    documents, excluded = curated_rows(data_dir, symbols, db)
    chunks = []
    seen = set()
    for doc in documents:
        if doc["format"] not in ("html", "htm"):
            continue
        for index, chunk in enumerate(html_chunks(doc, max_words), 1):
            digest = hashlib.sha256(clean(chunk["body"]).lower().encode()).hexdigest()
            key = (doc["symbol"], doc["kind"], doc["period"], digest)
            if key in seen:
                continue
            seen.add(key)
            chunk_id = hashlib.sha256(f"{doc['document_id']}:{index}".encode()).hexdigest()[:20]
            chunks.append({
                "chunk_id": chunk_id, "document_id": doc["document_id"], "db_id": doc["db_id"],
                "symbol": doc["symbol"], "kind": doc["kind"], "period": doc["period"],
                "date": doc["date"], "source_url": doc["source_url"],
                "source_path": doc["path"], "section": chunk["section"],
                "table": chunk["table"], "row_start": chunk["row_start"],
                "row_end": chunk["row_end"], "text": chunk["text"],
            })
    save_curation(db, symbols, documents, excluded, chunks)
    print(f"{len(documents)} selected documents, {len(excluded)} excluded records, "
          f"{len(chunks)} HTML chunks -> {db.path}")


def save_curation(db, symbols, documents, excluded, chunks):
    if not symbols:
        return
    marks = ','.join('?' for _ in symbols)
    # One transaction: readers see either the old or the complete new selection.
    with db.conn:
        db.conn.execute(f"DELETE FROM document_chunks WHERE document_id IN (SELECT id FROM documents WHERE symbol IN ({marks}))", symbols)
        db.conn.execute(f"""UPDATE documents SET selected_to_ingest=0,
            selection_reason='Not selected for ingestion',
            canonical_document_id=NULL,corpus_id=NULL,retrieval_title=NULL,curated_kind=NULL,
            curated_period=NULL,ingestion_path=NULL,ingestion_sha256=NULL,ingestion_format=NULL,
            processing=NULL,aliases_json='[]',source_ids_json='[]' WHERE symbol IN ({marks})""", symbols)
        for row in excluded:
            kept = row.get('kept_db_id')
            if kept is None and row.get('kept_id'):
                match = db.conn.execute('SELECT id FROM documents WHERE symbol=? AND source_id=? ORDER BY id LIMIT 1',
                                        (row['symbol'], str(row['kept_id']))).fetchone()
                kept = match[0] if match else None
            db.conn.execute('UPDATE documents SET selection_reason=?,canonical_document_id=? WHERE id=?',
                            (row['reason'], kept, row['db_id']))
        for doc in documents:
            db.conn.execute('''UPDATE documents SET selected_to_ingest=1,selection_reason='Selected canonical document',
                canonical_document_id=id,corpus_id=?,retrieval_title=?,curated_kind=?,curated_period=?,
                ingestion_path=?,ingestion_sha256=?,ingestion_format=?,processing=?,aliases_json=?,source_ids_json=?
                WHERE id=?''', (doc['document_id'],doc['title'],doc['kind'],doc['period'],doc['path'],
                    doc['sha256'],doc['format'],doc['processing'],encode(doc['aliases']),encode(doc['source_ids']),doc['db_id']))
        for chunk in chunks:
            db.conn.execute('INSERT INTO document_chunks VALUES (?,?,?,?,?,?,?,?,?)',
                (chunk['chunk_id'],chunk['db_id'],chunk['document_id'],chunk['section'],chunk['table'],
                 chunk['row_start'],chunk['row_end'],chunk['text'],encode({k:v for k,v in chunk.items() if k!='db_id'})))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("symbols", nargs="*", default=[])
    parser.add_argument("--data", type=Path, default=Path("data"))
    parser.add_argument("--db", type=Path, help="Default: DATA/pipeline.sqlite3")
    parser.add_argument("--max-words", type=int, default=550)
    args = parser.parse_args()
    if args.max_words < 100:
        parser.error("--max-words must be at least 100")
    db_path = args.db or args.data / 'pipeline.sqlite3'
    if not db_path.is_file():
        parser.error("Database not found. Run a collector first.")
    with Database(db_path) as db:
        symbols = args.symbols or list(dict.fromkeys(s for _,s in db.symbols()))
        build(args.data, symbols, args.max_words, db)


if __name__ == "__main__":
    main()
