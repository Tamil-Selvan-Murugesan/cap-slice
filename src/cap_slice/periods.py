"""Normalise a document's period into filterable fields, and check the rule against the documents.

    uv run cap-slice-periods                  # check every downloaded document -> review/periods/

Indian fiscal years run April-March; `fiscal_year` is the year the FY ends (FY2018-19 -> 2019).

    normalise(doc_type, period_label, filed_date, sme) -> {"fiscal_year", "period_kind", "period", "source"}

  annual_report          "FY2018-19"                          -> 2019, annual,    "FY19"
  periodic_results       "Q4/FY2025-26 (quarterly)"           -> 2026, quarter,   "Q4 FY26"
                         "H1 FY26 (half-yearly, SME)"         -> 2026, half_year, "H1 FY26"
                         "FY2025-26 audited (half-yearly, SME)" -> 2026, annual,  "FY26"
  concall / presentation "Aug 2026", "Feb 2018 (a)", "Oct/Nov 2024"
                         -> the latest quarter that ended before the event's month:
                            Aug 2026 -> Q1 FY27 (Apr-Jun 2026) -> 2027, event, "Q1 FY27"
                         -> for NSE SME companies (half-yearly filers) the latest half-year:
                            Aug 2026 -> H2 FY26 (Oct 2025-Mar 2026) -> 2026, event, "H2 FY26"

`source` is "label" (read from the catalogue label), "event_rule" (inferred from the event month) or
"override" (checked against the document).

The event rule is a guess (an AGM speech, a fundraise deck or a late call breaks it), so the check
reads the first pages of every concall and presentation (PDF text layer; the MinerU advanced cache for
pages without one) for the period the document states ("Q1 FY27", "quarter ended June 30, 2026",
"H1 FY26", "1QFY20") and compares. Where the document states a different fiscal year, the printed one
wins: it is recorded in data/period_overrides.csv (path, fiscal_year, period, note) and normalise_doc()
applies it. A document with no override and no event month gets no fiscal_year (a blank is safer than a
wrong year under a hard filter).
"""

from __future__ import annotations

import argparse
import collections
import csv
import json
import re
from pathlib import Path

from cap_slice.downloader import REPO_ROOT

MONTHS = {m: i for i, m in enumerate(
    "jan feb mar apr may jun jul aug sep oct nov dec".split(), 1)}
MONTH_NAMES = {**MONTHS, **{m: MONTHS[m[:3]] for m in
               "january february march april june july august september october november december".split()}}
OVERRIDES = REPO_ROOT / "data" / "period_overrides.csv"


def _fy(start_or_two_digit: str) -> int:
    """'2018-19' -> 2019, '26-27' -> 2027, '26' -> 2026, '2026' -> 2026."""
    s = start_or_two_digit
    if re.fullmatch(r"\d{2}-\d{2}", s):
        return 2000 + int(s[3:])
    if "-" in s:
        return int(s.split("-")[0]) + 1
    return 2000 + int(s) if len(s) == 2 else int(s)


def _event_quarter(month: int, year: int) -> tuple[int, int]:
    """(quarter, fiscal_year) of the latest quarter that ended before an event in month/year."""
    if month <= 3:
        return 3, year            # Oct-Dec of year-1 = Q3 FY<year>
    if month <= 6:
        return 4, year            # Jan-Mar = Q4 FY<year>
    if month <= 9:
        return 1, year + 1        # Apr-Jun = Q1 FY<year+1>
    return 2, year + 1            # Jul-Sep = Q2 FY<year+1>


def _event_half(month: int, year: int) -> tuple[int, int]:
    """(half, fiscal_year) of the latest half-year that ended before an event (SME companies)."""
    if month <= 3:
        return 1, year            # Apr-Sep of year-1 = H1 FY<year>
    if month <= 9:
        return 2, year            # Oct-Mar = H2 FY<year>
    return 1, year + 1            # Apr-Sep = H1 FY<year+1>


def normalise(doc_type: str, period_label: str, filed_date: str = "", sme: bool = False) -> dict:
    lab = period_label.strip()
    out = {"fiscal_year": None, "period_kind": None, "period": "", "source": ""}
    if doc_type in ("annual_report", "periodic_results"):
        if m := re.match(r"Q([1-4])\s*/\s*FY(\d{4}-\d{2})", lab):
            q, fy = int(m[1]), _fy(m[2])
            return {"fiscal_year": fy, "period_kind": "quarter", "period": f"Q{q} FY{fy % 100:02d}", "source": "label"}
        if m := re.match(r"H([12])\s*FY(\d{4}-\d{2}|\d{2})\b", lab):
            h, fy = int(m[1]), _fy(m[2])
            return {"fiscal_year": fy, "period_kind": "half_year", "period": f"H{h} FY{fy % 100:02d}", "source": "label"}
        if m := re.match(r"FY(\d{4}-\d{2})", lab):
            fy = _fy(m[1])
            return {"fiscal_year": fy, "period_kind": "annual", "period": f"FY{fy % 100:02d}", "source": "label"}
        return out
    m = re.match(r"(?:[A-Za-z]{3}/)?([A-Za-z]{3})\s+(\d{4})", lab)  # "Aug 2026", "Oct/Nov 2024" -> Nov
    if not m and filed_date:
        y, mo = filed_date.split("-")[:2]
        month, year = int(mo), int(y)
    elif m and m[1].lower() in MONTHS:
        month, year = MONTHS[m[1].lower()], int(m[2])
    else:
        return out
    if sme:
        h, fy = _event_half(month, year)
        return {"fiscal_year": fy, "period_kind": "event", "period": f"H{h} FY{fy % 100:02d}", "source": "event_rule"}
    q, fy = _event_quarter(month, year)
    return {"fiscal_year": fy, "period_kind": "event", "period": f"Q{q} FY{fy % 100:02d}", "source": "event_rule"}


def load_overrides() -> dict[str, dict]:
    if not OVERRIDES.exists():
        return {}
    return {r["path"]: r for r in csv.DictReader(OVERRIDES.open())}


def sme_symbols() -> set[str]:
    return {r["symbol"] for r in csv.DictReader((REPO_ROOT / "data" / "document_availability_matrix.csv").open())
            if r["listing_tier"] == "NSE SME"}


def normalise_doc(path: str, doc_type: str, period_label: str, filed_date: str = "",
                  overrides: dict[str, dict] | None = None, sme: bool | None = None) -> dict:
    """normalise() plus the checked override for this file, if any. `path` as `data/...pdf`."""
    if sme is None:
        sme = path.split("/")[1] in sme_symbols()
    out = normalise(doc_type, period_label, filed_date, sme)
    o = (load_overrides() if overrides is None else overrides).get(path)
    if o:
        out = {**out, "fiscal_year": int(o["fiscal_year"]) if o["fiscal_year"] else None,
               "period": o["period"], "source": "override"}
    return out


# ---- check: what period does the document itself state? ----

FY = r"(?:FY|F\.\s?Y\.?|F\s?Y)\s*[-–]?\s*'?(\d{4}\s*[-–]\s*\d{2}|\d{2}\s*[-–]\s*\d{2}|\d{4}|\d{2})\b"
DAY = r"(?:on\s+)?(?:\S{1,6}\s+){0,2}?"   # "30th", "30\"", "31 51" (OCR noise), "the 31st day of"
MON_YEAR = r"(june|september|december|march)\s*,?\s*(?:\d{1,2}\S{0,3}\s*,?\s*)?(\d{4})"
PATTERNS = [
    # Q3 FY24, Q3FY2024, Q3 & 9M FY24, Q3 and 9M FY'24, Q3 FY 2023-24
    (re.compile(r"\bQ([1-4])\s*[-–]?\s*(?:(?:&|and)\s*(?:9M|H[12]|12M|FY)\s*)?" + FY, re.I), "q"),
    (re.compile(r"\b([1-4])Q\s*" + FY, re.I), "q"),                                     # 1QFY20
    (re.compile(r"\bH([12])\s*" + FY, re.I), "h"),                                       # H1 FY26
    (re.compile(r"\b(?:quarter|three months)(?:\s+and\s+(?:nine|six|twelve)\s+months|\s+and\s+half[- ]year)?"
                r"\s+ended\s+" + DAY + MON_YEAR, re.I), "qe"),
    (re.compile(r"\b(?:half[- ]year|six months)\s+ended\s+" + DAY + MON_YEAR, re.I), "he"),
    (re.compile(r"\b(?:financial year|year|twelve months)\s+ended\s+" + DAY + r"(march)\s*,?\s*(?:\d{1,2}\S{0,3}\s*,?\s*)?(\d{4})", re.I), "ye"),
    (re.compile(r"\b(?:annual report|financial year|FY)\s*(?:for\s+(?:the\s+)?(?:financial\s+)?year\s+)?(20\d\d)\s*[-–]\s*(\d{2})\b", re.I), "ar"),
]
QE = {"june": (1, 1), "september": (2, 1), "december": (3, 1), "march": (4, 0)}


def stated_periods(text: str) -> collections.Counter:
    """Periods a text states, as Counter of (period, fiscal_year)."""
    found = collections.Counter()
    for rx, kind in PATTERNS:
        for m in rx.finditer(text):
            g = m.groups()
            if kind in ("q", "h"):
                fy = _fy(re.sub(r"\s|–", lambda x: "-" if x[0] == "–" else "", g[1]))
                if not 2010 <= fy <= 2030:
                    continue
                found[(f"{'Q' if kind == 'q' else 'H'}{g[0]} FY{fy % 100:02d}", fy)] += 1
            elif kind == "qe":
                q, add = QE[g[0].lower()]
                fy = int(g[1]) + add
                found[(f"Q{q} FY{fy % 100:02d}", fy)] += 1
            elif kind == "he":
                if g[0].lower() not in ("september", "march"):
                    continue
                h, fy = (1, int(g[1]) + 1) if g[0].lower() == "september" else (2, int(g[1]))
                found[(f"H{h} FY{fy % 100:02d}", fy)] += 1
            elif kind == "ye":
                fy = int(g[1])
                found[(f"FY{fy % 100:02d}", fy)] += 1
            else:
                if (int(g[0]) + 1) % 100 != int(g[1]):
                    continue
                fy = int(g[0]) + 1
                found[(f"FY{fy % 100:02d}", fy)] += 1
    return found


def first_pages_text(path: Path, n: int = 10) -> str:
    import pymupdf
    doc = pymupdf.open(path)
    cache = REPO_ROOT / "parsed_advanced" / "mineru" / path.relative_to(REPO_ROOT / "data").with_suffix("") / "pages.json"
    cached = {}
    if cache.exists():
        cached = {p["page"] if isinstance(p, dict) else p[0]: p["text"] if isinstance(p, dict) else p[1]
                  for p in json.loads(cache.read_text())["pages"]}
    out = []
    for i in range(min(n, doc.page_count)):
        t = doc[i].get_text()
        if len(t.strip()) < 50:
            t = cached.get(i + 1, "")
        out.append(t)
    return "\n".join(out)


def documents() -> list[dict]:
    rows = []
    for r in csv.DictReader((REPO_ROOT / "data" / "download_manifest.csv").open()):
        if r["path"] and (REPO_ROOT / r["path"]).exists() and r["path"].endswith(".pdf"):
            rows.append(r)
    seen, out = set(), []
    for r in rows:  # the manifest has one row per attempt; keep the latest per file
        if r["path"] not in seen:
            seen.add(r["path"])
            out.append(r)
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", type=Path, default=REPO_ROOT / "review" / "periods")
    ap.add_argument("--pages", type=int, default=10, help="first N pages read for the stated period")
    args = ap.parse_args(argv)
    overrides, sme = load_overrides(), sme_symbols()
    rows = []
    for r in documents():
        is_sme = r["symbol"] in sme
        rule = normalise(r["doc_type"], r["period_label"], r["filed_date"], is_sme)
        final = normalise_doc(r["path"], r["doc_type"], r["period_label"], r["filed_date"], overrides, is_sme)
        stated = stated_periods(first_pages_text(REPO_ROOT / r["path"], args.pages))
        top = stated.most_common(1)[0][0] if stated else None
        if rule["fiscal_year"] is None:
            status = "no_rule"
        elif not stated:
            status = "no_evidence"
        elif (rule["period"], rule["fiscal_year"]) in stated:
            status = "agree"          # the document states the rule's exact period
        elif any(fy == rule["fiscal_year"] for _, fy in stated):
            status = "agree_fy"       # same fiscal year, different quarter/half named
        else:
            status = "disagree"
        rows.append({"path": r["path"], "doc_type": r["doc_type"], "period_label": r["period_label"],
                     "filed_date": r["filed_date"], "rule_fy": rule["fiscal_year"], "rule_period": rule["period"],
                     "period_kind": rule["period_kind"], "stated_top": top[0] if top else "",
                     "stated_all": "; ".join(f"{p} x{c}" for (p, _), c in stated.most_common(5)),
                     "status": status, "final_fy": final["fiscal_year"], "final_period": final["period"],
                     "override": "yes" if final.get("source") == "override" else ""})
    rows.sort(key=lambda x: x["path"])
    args.out.mkdir(parents=True, exist_ok=True)
    with (args.out / "check.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    by = collections.Counter((r["doc_type"], r["status"]) for r in rows)
    for k, v in sorted(by.items()):
        print(f"{k[0]:<22} {k[1]:<12} {v}")
    print(f"{len(rows)} documents; {sum(r['override'] == 'yes' for r in rows)} overrides; wrote {args.out}/check.csv")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
