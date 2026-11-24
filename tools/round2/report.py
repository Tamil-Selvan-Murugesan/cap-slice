"""Round-2 comparison tables from the scored runs (review/retrieval/round2/*.score.json).

    uv run python tools/round2/report.py b1 b2 c d e > review/retrieval/round2/results.md

For every variant and filter setup: strict R@10 next to the round-1 baseline (a) and the paired win/loss
count with an exact sign test; for the production setup (question-based, soft): R@1/5/10/20, MRR@10,
lenient R@10, pages covered by the top 10, and strict R@10 per group of >= 15 questions with the
decision-rule check (overall R@10 up, no such group down by more than 0.10).
"""
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
R1 = ROOT / "review" / "retrieval"
R2 = R1 / "round2"
TAG = "voyage-4-large-2048"
SETUPS = [("none", ""), ("company", "-company"), ("company, soft", "-company-soft"),
          ("question", "-question"), ("question, soft", "-question-soft"),
          ("question + next year", "-question_next"), ("question + next year, soft", "-question_next-soft"),
          ("answer key (ceiling)", "-answer_key"), ("answer key, soft (ceiling)", "-answer_key-soft")]
PROD = "-question-soft"


def run(v, suffix):
    if v == "a":
        return R1 / f"dense-{TAG}{suffix}.jsonl"
    return R2 / f"dense-{TAG}__r2-{v}{suffix}.jsonl"


def score(p):
    return json.loads(p.with_suffix(".score.json").read_text())


def hits(p):
    return {q["qid"]: bool(q["strict"] and q["strict"] <= 10) for q in score(p)["per_question"]}


def sign_p(w, l):
    n = w + l
    if n == 0:
        return 1.0
    k = min(w, l)
    return min(1.0, 2 * sum(math.comb(n, i) for i in range(k + 1)) / 2 ** n)


def pages10(p):
    tot = []
    for line in p.open():
        r = json.loads(line)
        pages = set()
        for x in r["results"][:10]:
            pages |= {(x["doc"], n) for n in range(x["page_start"], max(x["page_start"], x["page_end"]) + 1)}
        tot.append(len(pages))
    return sum(tot) / len(tot)


def main(vs):
    out = ["# Round 2 — chunking variants (strict R@10, 200 questions)\n",
           "a = round-1 baseline. Cells: R@10 (wins / losses vs a, sign-test p).\n",
           "| Setup | a | " + " | ".join(vs) + " |", "|---|---|" + "---|" * len(vs)]
    for name, suf in SETUPS:
        base = run("a", suf)
        hb = hits(base)
        row = [name, f"{score(base)['groups']['all']['strict_R@10']:.3f}"]
        for v in vs:
            p = run(v, suf)
            if not p.with_suffix(".score.json").exists():
                row.append("–")
                continue
            hv = hits(p)
            w = sum(hv[q] and not hb[q] for q in hb)
            l = sum(hb[q] and not hv[q] for q in hb)
            row.append(f"{score(p)['groups']['all']['strict_R@10']:.3f} (+{w}/−{l}, p={sign_p(w, l):.2f})")
        out.append("| " + " | ".join(row) + " |")

    out += ["\n## Production setup (question-based, soft)\n",
            "| Variant | R@1 | R@5 | R@10 | R@20 | MRR@10 | lenient R@10 | pages in top 10 |",
            "|---|---|---|---|---|---|---|---|"]
    for v in ["a"] + vs:
        p = run(v, PROD)
        if not p.with_suffix(".score.json").exists():
            continue
        g = score(p)["groups"]["all"]
        out.append(f"| {v} | {g['strict_R@1']:.3f} | {g['strict_R@5']:.3f} | {g['strict_R@10']:.3f} | "
                   f"{g['strict_R@20']:.3f} | {g['strict_MRR@10']:.3f} | {g['lenient_R@10']:.3f} | {pages10(p):.1f} |")

    base = score(run("a", PROD))["groups"]
    groups = [k for k, g in base.items() if g["n"] >= 15 and k != "all"]
    out += ["\n## Groups of ≥ 15 questions (question-based soft, strict R@10)\n",
            "| Group | n | a | " + " | ".join(vs) + " |", "|---|---|---|" + "---|" * len(vs)]
    verdict = {}
    for k in groups:
        row = [k, str(base[k]["n"]), f"{base[k]['strict_R@10']:.2f}"]
        for v in vs:
            p = run(v, PROD)
            if not p.with_suffix(".score.json").exists():
                row.append("–")
                continue
            x = score(p)["groups"].get(k, {}).get("strict_R@10")
            d = x - base[k]["strict_R@10"]
            if d < -0.10 + 1e-9:
                verdict.setdefault(v, []).append(f"{k} {d:+.2f}")
            row.append(f"{x:.2f}" + (" ⚠" if d < -0.10 + 1e-9 else ""))
        out.append("| " + " | ".join(row) + " |")
    out += ["\n## Decision rule\n", "| Variant | R@10 vs a | wins / losses | groups down > 0.10 | passes |",
            "|---|---|---|---|---|"]
    hb = hits(run("a", PROD))
    a10 = base["all"]["strict_R@10"]
    for v in vs:
        p = run(v, PROD)
        if not p.with_suffix(".score.json").exists():
            continue
        hv = hits(p)
        w = sum(hv[q] and not hb[q] for q in hb)
        l = sum(hb[q] and not hv[q] for q in hb)
        x = score(p)["groups"]["all"]["strict_R@10"]
        bad = verdict.get(v, [])
        out.append(f"| {v} | {x:.3f} vs {a10:.3f} | +{w} / −{l} (p={sign_p(w, l):.2f}) | {', '.join(bad) or 'none'} | "
                   f"{'yes' if x > a10 and not bad else 'no'} |")
    print("\n".join(out))


if __name__ == "__main__":
    main(sys.argv[1:])
