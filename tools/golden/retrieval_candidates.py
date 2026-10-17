"""Retrieval question set: seeded candidate pages per evidence pool and company, and page renders.

    uv run python tools/golden/retrieval_candidates.py draw --out /tmp/rq        # candidates.csv
    uv run python tools/golden/retrieval_candidates.py render DOC PAGE --out /tmp/rq [--width 1400] [--clip y0,y1]
    uv run python tools/golden/retrieval_candidates.py find SYMBOL "TEXT" ["TEXT" ...]   # pages containing text
    uv run python tools/golden/retrieval_candidates.py alts      # -> data/golden/retrieval_answer_pages_auto.csv

`draw` shuffles each pool with a fixed seed and lists the pages in that order, at most one page per
document per pool, so questions are written from the first *suitable* pages in seeded order rather than
from pages picked for being easy. Unsuitable pages (blank, cover, nothing a user would ask about) are
skipped and recorded in retrieval_skipped.csv. Documents in golden v1 are excluded (the chunker was
tuned on them), and so are the exact pages that already carry v2/v3 facts.

`find` lists every page of a company whose PDF text layer contains all the given strings (commas and
spaces ignored). `alts` does this for every non-multi question: it takes up to two distinctive numbers from
the answer (>= 5 digits, not round thousands) and lists the other pages of the same company whose text
layer contains them — the "lenient" answer pages, not individually checked (see data/golden/README.md).

Every answer is read off a rendered page image, never from a parser's output.
"""

from __future__ import annotations

import argparse
import csv
import random
import re
from collections import defaultdict
from pathlib import Path

import pymupdf

GOLDEN = Path("data/golden")
SEED = 20261017


def n(r: dict, k: str) -> float:
    return float(r[k] or 0)


POOLS = {
    # primary financial statements and their notes (annual reports, results)
    "statement": lambda r: r["low_text"] == "0" and r["statement"] == "1",
    # other number-dense tables: segments, highlights, ratios, ownership, remuneration, results columns
    "table": lambda r: r["low_text"] == "0" and r["statement"] == "0" and n(r, "numbers") >= 40
    and r["doc_type"] in ("annual_report", "periodic_result"),
    # slides: charts, KPI tiles, tables on slides
    "slide": lambda r: r["doc_type"] == "investor_presentation" and r["low_text"] == "0" and 8 <= n(r, "numbers") <= 120,
    # graphic pages inside annual reports (highlights, charts)
    "ar_graphic": lambda r: r["doc_type"] == "annual_report" and r["low_text"] == "0" and 8 <= n(r, "numbers") <= 60
    and n(r, "words") < 300 and n(r, "image_cover") < 0.9,
    # annual-report prose: MD&A, directors' report, risks, policies
    "prose": lambda r: r["doc_type"] == "annual_report" and r["low_text"] == "0" and n(r, "words") >= 400
    and n(r, "numbers") <= 25,
    # concall pages with an analyst question
    "concall": lambda r: r["doc_type"] == "concall_transcript" and r["has_question"] == "1",
    # image-only pages: scanned statements, letters, pasted slides
    "scan": lambda r: r["low_text"] == "1",
}


def excluded() -> tuple[set[str], set[tuple[str, int]]]:
    docs = {r["path"] for r in csv.DictReader((GOLDEN / "compare_docs.csv").open())}
    pages = set()
    for name, key in (("v2_facts.csv", "path"), ("v3_facts.csv", "path")):
        pages |= {(r[key], int(r["page"])) for r in csv.DictReader((GOLDEN / name).open())}
    return docs, pages


def draw(out: Path) -> None:
    skip_docs, skip_pages = excluded()
    rows = [r for r in csv.DictReader((GOLDEN / "page_inventory.csv").open())
            if r["doc"] not in skip_docs and (r["doc"], int(r["page"])) not in skip_pages]
    rng = random.Random(SEED)
    out.mkdir(parents=True, exist_ok=True)
    with (out / "candidates.csv").open("w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["cand_id", "pool", "symbol", "rank", "doc", "page", "doc_type", "words", "numbers", "low_text"])
        for pool, test in POOLS.items():
            by_sym = defaultdict(list)
            for r in rows:
                if test(r):
                    by_sym[r["symbol"]].append(r)
            for sym in sorted(by_sym):
                cands = by_sym[sym]
                rng.shuffle(cands)
                seen, k = set(), 0
                for r in cands:
                    if r["doc"] in seen:
                        continue
                    seen.add(r["doc"])
                    k += 1
                    w.writerow([f"{pool}-{sym[:4]}-{k:02d}", pool, sym, k, r["doc"], r["page"], r["doc_type"],
                                r["words"], r["numbers"], r["low_text"]])
                print(f"{pool:11} {sym:11} {len(cands):5} pages, {k:3} candidates (one per document)")


def render(doc: str, page: int, out: Path, width: int, clip: str | None) -> None:
    out.mkdir(parents=True, exist_ok=True)
    with pymupdf.open(doc) as pdf:
        p = pdf[page - 1]
        rect = p.rect
        if clip:
            y0, y1 = (float(v) for v in clip.split(","))
            rect = pymupdf.Rect(rect.x0, rect.y0 + y0 * rect.height, rect.x1, rect.y0 + y1 * rect.height)
        zoom = width / rect.width
        pix = p.get_pixmap(matrix=pymupdf.Matrix(zoom, zoom), clip=rect)
    name = re.sub(r"[^A-Za-z0-9]+", "_", doc[5:-4]) + f"_p{page}" + (f"_{clip.replace(',', '-')}" if clip else "") + ".png"
    pix.save(out / name)
    print(out / name)


def norm(s: str) -> str:
    return re.sub(r"[\s,]+", "", s).lower()


def find(symbol: str, needles: list[str]) -> None:
    keys = [norm(x) for x in needles]
    for pdf_path in sorted(Path("data", symbol).glob("*/*.pdf")):
        with pymupdf.open(pdf_path) as pdf:
            for i, p in enumerate(pdf, 1):
                t = norm(p.get_text())
                if all(k in t for k in keys):
                    print(f"{pdf_path},{i}")


def alts() -> None:
    rows = list(csv.DictReader((GOLDEN / "retrieval_questions.csv").open()))
    text = {}
    for sym in sorted({r["symbol"] for r in rows}):
        for pdf_path in sorted(Path("data", sym).glob("*/*.pdf")):
            with pymupdf.open(pdf_path) as pdf:
                for i, p in enumerate(pdf, 1):
                    text[(str(pdf_path), i)] = norm(p.get_text())
    out = []
    for r in rows:
        if r["evidence"] == "multi":
            continue
        nums = [m.group() for m in re.finditer(r"\d[\d,]*\.\d+|\d{1,3}(?:,\d{2,3})+", r["answer"])]
        keys = [norm(x) for x in nums if sum(c.isdigit() for c in x) >= 5][:2]
        if not keys or all(re.fullmatch(r"\d+0{3}(\.0+)?", k) for k in keys):
            continue
        known = {(r["primary_doc"], int(r["primary_page"]))}
        known |= {(x.split("#")[0], int(x.split("#")[1])) for x in r["answer_pages"].split(";") if x}
        for (d, p), t in text.items():
            if d.startswith(f"data/{r['symbol']}/") and (d, p) not in known and all(k in t for k in keys):
                out.append([r["qid"], f"{d}#{p}", "|".join(keys), "machine_found"])
    with (GOLDEN / "retrieval_answer_pages_auto.csv").open("w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["qid", "page", "matched_numbers", "status"])
        w.writerows(out)
    print(f"{len(out)} candidate pages for {len({o[0] for o in out})} questions")


def main() -> None:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    d = sub.add_parser("draw")
    d.add_argument("--out", required=True)
    r = sub.add_parser("render")
    r.add_argument("doc")
    r.add_argument("page", type=int)
    r.add_argument("--out", required=True)
    r.add_argument("--width", type=int, default=1400)
    r.add_argument("--clip", help="vertical fraction range, e.g. 0,0.5 for the top half")
    f = sub.add_parser("find")
    f.add_argument("symbol")
    f.add_argument("needles", nargs="+")
    sub.add_parser("alts")
    a = ap.parse_args()
    if a.cmd == "draw":
        draw(Path(a.out))
    elif a.cmd == "render":
        render(a.doc, a.page, Path(a.out), a.width, a.clip)
    elif a.cmd == "alts":
        alts()
    else:
        find(a.symbol, a.needles)


if __name__ == "__main__":
    main()
