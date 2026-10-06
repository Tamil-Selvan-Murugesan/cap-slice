"""Number fidelity of parser output on digital pages, measured against the PDF's own text layer.

    uv run python tools/golden/number_check.py parsed_advanced/mineru parsed/paddleocr_vl ...

No golden facts needed: on a page with a real text layer and (almost) no pictures, every number a
parser outputs should also be printed in the text layer. For each parser cache (pages after
page_clean.py, i.e. the text that would be chunked):

  precision   share of the parser's numbers that the page's text layer contains
  changed     parser numbers NOT on the page that differ from a number on the page by exactly one
              digit (same length) or by two swapped neighbouring digits — the misread signature
              (5,882.60 -> 5,892.60)
  other       remaining parser numbers not on the page (invented, merged, split, mis-tokenised)
  missed      share of the text layer's numbers absent from the parser output

Numbers: at least 3 digits (so note references and single digits don't dominate); commas, Indian or
Western grouping, signs and brackets ignored ("(1,57,280.58)" == "157280.58"). Pages: no low-text flag,
>= 300 characters of text, image cover < 10 % (page_inventory.csv). Only pages every given parser has.
"""

from __future__ import annotations

import csv
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

import pymupdf

from cap_slice.page_clean import clean_pages

NUM = re.compile(r"\d[\d,]*(?:\.\d+)?")


def numbers(text: str) -> set[str]:
    out = set()
    for m in NUM.finditer(text):
        s = m.group().rstrip(",").replace(",", "")
        if s.endswith("."):
            s = s[:-1]
        if sum(ch.isdigit() for ch in s) >= 3:
            out.add(s)
    return out


def one_digit_off(a: str, pool: set[str]) -> bool:
    for b in pool:
        if len(a) != len(b):
            continue
        diff = [i for i, (x, y) in enumerate(zip(a, b)) if x != y]
        if len(diff) == 1:
            return True
        if len(diff) == 2 and diff[1] == diff[0] + 1 and a[diff[0]] == b[diff[1]] and a[diff[1]] == b[diff[0]]:
            return True
    return False


def main() -> None:
    roots = [Path(a) for a in sys.argv[1:]]
    inv = defaultdict(dict)
    for r in csv.DictReader(open("data/golden/page_inventory.csv")):
        if r["low_text"] == "0" and int(r["chars"]) >= 300 and float(r["image_cover"] or 0) < 0.1:
            inv[r["doc"]][int(r["page"])] = r["doc_type"]
    parsed = {}
    for root in roots:
        parsed[root] = {}
        for f in root.glob("*/*/*/pages.json"):
            doc = "data/" + str(f.parent.relative_to(root)) + ".pdf"
            if doc in inv:
                pages = json.load(open(f))["pages"]
                parsed[root][doc] = dict(clean_pages(pages, Path(doc))[0])
    docs = sorted(set.intersection(*(set(p) for p in parsed.values())))
    stats = {root: Counter() for root in roots}
    by_type = {root: defaultdict(Counter) for root in roots}
    examples = {root: [] for root in roots}
    npages = 0
    for doc in docs:
        with pymupdf.open(doc) as pdf:
            for n, dtype in inv[doc].items():
                if not all(n in parsed[root][doc] for root in roots):
                    continue
                truth = numbers(pdf[n - 1].get_text())
                if len(truth) < 5:
                    continue
                npages += 1
                for root in roots:
                    got = numbers(parsed[root][doc][n])
                    ok = got & truth
                    bad = got - truth
                    changed = {x for x in bad if one_digit_off(x, truth)}
                    s = stats[root]
                    s["out"] += len(got); s["ok"] += len(ok); s["changed"] += len(changed)
                    s["other"] += len(bad) - len(changed); s["truth"] += len(truth); s["missed"] += len(truth - got)
                    t = by_type[root][dtype]
                    t["out"] += len(got); t["ok"] += len(ok); t["changed"] += len(changed)
                    if changed and len(examples[root]) < 8:
                        x = sorted(changed)[0]
                        examples[root].append(f"{doc[5:]} p{n}: {x}")
    print(f"{npages} digital pages from {len(docs)} documents (all parsers present)\n")
    print(f"{'parser':28} {'numbers out':>11} {'precision':>9} {'changed':>8} {'per 10k':>7} {'other':>7} {'missed':>7}")
    for root in roots:
        s = stats[root]
        print(f"{str(root):28} {s['out']:>11,} {s['ok'] / s['out']:>9.2%} {s['changed']:>8,} "
              f"{1e4 * s['changed'] / s['out']:>7.1f} {s['other']:>7,} {s['missed'] / s['truth']:>7.2%}")
    print("\nchanged digits per 10,000 numbers, by document type")
    types = sorted({t for r in roots for t in by_type[r]})
    print(f"{'':28}" + "".join(f"{t[:14]:>16}" for t in types))
    for root in roots:
        print(f"{str(root):28}" + "".join(
            f"{1e4 * by_type[root][t]['changed'] / max(by_type[root][t]['out'], 1):>16.1f}" for t in types))
    for root in roots:
        print(f"\nexamples, {root}:", *examples[root], sep="\n  ")


if __name__ == "__main__":
    main()
