"""Score a retrieval run against the retrieval question set.

    uv run cap-slice-retrieval-score review/retrieval/bm25.jsonl
    uv run cap-slice-retrieval-score review/retrieval/bm25.jsonl --compare review/retrieval/other.jsonl

A run is any retriever's output, one JSON line per question, results ranked best first:

    {"qid": "R001", "results": [{"doc": "data/APARINDS/annual_reports/FY2023-24.pdf",
                                 "page_start": 128, "page_end": 128, "score": 12.3}, ...]}

A result "hits" a gold page when it is the same document and its page range covers that page.
Questions with match=any (most) are answered by any one gold page; match=all (multi-page questions)
need every gold page, and count as found at the rank where the last one appears.

Two answer keys (data/golden/README.md):
  strict   primary_page + answer_pages — every page checked on the page image
  lenient  strict + retrieval_answer_pages_auto.csv — pages whose text layer prints the answer's
           distinctive numbers, not individually checked (6 of 8 correct in a spot check)

Reports Recall@1/5/10/20/50 and MRR@10 overall and per group (evidence, style, company, document
type, hard-case tags with >= 10 questions), plus doc@10: the right document anywhere in the top 10
(tells "wrong document" from "right document, wrong page"). Writes <run>.score.json and
<run>.score.md next to the run. --compare gives the paired comparison at Recall@10 (strict): questions
won, lost and tied, with an exact two-sided sign test.
"""

from __future__ import annotations

import argparse
import collections
import csv
import json
import math
from pathlib import Path

from cap_slice.downloader import REPO_ROOT

GOLDEN = REPO_ROOT / "data" / "golden"
KS = (1, 5, 10, 20, 50)


def _page(ref: str) -> tuple[str, int]:
    doc, page = ref.rsplit("#", 1)
    return doc, int(page)


def load_questions() -> list[dict]:
    qs = list(csv.DictReader((GOLDEN / "retrieval_questions.csv").open()))
    auto = collections.defaultdict(set)
    for r in csv.DictReader((GOLDEN / "retrieval_answer_pages_auto.csv").open()):
        auto[r["qid"]].add(_page(r["page"]))
    for q in qs:
        strict = {(q["primary_doc"], int(q["primary_page"]))}
        strict |= {_page(x) for x in q["answer_pages"].split(";") if x}
        q["gold"] = {"strict": strict, "lenient": strict | auto[q["qid"]]}
    return qs


def load_run(path: Path) -> dict[str, list[dict]]:
    run = {}
    for line in path.read_text().splitlines():
        if line.strip():
            r = json.loads(line)
            run[r["qid"]] = r["results"]
    return run


def found_rank(results: list[dict], gold: set[tuple[str, int]], match: str) -> int | None:
    """1-based rank at which the question counts as answered, or None."""
    need = set(gold)
    for rank, res in enumerate(results, 1):
        covered = {(d, p) for d, p in gold
                   if d == res["doc"] and res["page_start"] <= p <= res["page_end"]}
        if covered and match == "any":
            return rank
        need -= covered
        if not need:
            return rank
    return None


def groups(q: dict) -> list[str]:
    g = ["all", f"evidence:{q['evidence']}", f"style:{q['style']}", f"company:{q['symbol']}",
         f"doctype:{q['primary_doc'].split('/')[2]}"]
    return g + [f"hard:{t}" for t in q["hard"].split(";") if t]


def score(run: dict[str, list[dict]], qs: list[dict]) -> dict:
    per_q = []
    for q in qs:
        res = run.get(q["qid"], [])
        row = {"qid": q["qid"], "groups": groups(q), "in_run": q["qid"] in run}
        for key in ("strict", "lenient"):
            row[key] = found_rank(res, q["gold"][key], q["match"])
        docs = {d for d, _ in q["gold"]["strict"]}
        row["doc10"] = any(r["doc"] in docs for r in res[:10])
        per_q.append(row)

    def metrics(rows: list[dict]) -> dict:
        n = len(rows)
        m = {"n": n}
        for key in ("strict", "lenient"):
            for k in KS:
                m[f"{key}_R@{k}"] = sum(r[key] is not None and r[key] <= k for r in rows) / n
            m[f"{key}_MRR@10"] = sum(1 / r[key] for r in rows if r[key] and r[key] <= 10) / n
        m["doc@10"] = sum(r["doc10"] for r in rows) / n
        return m

    by_group = collections.defaultdict(list)
    for r in per_q:
        for g in r["groups"]:
            by_group[g].append(r)
    report = {g: metrics(rows) for g, rows in sorted(by_group.items())
              if g == "all" or not g.startswith("hard:") or len(rows) >= 10}
    return {"questions": len(qs), "missing_from_run": [r["qid"] for r in per_q if not r["in_run"]],
            "groups": report, "per_question": per_q}


def sign_test(wins: int, losses: int) -> float:
    """Exact two-sided sign test p-value (ties dropped)."""
    n = wins + losses
    if n == 0:
        return 1.0
    tail = sum(math.comb(n, i) for i in range(0, min(wins, losses) + 1)) / 2 ** n
    return min(1.0, 2 * tail)


def compare(a: dict, b: dict, k: int = 10) -> dict:
    hit = lambda r: r["strict"] is not None and r["strict"] <= k  # noqa: E731
    bq = {r["qid"]: r for r in b["per_question"]}
    wins = [r["qid"] for r in a["per_question"] if hit(r) and not hit(bq[r["qid"]])]
    losses = [r["qid"] for r in a["per_question"] if not hit(r) and hit(bq[r["qid"]])]
    return {"k": k, "a_only": wins, "b_only": losses,
            "ties": len(a["per_question"]) - len(wins) - len(losses),
            "sign_test_p": sign_test(len(wins), len(losses))}


def markdown(name: str, s: dict, cmp: dict | None, other: str | None) -> str:
    cols = ["n", "strict_R@1", "strict_R@5", "strict_R@10", "strict_R@20", "strict_MRR@10",
            "lenient_R@10", "doc@10"]
    lines = [f"# Retrieval score: `{name}`", "",
             f"{s['questions']} questions; missing from run: {len(s['missing_from_run'])}. "
             "Strict = answer pages checked on the image; lenient adds machine-found pages that print "
             "the answer's numbers. doc@10 = the right document anywhere in the top 10.", "",
             "| group | " + " | ".join(cols) + " |", "|---|" + "---|" * len(cols)]
    order = sorted(s["groups"], key=lambda g: (g != "all", g.split(":")[0], -s["groups"][g]["n"], g))
    for g in order:
        m = s["groups"][g]
        cells = [str(m["n"])] + [f"{m[c]:.2f}" for c in cols[1:]]
        lines.append(f"| {g} | " + " | ".join(cells) + " |")
    if cmp:
        lines += ["", f"## Paired comparison vs `{other}` (strict Recall@{cmp['k']})", "",
                  f"Only this run finds: {len(cmp['a_only'])} ({', '.join(cmp['a_only']) or '-'})  ",
                  f"Only the other finds: {len(cmp['b_only'])} ({', '.join(cmp['b_only']) or '-'})  ",
                  f"Ties: {cmp['ties']}; exact sign test p = {cmp['sign_test_p']:.3f}"]
    missed = [r["qid"] for r in s["per_question"] if r["strict"] is None or r["strict"] > 10]
    lines += ["", f"## Not found in the top 10 (strict): {len(missed)}", "", ", ".join(missed) or "-"]
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("run", type=Path)
    ap.add_argument("--compare", type=Path, help="second run for a paired comparison")
    args = ap.parse_args(argv)
    qs = load_questions()
    s = score(load_run(args.run), qs)
    cmp = compare(s, score(load_run(args.compare), qs)) if args.compare else None
    out = args.run.with_suffix("")
    Path(f"{out}.score.json").write_text(json.dumps({**s, "compare": cmp}, indent=1, default=list))
    md = markdown(args.run.name, s, cmp, args.compare.name if args.compare else None)
    Path(f"{out}.score.md").write_text(md)
    a = s["groups"]["all"]
    print(f"{args.run.name}: strict R@1 {a['strict_R@1']:.2f}  R@5 {a['strict_R@5']:.2f}  "
          f"R@10 {a['strict_R@10']:.2f}  R@20 {a['strict_R@20']:.2f}  MRR@10 {a['strict_MRR@10']:.2f}  "
          f"| lenient R@10 {a['lenient_R@10']:.2f} | doc@10 {a['doc@10']:.2f}")
    if cmp:
        print(f"vs {args.compare.name}: +{len(cmp['a_only'])} / -{len(cmp['b_only'])} questions at R@10, "
              f"sign test p = {cmp['sign_test_p']:.3f}")
    print(f"wrote {out}.score.json and .score.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
