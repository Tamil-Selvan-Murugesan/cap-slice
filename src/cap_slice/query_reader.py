"""Question reader: question text -> filters (company, fiscal years, document type). Rules only, no API calls.

    uv run cap-slice-query-reader             # evaluate on the retrieval set -> review/query_reader/

    read("What was APAR's EBITDA in the December 2023 quarter?")
      -> {"symbol": "APARINDS", "fiscal_years": [2024], "doc_type": None, "periods": ["Q3 FY24"], ...}

Sees only the question — never the answer key. Production would run the same function on a user's
question, so its mistakes are part of what the retrieval experiments measure (docs/plan.md, Filters).

fiscal_years uses the same scale as the documents (periods.py): the year the Indian FY (April-March)
ends. A question can give several (comparisons) or none (no period named -> no year filter):

  FY2020-21, FY 2020-21, 2020-21, FY21              -> 2021
  Q3 FY24, H1 FY24, 9M FY24                         -> 2024
  December 2023 quarter, quarter ended Dec 2023     -> Q3 FY24 -> 2024
  six months to September 2023                      -> H1 FY24 -> 2024
  year to March 2019, at March 31, 2024             -> 2019, 2024
  at 31 December 2021, end of June 2020             -> 2022, 2021 (the quarter that date ends)
  the August 2018 call, July 2024 presentation      -> the document's own year: periods.py event rule
                                                       (Aug 2018 -> Q1 FY19 -> 2019; half-year for SME)
  other months ("in May 2023")                     -> the month's FY and the FY of a call/deck held then:
                                                       2024, 2023
  a bare calendar year ("in 2025", "2018 IPO")      -> both fiscal years it touches: 2025, 2026

Two document types named ("call ... slides") -> no doc-type filter.
"""

from __future__ import annotations

import argparse
import collections
import csv
import json
import re
from pathlib import Path

from cap_slice.downloader import REPO_ROOT
from cap_slice.periods import _event_half, _event_quarter, sme_symbols

COMPANIES = {  # alias regex -> symbol
    r"\bapar\b": "APARINDS",
    r"\bhero\b": "HEROMOTOCO",
    r"\be2e\b": "E2E",
    r"\besconet\b": "ESCONET",
    r"\bc2c\b": "C2C",
}
DOC_TYPES = [  # first match wins; only explicit mentions
    (r"\b(?:con(?:ference)?[- ]?calls?|earnings calls?|calls?|transcripts?|analysts? meet)\b", "concall_transcript"),
    (r"\b(?:presentations?|decks?|slides?|investor update)\b", "investor_presentation"),
    (r"\b(?:annual reports?|chairman'?s (?:message|letter)|directors'? report|board'?s report|"
     r"management discussion|corporate governance report)\b", "annual_report"),
]
MONTHS = {m: i for i, m in enumerate("jan feb mar apr may jun jul aug sep oct nov dec".split(), 1)}
MON = r"(jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|june?|july?|aug(?:ust)?|sep(?:t(?:ember)?)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)"
DAY = r"(?:\d{1,2}(?:st|nd|rd|th)?\s+)?"
YEAR = r"((?:19|20)\d\d)"


def _m(name: str) -> int:
    return MONTHS[name[:3].lower()]


def _fy_of_month(month: int, year: int) -> int:
    """Fiscal year containing a calendar month (April-March)."""
    return year + 1 if month >= 4 else year


def _quarter_of_month(month: int, year: int) -> tuple[int, int]:
    fy = _fy_of_month(month, year)
    return {4: 1, 5: 1, 6: 1, 7: 2, 8: 2, 9: 2, 10: 3, 11: 3, 12: 3, 1: 4, 2: 4, 3: 4}[month], fy


def _fy2(s: str) -> int:
    return 2000 + int(s) if len(s) == 2 else int(s)


def read(question: str) -> dict:
    q = question
    out = {"symbol": None, "fiscal_years": [], "doc_type": None, "periods": [], "event": False, "evidence": []}
    for rx, sym in COMPANIES.items():
        if re.search(rx, q, re.I):
            out["symbol"] = sym
            break
    named = {dt for rx, dt in DOC_TYPES if re.search(rx, q, re.I)}
    if len(named) == 1:  # cues for two types ("call ... slides") -> no doc-type filter
        out["doc_type"] = named.pop()
    sme = out["symbol"] in sme_symbols()
    fys, periods, taken = [], [], []

    def add(span, fy, period=None, note=""):
        if any(a < span[1] and span[0] < b for a, b in taken):
            return
        taken.append(span)
        fys.append(fy)
        if period:
            periods.append(period)
        out["evidence"].append(f"{q[span[0]:span[1]]!r}{' ' + note if note else ''}")

    pats = [
        # Q3 FY24, H1 FY2023-24, 9M FY24, Q3 & 9M FY24
        (rf"\b(Q[1-4]|H[12]|9M)\s*(?:(?:&|and)\s*(?:9M|H[12])\s*)?FY\s*'?(\d{{4}})\s*[-–]\s*(\d{{2}})\b",
         lambda m: (int(m[2]) + 1, f"{m[1].upper()} FY{(int(m[2]) + 1) % 100:02d}")),
        (rf"\b(Q[1-4]|H[12]|9M)\s*(?:(?:&|and)\s*(?:9M|H[12])\s*)?FY\s*'?(\d{{4}}|\d{{2}})\b",
         lambda m: (_fy2(m[2]), f"{m[1].upper()} FY{_fy2(m[2]) % 100:02d}")),
        # FY2020-21, FY 2020-21, 2020-21
        (r"\b(?:FY\s*'?)?((?:19|20)\d\d)\s*[-–/]\s*(\d{2})\b",
         lambda m: (int(m[1]) + 1, f"FY{(int(m[1]) + 1) % 100:02d}") if (int(m[1]) + 1) % 100 == int(m[2]) else None),
        (r"\bFY\s*'?(\d{2})\s*[-–]\s*(\d{2})\b",                       # FY 25-26
         lambda m: (2000 + int(m[2]), f"FY{m[2]}") if (int(m[1]) + 1) % 100 == int(m[2]) else None),
        (r"\bFY\s*'?(\d{4}|\d{2})\b", lambda m: (_fy2(m[1]), f"FY{_fy2(m[1]) % 100:02d}")),
        # the December 2023 quarter / quarter ended (31) December 2023 / three months to Dec 2023
        (rf"\b{MON}\s+{YEAR}\s+quarter\b",
         lambda m: (lambda qf: (qf[1], f"Q{qf[0]} FY{qf[1] % 100:02d}"))(_quarter_of_month(_m(m[1]), int(m[2])))),
        (rf"\b(?:quarter|three months)\s+(?:ended|ending|to|through)\s+(?:on\s+)?{DAY}{MON},?\s+{DAY}{YEAR}",
         lambda m: (lambda qf: (qf[1], f"Q{qf[0]} FY{qf[1] % 100:02d}"))(_quarter_of_month(_m(m[1]), int(m[2])))),
        # six months / half year to September 2023
        (rf"\b(?:six months|half[- ]year|first half|second half)\s+(?:ended|ending|to|through)\s+(?:on\s+)?{DAY}{MON},?\s+{DAY}{YEAR}",
         lambda m: (_fy_of_month(_m(m[1]), int(m[2])),
                    f"H{1 if _m(m[1]) <= 9 and _m(m[1]) >= 4 else 2} FY{_fy_of_month(_m(m[1]), int(m[2])) % 100:02d}")),
        # year to / ended March 2019
        (rf"\b(?:year|twelve months|fiscal)\s+(?:ended|ending|to|through)\s+(?:on\s+)?{DAY}{MON},?\s+{DAY}{YEAR}",
         lambda m: (_fy_of_month(_m(m[1]), int(m[2])), f"FY{_fy_of_month(_m(m[1]), int(m[2])) % 100:02d}")),
    ]
    for rx, f in pats:
        for m in re.finditer(rx, q, re.I):
            r = f(m)
            if r:
                add(m.span(), r[0], r[1])

    # an event: "the August 2018 call", "July 2024 corporate presentation", "as explained in January 2026"
    for m in re.finditer(rf"\b{MON},?\s+{YEAR}\b(?=[^.?]{{0,40}}\b(?:call|presentation|deck|transcript|meet|investor day|charts?|conference|update|interview))|"
                         rf"\b(?:call|presentation|deck|transcript|meet|explained|said|stated|told|reiterated|guided|announced|commented|noted|according to)\b[^.?]{{0,25}}?\b(?:in|on|of)\s+{MON},?\s+{YEAR}\b",
                         q, re.I):
        mon, yr = (m[1], m[2]) if m[1] else (m[3], m[4])
        month, year = _m(mon), int(yr)
        part, fy = _event_half(month, year) if sme else _event_quarter(month, year)
        out["event"] = True
        add(m.span(), fy, f"{'H' if sme else 'Q'}{part} FY{fy % 100:02d}", "(event)")

    # a date: at/as of/end of (31) March 2024, 31 December 2021, end of June 2020
    for m in re.finditer(rf"\b{DAY}{MON},?\s+{DAY}{YEAR}\b", q, re.I):
        month, year = _m(m[1]), int(m[2])
        if month in (3, 6, 9, 12):
            qn, fy = _quarter_of_month(month, year)
            add(m.span(), fy, f"FY{fy % 100:02d}" if month == 3 else f"Q{qn} FY{fy % 100:02d}", "(date)")
        else:  # "in May 2023": data from that month, or a call/deck held then (May 2023 -> Q4 FY23)
            part, efy = _event_half(month, year) if sme else _event_quarter(month, year)
            before = len(fys)
            add(m.span(), _fy_of_month(month, year), None, "(month)")
            if len(fys) > before:
                fys.append(efy)

    # a bare calendar year: both fiscal years it touches
    for m in re.finditer(r"\b((?:19|20)\d\d)\b", q):
        y = int(m[1])
        if 2005 <= y <= 2035:
            before = len(fys)
            add(m.span(), y, None, "(calendar year)")
            if len(fys) > before:
                fys.append(y + 1)

    out["fiscal_years"] = sorted(set(fys))
    out["periods"] = periods
    return out


# ---- evaluation on the retrieval set ----

def _period_fys(period_col: str) -> set[int]:
    fys = set()
    for p in period_col.split(";"):
        p = p.strip()
        if m := re.match(r"FY(\d{4})-(\d{2})", p):
            fys.add(int(m[1]) + 1)
        elif m := re.match(r"(?:Q[1-4]|H[12]|9M)\s*FY(\d{2})", p):
            fys.add(2000 + int(m[1]))
    return fys


def doc_meta() -> dict[str, dict]:
    """path -> {symbol, doc_type, fiscal_year} for every downloaded document (periods.py)."""
    from cap_slice.periods import documents, load_overrides, normalise_doc
    ov, sme = load_overrides(), sme_symbols()
    meta = {}
    for r in documents():
        n = normalise_doc(r["path"], r["doc_type"], r["period_label"], r["filed_date"], ov, r["symbol"] in sme)
        meta[r["path"]] = {"symbol": r["symbol"], "doc_type": r["doc_type"], "fiscal_year": n["fiscal_year"]}
    return meta


def keeps(f: dict, m: dict, use: tuple[str, ...], next_year: bool = False) -> bool:
    """Does filter f (from read() or the answer key) keep a document with metadata m?
    next_year: also keep the following fiscal year (filings repeat last year's figures as comparatives)."""
    if "symbol" in use and f.get("symbol") and m["symbol"] != f["symbol"]:
        return False
    if "year" in use and f.get("fiscal_years"):
        years = set(f["fiscal_years"]) | ({y + 1 for y in f["fiscal_years"]} if next_year else set())
        if m["fiscal_year"] not in years:
            return False
    if "doc_type" in use and f.get("doc_type") and m["doc_type"] != f["doc_type"]:
        return False
    return True


def answer_key_filter(q: dict, meta: dict) -> dict:
    """Upper bound: the gold primary document's own metadata (never a production number)."""
    m = meta[q["primary_doc"]]
    return {"symbol": m["symbol"], "fiscal_years": [m["fiscal_year"]], "doc_type": m["doc_type"]}


HISTORY = """**First run, before any change (2026-10-19):** company 200/200; year right 180, wrong 6, none 14; doc type
right 28, wrong 1; hard company + year filter keeps an answer page for 186/200. Three general phrasings
were then fixed — `FY 25-26` read as FY25 and FY22; an event named by "investor day charts" or
"reiterated in May 2023" not recognised; a call named next to slides given a doc-type filter — giving
the numbers below. Because those fixes were made on this set, treat the result as slightly optimistic."""


def FILTERS(read_f: dict, key_f: dict) -> list[tuple]:  # noqa: N802
    """(name, filter, fields used, next_year) for every filter setup reported."""
    return [("company", read_f, ("symbol",), False),
            ("company_year", read_f, ("symbol", "year"), False),
            ("company_year_next", read_f, ("symbol", "year"), True),
            ("company_year_type", read_f, ("symbol", "year", "doc_type"), False),
            ("company_year_next_type", read_f, ("symbol", "year", "doc_type"), True),
            ("answer_key", key_f, ("symbol", "year", "doc_type"), False)]


def main(argv: list[str] | None = None) -> int:
    from cap_slice.retrieval_score import load_questions
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", type=Path, default=REPO_ROOT / "review" / "query_reader")
    args = ap.parse_args(argv)
    qs, meta = load_questions(), doc_meta()
    chunks_per_doc = collections.Counter()
    cpath = REPO_ROOT / "parsed_advanced" / "_chunks" / "mineru.jsonl"
    if cpath.exists():
        for line in cpath.open():
            chunks_per_doc[json.loads(line)["doc"]] += 1
    total = sum(chunks_per_doc.values())

    rows = []
    for q in qs:
        r = read(q["question"])
        want = _period_fys(q["period"])
        gold_docs = {d for d, _ in q["gold"]["strict"]}
        row = {"qid": q["qid"], "question": q["question"], "period": q["period"], "evidence": q["evidence"],
               "style": q["style"], "symbol_ok": r["symbol"] == q["symbol"],
               "years": ";".join(map(str, r["fiscal_years"])), "doc_type": r["doc_type"] or "",
               "read_periods": ";".join(r["periods"]), "read_evidence": " | ".join(r["evidence"])}
        if not r["fiscal_years"]:
            row["year_status"] = "none"
        elif want & set(r["fiscal_years"]):
            row["year_status"] = "hit"
        else:
            row["year_status"] = "miss"
        row["doc_type_status"] = ("none" if not r["doc_type"] else
                                  "hit" if r["doc_type"] == meta[q["primary_doc"]]["doc_type"] else "miss")
        # does a hard filter keep the gold page(s)? (match=all needs every gold document kept)
        for name, f, use, nxt in FILTERS(r, answer_key_filter(q, meta)):
            kept = [d for d in gold_docs if keeps(f, meta[d], use, nxt)]
            row[f"keeps_{name}"] = (len(kept) == len(gold_docs)) if q["match"] == "all" else bool(kept)
            pool = sum(n for d, n in chunks_per_doc.items() if keeps(f, meta[d], use, nxt))
            row[f"pool_{name}"] = pool
        rows.append(row)

    args.out.mkdir(parents=True, exist_ok=True)
    with (args.out / "readings.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)

    n = len(rows)
    yc = collections.Counter(r["year_status"] for r in rows)
    dc = collections.Counter(r["doc_type_status"] for r in rows)
    median = lambda xs: sorted(xs)[len(xs) // 2]  # noqa: E731
    lines = ["# Question reader", "",
             f"Rules-based reader (`src/cap_slice/query_reader.py`) on the {n} retrieval questions; reads only the "
             "question text. Year checked against the `period` column (what the question asks about, recorded "
             "when the set was built).", "", HISTORY, "",
             "| | Count |", "|---|---|",
             f"| Company read correctly | {sum(r['symbol_ok'] for r in rows)} / {n} |",
             f"| Year: read and right (includes the asked year) | {yc['hit']} |",
             f"| Year: read but wrong | {yc['miss']} |",
             f"| Year: none read (no year filter) | {yc['none']} |",
             f"| Doc type: read and right | {dc['hit']} |",
             f"| Doc type: read but wrong | {dc['miss']} |",
             f"| Doc type: none read | {dc['none']} |", "",
             "**Does a hard filter keep an answer page?** (if not, the question cannot be answered under that filter)", "",
             f"| Filter | Keeps an answer page | Median pool (chunks of {total:,}) |", "|---|---|---|"]
    for name, label in [("company", "Company (question-based)"), ("company_year", "Company + year (question-based)"),
                        ("company_year_next", "Company + year or the next year (question-based)"),
                        ("company_year_type", "Company + year + doc type (question-based)"),
                        ("company_year_next_type", "Company + year or the next year + doc type (question-based)"),
                        ("answer_key", "Company + year + doc type (answer key, upper bound)")]:
        lines.append(f"| {label} | {sum(r[f'keeps_{name}'] for r in rows)} / {n} | "
                     f"{median([r[f'pool_{name}'] for r in rows]):,} |")
    lost = [r for r in rows if r["keeps_company"] and not r["keeps_company_year_type"]]
    lines += ["", f"## Questions a question-based hard filter makes unanswerable: {len(lost)}", "",
              "| qid | question | period | read years | doc type | evidence |", "|---|---|---|---|---|---|"]
    for r in lost:
        lines.append(f"| {r['qid']} | {r['question']} | {r['period']} | {r['years']} | {r['doc_type']} | "
                     f"{r['read_evidence']} |")
    (args.out / "README.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines[7:26]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
