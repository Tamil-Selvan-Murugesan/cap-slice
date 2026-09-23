"""Download the documents listed in the availability matrix.

Files land in ``data/<SYMBOL>/<doc_type dir>/<filed_date>_<period>.<ext>``.
Requests are sequential and throttled (see AGENTS.md rules). Existing files
are skipped, so the script can be re-run to resume.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import re
import sys
import time
import urllib.error
import urllib.request
import zipfile
from dataclasses import dataclass
from datetime import date
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = REPO_ROOT / "data"
MATRIX_PATH = DATA_DIR / "document_availability_matrix.csv"
MANIFEST_PATH = DATA_DIR / "download_manifest.csv"

DOC_TYPE_DIRS = {
    "annual_report": "annual_reports",
    "periodic_results": "periodic_results",
    "shareholding_pattern": "shareholding_patterns",
    "concall_transcript": "concall_transcripts",
    "investor_presentation": "investor_presentations",
}

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)

# Detect the real file type from its first bytes; an HTML page is a decoy/error.
MAGIC = {b"%PDF": ".pdf", b"PK\x03\x04": ".zip"}

MANIFEST_FIELDS = [
    "symbol", "doc_type", "period_label", "filed_date", "url",
    "result", "http_code", "bytes", "sha256", "path", "error", "downloaded_on",
]


@dataclass
class Outcome:
    result: str  # downloaded | skipped_exists | failed
    http_code: str = ""
    size: int = 0
    sha256: str = ""
    path: str = ""
    error: str = ""


def slugify(text: str) -> str:
    text = re.sub(r"[^A-Za-z0-9.]+", "-", text).strip("-")
    return text or "undated"


def base_name(row: dict[str, str]) -> str:
    parts = [row["filed_date"].strip(), slugify(row["period_label"])]
    return "_".join(p for p in parts if p)


def target_dir(row: dict[str, str]) -> Path:
    return DATA_DIR / row["symbol"] / DOC_TYPE_DIRS[row["doc_type"]]


def existing_file(row: dict[str, str]) -> Path | None:
    for ext in MAGIC.values():
        path = target_dir(row) / (base_name(row) + ext)
        if path.exists():
            return path
    return None


def unzip_single_pdf(zip_path: Path) -> Path | None:
    """Replace a ZIP holding exactly one PDF with that PDF (same base name).

    NSE serves annual reports up to FY2022-23 as ZIPs wrapping a single PDF.
    Returns the PDF path, or None (ZIP left in place) if the contents differ.
    """
    with zipfile.ZipFile(zip_path) as zf:
        pdfs = [n for n in zf.namelist() if n.lower().endswith(".pdf")]
        if len(pdfs) != 1:
            return None
        data = zf.read(pdfs[0])
    if not data.startswith(b"%PDF"):
        return None
    pdf_path = zip_path.with_suffix(".pdf")
    tmp = pdf_path.with_suffix(".pdf.part")
    tmp.write_bytes(data)
    tmp.rename(pdf_path)
    zip_path.unlink()
    return pdf_path


def unzip_existing() -> None:
    for zip_path in sorted(DATA_DIR.glob("*/*/*.zip")):
        if pdf := unzip_single_pdf(zip_path):
            print(f"unzipped {pdf.relative_to(REPO_ROOT)}", file=sys.stderr)
        else:
            print(f"left as ZIP (not exactly one PDF inside): "
                  f"{zip_path.relative_to(REPO_ROOT)}", file=sys.stderr)


def fetch(url: str, timeout: int) -> tuple[int, bytes]:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=timeout) as resp:  # follows redirects
        return resp.status, resp.read()


def download_row(row: dict[str, str], timeout: int) -> Outcome:
    if found := existing_file(row):
        data = found.read_bytes()
        return Outcome("skipped_exists", size=len(data),
                       sha256=hashlib.sha256(data).hexdigest(),
                       path=str(found.relative_to(REPO_ROOT)))
    try:
        code, body = fetch(row["url"], timeout)
    except urllib.error.HTTPError as e:
        return Outcome("failed", http_code=str(e.code), error=f"HTTP {e.code}")
    except Exception as e:  # network errors, timeouts
        return Outcome("failed", error=f"{type(e).__name__}: {e}")

    ext = next((x for magic, x in MAGIC.items() if body.startswith(magic)), None)
    if ext is None:
        return Outcome("failed", http_code=str(code), size=len(body),
                       error=f"not a PDF/ZIP (starts {body[:16]!r})")

    path = target_dir(row) / (base_name(row) + ext)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(ext + ".part")
    tmp.write_bytes(body)
    tmp.rename(path)
    if ext == ".zip" and (pdf := unzip_single_pdf(path)):
        path, body = pdf, pdf.read_bytes()
    return Outcome("downloaded", http_code=str(code), size=len(body),
                   sha256=hashlib.sha256(body).hexdigest(),
                   path=str(path.relative_to(REPO_ROOT)))


def matrix_status(outcome: Outcome, current: str) -> str:
    """Map a download outcome to the matrix's fetch_status vocabulary."""
    if outcome.result in ("downloaded", "skipped_exists"):
        return "200"
    if outcome.http_code in ("401", "403"):
        return "blocked"
    if outcome.http_code in ("404", "410"):
        return "not found"
    return current


def write_matrix(rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    """Write the matrix, setting download_status from what is on disk."""
    for row in rows:
        row["download_status"] = "yes" if existing_file(row) else "no"
    with MATRIX_PATH.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--symbol", action="append", help="limit to these NSE symbols")
    ap.add_argument("--doc-type", action="append", choices=sorted(DOC_TYPE_DIRS))
    ap.add_argument("--delay", type=float, default=3.0,
                    help="seconds between requests (default 3)")
    ap.add_argument("--timeout", type=int, default=120)
    ap.add_argument("--dry-run", action="store_true",
                    help="list what would be downloaded, fetch nothing")
    ap.add_argument("--no-update-matrix", action="store_true",
                    help="don't write fetch_status/download_status back to the matrix CSV")
    ap.add_argument("--refresh-status", action="store_true",
                    help="only recompute download_status from files on disk, fetch nothing")
    args = ap.parse_args(argv)

    with MATRIX_PATH.open(newline="") as f:
        reader = csv.DictReader(f)
        fieldnames = list(reader.fieldnames)
        rows = list(reader)
    if "download_status" not in fieldnames:
        fieldnames.append("download_status")
    unzip_existing()

    if args.refresh_status:
        write_matrix(rows, fieldnames)
        return 0

    todo = [
        r for r in rows
        if r["url"].strip()
        and (not args.symbol or r["symbol"] in args.symbol)
        and (not args.doc_type or r["doc_type"] in args.doc_type)
    ]
    print(f"{len(todo)} of {len(rows)} matrix rows have a URL and match the filters",
          file=sys.stderr)

    if args.dry_run:
        for r in todo:
            print(target_dir(r).relative_to(REPO_ROOT) / base_name(r), r["url"])
        return 0

    manifest = []
    today = date.today().isoformat()
    for i, row in enumerate(todo, 1):
        out = download_row(row, args.timeout)
        print(f"[{i}/{len(todo)}] {out.result:<14} {row['symbol']:<10} "
              f"{row['doc_type']:<21} {row['period_label']}"
              + (f"  ({out.error})" if out.error else ""), file=sys.stderr)
        manifest.append({
            "symbol": row["symbol"], "doc_type": row["doc_type"],
            "period_label": row["period_label"], "filed_date": row["filed_date"],
            "url": row["url"], "result": out.result, "http_code": out.http_code,
            "bytes": out.size, "sha256": out.sha256, "path": out.path,
            "error": out.error, "downloaded_on": today if out.result == "downloaded" else "",
        })
        row["fetch_status"] = matrix_status(out, row["fetch_status"])
        if out.result != "skipped_exists" and i < len(todo):
            time.sleep(args.delay)

    # Merge with earlier runs so filtered runs don't drop other entries.
    merged: dict[str, dict] = {}
    if MANIFEST_PATH.exists():
        with MANIFEST_PATH.open(newline="") as f:
            merged = {m["url"]: m for m in csv.DictReader(f)}
    for m in manifest:
        if m["result"] == "skipped_exists" and m["url"] in merged:
            continue  # keep the original download record
        merged[m["url"]] = m
    with MANIFEST_PATH.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=MANIFEST_FIELDS)
        w.writeheader()
        w.writerows(merged.values())

    if not args.no_update_matrix:
        write_matrix(rows, fieldnames)

    counts: dict[str, int] = {}
    for m in manifest:
        counts[m["result"]] = counts.get(m["result"], 0) + 1
    print(f"done: {counts}; manifest -> {MANIFEST_PATH.relative_to(REPO_ROOT)}",
          file=sys.stderr)
    return 1 if counts.get("failed") else 0


if __name__ == "__main__":
    sys.exit(main())
