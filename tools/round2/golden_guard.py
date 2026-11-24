"""Golden facts v1-v3 at L4 on the text a variant returns, against the baseline (round 2 guard).

    uv run python tools/round2/golden_guard.py d e

Scores every fact with compare_parsers.score_fact against the variant's returned chunks (`text`) of the
fact's document, exactly as cap-slice-score --clean does for the baseline; lists any fact whose level drops.
"""
import collections
import csv
import json
import sys

from cap_slice.compare_parsers import OutChunk, score_fact
from cap_slice.downloader import REPO_ROOT

G = REPO_ROOT / "data" / "golden"
CH = REPO_ROOT / "parsed_advanced" / "_chunks"


def facts():
    paths = {d["key"]: d["path"] for d in csv.DictReader((G / "compare_docs.csv").open())}
    out = []
    for name, f in (("v1", "parse_facts.csv"), ("v2", "v2_facts.csv"), ("v3", "v3_facts.csv")):
        for r in csv.DictReader((G / f).open()):
            if "path" not in r:
                r["path"] = paths[r["doc"]]
            r["set"] = name
            out.append(r)
    return out


def by_doc(path):
    d = collections.defaultdict(list)
    seen = set()
    for l in path.open():
        c = json.loads(l)
        key = (c["doc"], c.get("parent", c["chunk"]))
        if key in seen:  # small-to-big: score each returned parent once
            continue
        seen.add(key)
        d[c["doc"]].append(OutChunk(len(d[c["doc"]]), c["kind"], c["text"], c["section"], c["page_start"], c["page_end"], []))
    return d


def levels(chunks, fs):
    return {f"{f['set']}:{f['id']}": score_fact(f, chunks.get(f["path"], []))[0] for f in fs}


fs = facts()
base = levels(by_doc(CH / "mineru.jsonl"), fs)
for v in sys.argv[1:]:
    lv = levels(by_doc(CH / f"r2-{v}.jsonl"), fs)
    tot = lambda L, s: sum(1 for k, x in L.items() if k.startswith(s) and x >= 4)  # noqa: E731
    print(f"{v}: L4 v1 {tot(base,'v1')}->{tot(lv,'v1')}, v2 {tot(base,'v2')}->{tot(lv,'v2')}, v3 {tot(base,'v3')}->{tot(lv,'v3')}")
    worse = [(k, base[k], lv[k]) for k in base if lv[k] < base[k]]
    better = [(k, base[k], lv[k]) for k in base if lv[k] > base[k]]
    print(f"   worse {len(worse)}: {worse}\n   better {len(better)}: {better}")
