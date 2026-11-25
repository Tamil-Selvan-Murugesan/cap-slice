"""Fresh retrieval question set (2026-11-25): seeded candidate pages, excluding everything already used.

    uv run python tools/golden/fresh_candidates.py draw --out DIR      # DIR/candidates.csv
    uv run python tools/golden/retrieval_candidates.py render DOC PAGE --out DIR    # page images (same tool)
    uv run python tools/golden/retrieval_candidates.py find SYMBOL "TEXT" ...       # pages printing a value

Same pools as the 200-question set (tools/golden/retrieval_candidates.py), a new seed, and wider exclusions:
golden v1 documents, the pages carrying v2/v3 facts, and every page of the 200 questions (strict answer
pages and the machine-found lenient pages). Chart and KPI pages are drawn from the slide and annual-report
graphic pools; multi-page questions start from a drawn page and add the same metric from another period's
filing. Questions are written from the first suitable pages in seeded order; unsuitable pages are recorded
in data/golden/fresh_skipped.csv. Every answer is read off a rendered page image, never from a parser.
"""

from __future__ import annotations

import argparse
import csv
import random
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from retrieval_candidates import GOLDEN, POOLS, excluded  # noqa: E402

SEED = 20261125


def used_by_retrieval_set() -> set[tuple[str, int]]:
    pages = set()
    for r in csv.DictReader((GOLDEN / "retrieval_questions.csv").open()):
        pages.add((r["primary_doc"], int(r["primary_page"])))
        for x in filter(None, r["answer_pages"].split(";")):
            d, p = x.rsplit("#", 1)
            pages.add((d, int(p)))
    for r in csv.DictReader((GOLDEN / "retrieval_answer_pages_auto.csv").open()):
        d, p = r["page"].rsplit("#", 1)
        pages.add((d, int(p)))
    return pages


def draw(out: Path) -> None:
    skip_docs, skip_pages = excluded()
    skip_pages |= used_by_retrieval_set()
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
                    w.writerow([f"F-{pool}-{sym[:4]}-{k:02d}", pool, sym, k, r["doc"], r["page"], r["doc_type"],
                                r["words"], r["numbers"], r["low_text"]])
    print(f"wrote {out / 'candidates.csv'} ({len(skip_pages)} pages excluded)")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    d = sub.add_parser("draw")
    d.add_argument("--out", required=True, type=Path)
    a = ap.parse_args()
    draw(a.out)


if __name__ == "__main__":
    main()
