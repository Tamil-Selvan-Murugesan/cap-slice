"""LLM-judged context metrics in the style of RAGAS (2026-11-25).

    uv run cap-slice-context-judge RUN.jsonl --set main|fresh      # judge the top 10 of a run (cached)

Label-based scores (retrieval_score.py) ask "is an answer *page* in the results?". These ask what a
generator would see: given the question, the reference answer and the top-10 retrieved chunks (the text the
answer step would get: b2s embed_text, i.e. context header + heading path + chunk), Claude Sonnet 5.5 judges

  context recall     the reference answer split into claims; share of claims a retrieved chunk supports
                     (RAGAS LLMContextRecall)
  context precision  for each chunk, whether it is useful for arriving at the reference answer; average
                     precision over the useful ranks (RAGAS LLMContextPrecisionWithReference)

These catch answering pages the answer key doesn't list, and miss nothing for being on a "wrong" copy of a
page, but they are a model's judgement, not ground truth. One call per question; the prompt is fixed before
any run and its hash is stored; verdicts are cached in review/retrieval/judge/<set>-<run>.jsonl (committed,
since the model can't be made deterministic).
"""
import argparse
import csv
import hashlib
import json
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from .downloader import REPO_ROOT
from .retrieval_rerank import load_texts

OUT = REPO_ROOT / "review" / "retrieval" / "judge"
SETS = {"main": REPO_ROOT / "data/golden/retrieval_questions.csv", "fresh": REPO_ROOT / "data/golden/fresh_questions.csv"}
MODEL = "claude-sonnet-5-5"
K = 10

SYSTEM = """You evaluate a retrieval system over the stock-exchange filings of Indian listed companies \
(annual reports, results, earnings-call transcripts, investor presentations; Indian fiscal years end in March; \
amounts may be in crore, lakh, million or full rupees).

You get a question, its reference answer (correct, written by a person who read the source pages) and numbered \
passages retrieved for the question. Each passage starts with a header naming the company, document and period.

1. Split the reference answer into its atomic claims (each figure, with what it is and the period it belongs to, \
is one claim; a qualitative statement is one claim). Use the question to make each claim self-contained. The \
reference answer may add, usually in parentheses, figures the question does not ask for (a prior year, another \
quarter, a breakdown) for the reader's reference: leave those out; make claims only from what answers the question.
2. For each claim, decide whether the passages support it: a passage supports a claim only if it states that \
fact for the same company, the same period and the same scope (standalone or consolidated) the question asks \
about; the same figure printed as a prior-year comparative in a later document counts. Arithmetic is allowed \
only to convert units or to combine figures the passages state. List the supporting passage numbers.
3. For each passage, decide whether it is useful for arriving at the reference answer (it states at least one \
of the claims, as defined above). Return one verdict per passage, in passage order.
Judge only from the passages; do not use outside knowledge."""

SCHEMA = {
    "type": "object",
    "properties": {
        "claims": {"type": "array", "items": {
            "type": "object",
            "properties": {"claim": {"type": "string"}, "supported": {"type": "boolean"},
                           "passages": {"type": "array", "items": {"type": "integer"}}},
            "required": ["claim", "supported", "passages"], "additionalProperties": False}},
        "useful": {"type": "array", "items": {"type": "boolean"}},
    },
    "required": ["claims", "useful"],
    "additionalProperties": False,
}
PROMPT_HASH = hashlib.sha256((SYSTEM + json.dumps(SCHEMA, sort_keys=True) + MODEL).encode()).hexdigest()[:12]


def user_message(q: dict, passages: list[str]) -> str:
    ref = q["answer"] + (f" (unit: {q['unit']})" if q.get("unit") else "")
    body = "\n\n".join(f"[{i}]\n{t}" for i, t in enumerate(passages, 1))
    return f"Question: {q['question']}\nReference answer: {ref}\n\nPassages ({len(passages)}):\n\n{body}"


def judge_one(client, q: dict, passages: list[str]) -> dict:
    for attempt in range(3):
        r = client.beta.messages.create(
            model=MODEL, max_tokens=8000, system=SYSTEM,
            messages=[{"role": "user", "content": user_message(q, passages)}],
            output_config={"effort": "medium", "format": {"type": "json_schema", "schema": SCHEMA}},
            betas=["server-side-fallback-2026-07-01"], fallbacks="default",
        )
        if r.stop_reason in ("refusal", "max_tokens"):
            raise SystemExit(f"{q['qid']}: stop_reason {r.stop_reason}")
        v = json.loads(next(b.text for b in r.content if b.type == "text"))
        if len(v["useful"]) == len(passages) and v["claims"]:
            return {**v, "model": r.model, "in": r.usage.input_tokens, "out": r.usage.output_tokens}
    raise SystemExit(f"{q['qid']}: verdict length mismatch after 3 tries")


def scores(v: dict) -> tuple[float, float]:
    recall = sum(c["supported"] for c in v["claims"]) / len(v["claims"])
    u = v["useful"]
    hits = sum(u)
    precision = sum(sum(u[:i + 1]) / (i + 1) for i in range(len(u)) if u[i]) / hits if hits else 0.0
    return recall, precision


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("run", type=Path)
    ap.add_argument("--set", choices=sorted(SETS), default="main")
    ap.add_argument("--corpus", default="b2s")
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args(argv)

    import anthropic
    client = anthropic.Anthropic(max_retries=5)
    qs = {r["qid"]: r for r in csv.DictReader(SETS[args.set].open())}
    run = {r["qid"]: r["results"][:K] for r in map(json.loads, args.run.open())}
    texts = load_texts(args.corpus)
    OUT.mkdir(parents=True, exist_ok=True)
    cache_path = OUT / f"{args.set}-{args.run.stem}.jsonl"
    done = {}
    if cache_path.exists():
        done = {v["qid"]: v for v in map(json.loads, cache_path.open()) if v["prompt"] == PROMPT_HASH}
    todo = [qid for qid in qs if qid in run and qid not in done][: args.limit or None]

    def work(qid):
        passages = [texts[(c["doc"], c["chunk"])] for c in run[qid]]
        v = judge_one(client, qs[qid], passages)
        return {"qid": qid, **v, "chunks": [[c["doc"], c["chunk"]] for c in run[qid]],
                "prompt": PROMPT_HASH, "date": time.strftime("%Y-%m-%d")}

    with cache_path.open("a") as f, ThreadPoolExecutor(args.workers) as ex:
        for n, v in enumerate(ex.map(work, todo), 1):
            done[v["qid"]] = v
            f.write(json.dumps(v) + "\n")
            f.flush()
            if n % 25 == 0 or n == len(todo):
                print(f"[{n}/{len(todo)}]", flush=True)

    rows = [done[q] for q in qs if q in done]
    rec, pre = zip(*map(scores, rows))
    tin, tout = sum(v["in"] for v in rows), sum(v["out"] for v in rows)
    summary = {"run": str(args.run), "set": args.set, "questions": len(rows), "k": K, "model": MODEL,
               "prompt": PROMPT_HASH, "llm_context_recall@10": round(sum(rec) / len(rec), 4),
               "llm_context_precision@10": round(sum(pre) / len(pre), 4),
               "fully_supported": round(sum(r == 1 for r in rec) / len(rec), 4),
               "tokens_in": tin, "tokens_out": tout}
    cache_path.with_suffix(".summary.json").write_text(json.dumps(summary, indent=1))
    print(json.dumps(summary, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
