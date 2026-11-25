"""Multi-query expansion for questions whose answer spans several pages (2026-11-25).

    uv run cap-slice-query-expand plan            # Sonnet 5.5 decides single/multi and writes sub-queries (cached)
    uv run cap-slice-query-expand questions       # sub-queries as a question file for the dense search / reranker
    uv run cap-slice-query-expand merge           # merged runs A / B / C -> review/retrieval/expand/

    --questions CSV --out-dir DIR (before the command) run the same steps on another question set, e.g. the
    fresh set: plans, sub-queries and merged runs then live in DIR.

Each question goes to Claude Sonnet 5.5 once. If one search can answer it, nothing changes: the production run is
used as is. Otherwise its 2-4 self-contained sub-queries (one fact each, naming company, period and scope) each run
through the production pipeline (question-reader soft filter -> dense top 100 -> rerank-3 top 50 against the
sub-query), and the lists are merged:

  A  union of the sub-query lists and the original's, reranked against the original question
  B  round-robin: the best chunk of each list in turn (original first), then the second best, ...; duplicates skipped
  C  reciprocal rank fusion (k = 60) over the same lists

Plans are cached in review/retrieval/expand/plans.jsonl (committed): the model can't be made deterministic
(sampling parameters are not accepted), so the cached plans are what every run uses. The prompt below is fixed
before any run and is not tuned on the test questions; its hash is stored with each plan.
"""
import argparse
import csv
import hashlib
import json
import time
from pathlib import Path

from .downloader import REPO_ROOT

QUESTIONS = REPO_ROOT / "data" / "golden" / "retrieval_questions.csv"
OUT = REPO_ROOT / "review" / "retrieval" / "expand"
PLANS = OUT / "plans.jsonl"
SUBQ = OUT / "subqueries.csv"
MODEL = "claude-sonnet-5-5"
RRF_K = 60
TOP = 50

SYSTEM = """You prepare search queries for a retrieval system over the stock-exchange filings of five Indian listed \
companies: APAR Industries, E2E Networks, Esconet Technologies, C2C Advanced Systems and Hero MotoCorp. The filings \
are annual reports, quarterly or half-yearly results, earnings-call transcripts and investor presentations, from \
about FY2012 to FY2027 (Indian fiscal years end in March).

The retrieval system returns single passages, each from one page or a few neighbouring pages of one document. A \
question whose answer needs facts from different documents, periods or statements (for example growth between two \
years, a comparison of two periods or of standalone and consolidated figures, guidance that changed between two \
calls) needs one search per fact.

Decide whether the question needs more than one search.
- If one search can find everything the answer needs, set "multi" to false and return no queries.
- Otherwise set "multi" to true and return 2 to 4 search queries. Each query asks for exactly one fact and is \
self-contained: it names the company, the period (as the question states or clearly implies it) and, when the \
question gives them, the statement scope (standalone or consolidated) and the kind of document.
Do not answer the question. Do not add facts, figures or periods the question does not state or clearly imply.
Give a one-sentence reason."""

SCHEMA = {
    "type": "object",
    "properties": {
        "multi": {"type": "boolean"},
        "queries": {"type": "array", "items": {"type": "string"}},
        "reason": {"type": "string"},
    },
    "required": ["multi", "queries", "reason"],
    "additionalProperties": False,
}
PROMPT_HASH = hashlib.sha256((SYSTEM + json.dumps(SCHEMA, sort_keys=True) + MODEL).encode()).hexdigest()[:12]


def questions() -> list[dict]:
    return list(csv.DictReader(QUESTIONS.open()))


def set_paths(questions_csv: Path, out_dir: Path) -> None:
    global QUESTIONS, OUT, PLANS, SUBQ
    QUESTIONS, OUT = questions_csv.resolve(), out_dir.resolve()
    PLANS, SUBQ = OUT / "plans.jsonl", OUT / "subqueries.csv"


def load_plans() -> dict[str, dict]:
    if not PLANS.exists():
        return {}
    return {p["qid"]: p for p in map(json.loads, PLANS.open()) if p["prompt"] == PROMPT_HASH}


def cmd_plan(args) -> int:
    import anthropic
    client = anthropic.Anthropic(max_retries=5)
    done = load_plans()
    todo = [q for q in questions() if q["qid"] not in done][: args.limit or None]
    OUT.mkdir(parents=True, exist_ok=True)
    tokens_in = tokens_out = 0
    with PLANS.open("a") as f:
        for n, q in enumerate(todo, 1):
            r = client.beta.messages.create(
                model=MODEL, max_tokens=4000, system=SYSTEM,
                messages=[{"role": "user", "content": q["question"]}],
                output_config={"effort": "medium", "format": {"type": "json_schema", "schema": SCHEMA}},
                betas=["server-side-fallback-2026-07-01"], fallbacks="default",
            )
            if r.stop_reason == "refusal":
                raise SystemExit(f"{q['qid']}: refused ({r.stop_details})")
            if r.stop_reason == "max_tokens":
                raise SystemExit(f"{q['qid']}: hit max_tokens")
            plan = json.loads(next(b.text for b in r.content if b.type == "text"))
            if not plan["multi"]:
                plan["queries"] = []
            tokens_in += r.usage.input_tokens
            tokens_out += r.usage.output_tokens
            f.write(json.dumps({"qid": q["qid"], "question": q["question"], **plan, "model": r.model,
                                "prompt": PROMPT_HASH, "date": time.strftime("%Y-%m-%d")}) + "\n")
            f.flush()
            if n % 20 == 0 or n == len(todo):
                print(f"[{n}/{len(todo)}] {tokens_in:,} in / {tokens_out:,} out tokens", flush=True)
    plans = load_plans()
    multi = [p for p in plans.values() if p["multi"]]
    print(f"{len(plans)} plans ({PROMPT_HASH}): {len(multi)} multi, {sum(len(p['queries']) for p in multi)} sub-queries")
    return 0


def cmd_questions(args) -> int:
    rows = [{"qid": f"{p['qid']}#{i}", "question": s}
            for p in load_plans().values() if p["multi"] for i, s in enumerate(p["queries"], 1)]
    with SUBQ.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["qid", "question"])
        w.writeheader()
        w.writerows(rows)
    print(f"wrote {SUBQ.relative_to(REPO_ROOT)}: {len(rows)} sub-queries")
    return 0


def read(path: Path) -> dict[str, list[dict]]:
    return {r["qid"]: r["results"] for r in map(json.loads, path.open())}


def _key(c):
    return (c["doc"], c["chunk"])


def round_robin(lists: list[list[dict]], top: int) -> list[dict]:
    out, seen = [], set()
    for depth in range(max(map(len, lists), default=0)):
        for lst in lists:
            if depth < len(lst) and _key(lst[depth]) not in seen:
                seen.add(_key(lst[depth]))
                out.append(lst[depth])
                if len(out) == top:
                    return out
    return out


def rrf(lists: list[list[dict]], top: int) -> list[dict]:
    score, first = {}, {}
    for lst in lists:
        for rank, c in enumerate(lst, 1):
            score[_key(c)] = score.get(_key(c), 0) + 1 / (RRF_K + rank)
            first.setdefault(_key(c), c)
    return [first[k] for k in sorted(score, key=lambda k: -score[k])][:top]


def cmd_merge(args) -> int:
    plans = load_plans()
    prod = read(args.production)
    sub = read(args.sub) if args.sub.exists() else {}
    out_b, out_c, union = [], [], []
    for q in questions():
        qid, p = q["qid"], plans.get(q["qid"])
        lists = [prod[qid]] + ([sub[f"{qid}#{i}"] for i in range(1, len(p["queries"]) + 1)] if p and p["multi"] else [])
        out_b.append({"qid": qid, "results": round_robin(lists, TOP)})
        out_c.append({"qid": qid, "results": rrf(lists, TOP)})
        seen, u = set(), []
        for lst in lists:
            for c in lst:
                if _key(c) not in seen:
                    seen.add(_key(c))
                    u.append(c)
        union.append({"qid": qid, "results": u})
    for name, rows in (("B-roundrobin", out_b), ("C-rrf", out_c), ("A-union-candidates", union)):
        path = OUT / f"expand-{name}.jsonl"
        path.write_text("".join(json.dumps(r) + "\n" for r in rows))
        print(f"wrote {path.relative_to(REPO_ROOT)}")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--questions", type=Path, default=QUESTIONS, help="qid,question CSV (default: the 200 questions)")
    ap.add_argument("--out-dir", type=Path, default=OUT, help="plans, sub-queries and merged runs")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("plan")
    p.add_argument("--limit", type=int, default=0)
    sub.add_parser("questions")
    m = sub.add_parser("merge")
    m.add_argument("--production", type=Path,
                   default=REPO_ROOT / "review/retrieval/s22/dense-b2s-question-soft-top100-rerank-rerank-3-d50.jsonl")
    m.add_argument("--sub", type=Path, help="reranked sub-query run (default: in --out-dir)")
    args = ap.parse_args(argv)
    set_paths(args.questions, args.out_dir)
    if args.cmd == "merge" and args.sub is None:
        args.sub = OUT / "dense-b2s-subqueries-question-soft-top100-rerank-rerank-3-d50.jsonl"
    return {"plan": cmd_plan, "questions": cmd_questions, "merge": cmd_merge}[args.cmd](args)


if __name__ == "__main__":
    raise SystemExit(main())
