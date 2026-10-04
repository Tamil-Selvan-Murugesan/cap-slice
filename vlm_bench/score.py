"""Accuracy scoring for the benchmark set (stdlib only; run on the pod or locally).

Uses the per-page markdown every runner saves (results/<model>/<run>/md/<page_id>.md)
and the benchmark set built by parsing_eval/sets/build_sample.py.

Three checks:
  1. Control pages (born-digital, gold/<page_id>.txt = PDF text layer = ground truth).
     Pages whose text layer is not real text (shifted-glyph fonts, symbol soup, legacy-font
     Indic newspaper pages) are excluded and counted as gold_unreliable_pages:
       num_recall     share of gold numbers found in the output (multiset)
       num_precision  share of output numbers that are in the gold (low = invented numbers)
       word_f1        bag-of-words F1 against the gold text
  2. Questions (questions.json, must_contain): does the text of each question's evidence
     pages contain every string the answer needs? Necessary, not sufficient - it does not
     prove the value sits in the right row/column.
  3. Non-control pages (scans, charts; no ground truth): number agreement between models.
     Lowest-agreement pages go to disagreements.csv for manual review.

  python score.py --results /workspace/results --bench /workspace/data/bench_set
  python score.py ... --runs paddleocr-vl-1.6=c64 glm-ocr=w8 unlimited-ocr=c64_k1

Without --runs, each model's fastest single-page run (highest pages_per_s) over the full
set is scored; smoke / --limit runs are ignored.
Outputs in --results: score_summary.csv, score_pages.csv, score_questions.csv,
disagreements.csv
"""
import argparse
import csv
import html
import json
import re
import statistics
from collections import Counter
from itertools import combinations
from pathlib import Path

NUM = re.compile(r"\d[\d,]*(?:\.\d+)?")
WORD = re.compile(r"[a-z0-9]+(?:\.[0-9]+)?")
TAGS = re.compile(r"</?[A-Za-z][A-Za-z0-9]*(?:\s[^<>]*)?/?>")   # real HTML tags only, not "<1x"
COMMENT_LABEL = re.compile(r"<!--\s*(?:header:|image text|image)?\s*|\s*-->")
MIN_GOLD_CHARS = 50


def gold_reliable(text: str) -> bool:
    """False when the PDF text layer is not real text, so it cannot serve as ground truth:
    fonts with a shifted glyph mapping (e.g. 'ANNEXURE' stored as '$11(;85(' -> few vowels),
    symbol soup, or legacy-font Indic text (few ASCII letters). Seen on ~13 of 230 control pages."""
    chars = [c for c in text if not c.isspace()]
    letters = [c.lower() for c in text if c.isascii() and c.isalpha()]
    if len(letters) >= 200 and sum(c in "aeiou" for c in letters) / len(letters) < 0.24:
        return False
    if len(chars) >= 200 and len(letters) / len(chars) < 0.30:
        return False
    return True


def plain(md: str) -> str:
    """Markdown/HTML -> plain text: keep comment payloads (headers, image text), drop tags."""
    t = COMMENT_LABEL.sub(" ", md)
    t = TAGS.sub(" ", t)
    t = html.unescape(t)
    t = re.sub(r"[#*`|_]+", " ", t)
    return re.sub(r"\s+", " ", t).strip()


def numbers(text: str) -> Counter:
    out = Counter()
    for m in NUM.findall(text):
        n = m.replace(",", "").rstrip(".")
        if len(n.replace(".", "")) >= 2:      # skip single digits (note refs, list markers)
            out[n] += 1
    return out


def words(text: str) -> Counter:
    return Counter(WORD.findall(text.lower()))


def norm(s: str) -> str:
    s = re.sub(r"(?<=\d),(?=\d)", "", s.lower())
    return re.sub(r"\s+", " ", s).strip()


def overlap(a: Counter, b: Counter) -> int:
    return sum((a & b).values())


def pick_runs(results: Path, explicit: list[str]) -> dict[str, Path]:
    if explicit:
        return {m: results / m / r for m, r in (x.split("=", 1) for x in explicit)}
    summaries = [(s, json.loads(s.read_text())) for s in results.glob("*/*/summary.json")]
    full = {}                                      # largest page count seen per model
    for _, j in summaries:
        full[j["model"]] = max(full.get(j["model"], 0), j.get("pages", 0))
    best = {}
    for s, j in summaries:
        if j.get("pages_per_request", 1) != 1:     # multi-page runs have no per-page markdown
            continue
        if j.get("pages", 0) < 0.9 * full[j["model"]]:   # smoke / --limit runs
            continue
        if j.get("empty_outputs", 0) > 0.01 * max(j.get("pages", 0), 1):
            # e.g. GLM w8/w16: layout OOM -> pages silently empty -> fake high pages/s
            print(f"skipping {j['model']}/{j['run']}: {j['empty_outputs']} empty outputs")
            continue
        if j.get("pages_per_s", 0) > best.get(j["model"], (0, None))[0]:
            best[j["model"]] = (j["pages_per_s"], s.parent)
    return {m: d for m, (_, d) in best.items()}


def load_md(run: Path, page_id: str) -> str | None:
    p = run / "md" / f"{page_id}.md"
    return p.read_text(errors="replace") if p.exists() else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", required=True)
    ap.add_argument("--bench", required=True, help="dir with manifest.jsonl, gold/, questions.json")
    ap.add_argument("--runs", nargs="*", default=[], help="model=run_name")
    a = ap.parse_args()

    results, bench = Path(a.results), Path(a.bench)
    rows = [json.loads(l) for l in (bench / "manifest.jsonl").read_text().splitlines() if l.strip()]
    runs = pick_runs(results, a.runs)
    if not runs:
        raise SystemExit("no runs found")
    print("scoring:", {m: str(d) for m, d in runs.items()})

    page_rows, per_model = [], {m: {"missing": 0, "empty": 0, "ctrl": []} for m in runs}
    texts = {}                                    # (model, page_id) -> plain text
    for r in rows:
        pid = r["page_id"]
        gold_path = bench / "gold" / f"{pid}.txt"
        gold = gold_path.read_text() if r.get("control") and gold_path.exists() else None
        if gold is not None and len(gold.strip()) < MIN_GOLD_CHARS:
            gold = None
        bad_gold = gold is not None and not gold_reliable(gold)
        if bad_gold:
            gold = None
        for m, run in runs.items():
            md = load_md(run, pid)
            if md is None:
                per_model[m]["missing"] += 1
                continue
            t = plain(md)
            texts[(m, pid)] = t
            if not t:
                per_model[m]["empty"] += 1
            rec = {"model": m, "page_id": pid, "page_class": r["page_class"], "kind": r["kind"],
                   "control": bool(gold), "gold_unreliable": bad_gold, "chars": len(t)}
            if gold:
                gn, on = numbers(gold), numbers(t)
                gw, ow = words(gold), words(t)
                hit_n, hit_w = overlap(gn, on), overlap(gw, ow)
                rec["num_recall"] = round(hit_n / sum(gn.values()), 4) if gn else None
                rec["num_precision"] = round(hit_n / sum(on.values()), 4) if on else None
                p = hit_w / sum(ow.values()) if ow else 0
                rc = hit_w / sum(gw.values()) if gw else 0
                rec["word_f1"] = round(2 * p * rc / (p + rc), 4) if p + rc else 0.0
                per_model[m]["ctrl"].append(rec)
            page_rows.append(rec)

    # ---- questions
    qf = bench / "questions.json"   # optional (the representative sample has none)
    qs = json.loads(qf.read_text())["questions"] if qf.exists() else []
    q_rows = []
    for q in qs:
        pids = [f"{e['doc_id']}_p{e['pdf_page']:03d}" for e in q["evidence"]]
        for m in runs:
            hay = norm(" ".join(texts.get((m, p), "") for p in pids))
            found = [s for s in q["must_contain"] if norm(s) in hay]
            q_rows.append({"model": m, "id": q["id"], "difficulty": q["difficulty"],
                           "requires": "+".join(q["requires"]),
                           "found": len(found), "needed": len(q["must_contain"]),
                           "supported": len(found) == len(q["must_contain"]),
                           "missing": "; ".join(s for s in q["must_contain"] if s not in found)})

    # ---- agreement on non-control pages
    dis_rows, agree = [], {m: [] for m in runs}
    for r in rows:
        if r.get("control") or len(runs) < 2:
            continue
        pid = r["page_id"]
        nums = {m: numbers(texts.get((m, pid), "")) for m in runs}
        pair_scores = []
        for x, y in combinations(runs, 2):
            u = sum((nums[x] | nums[y]).values())
            pair_scores.append(((x, y), overlap(nums[x], nums[y]) / u if u else 1.0))
        for m in runs:
            mine = [s for (pair, s) in pair_scores if m in pair]
            agree[m].append(statistics.mean(mine))
        worst = min(s for _, s in pair_scores)
        only = {m: sorted((nums[m] - sum((nums[o] for o in runs if o != m), Counter())).keys())[:15]
                for m in runs}
        dis_rows.append({"page_id": pid, "page_class": r["page_class"], "kind": r["kind"],
                         "min_pair_agreement": round(worst, 3),
                         **{f"only_in_{m}": " ".join(v) for m, v in only.items()}})
    dis_rows.sort(key=lambda d: d["min_pair_agreement"])

    # ---- summary
    def mean(xs):
        xs = [x for x in xs if x is not None]
        return round(statistics.mean(xs), 4) if xs else None

    summary = []
    for m in runs:
        ctrl = per_model[m]["ctrl"]
        mq = [q for q in q_rows if q["model"] == m]
        s = {"model": m, "run": runs[m].name, "pages": len(rows),
             "missing": per_model[m]["missing"], "empty": per_model[m]["empty"],
             "control_pages": len(ctrl),
             "gold_unreliable_pages": sum(1 for r in page_rows
                                          if r["model"] == m and r.get("gold_unreliable")),
             "num_recall": mean(c["num_recall"] for c in ctrl),
             "num_precision": mean(c["num_precision"] for c in ctrl),
             "word_f1": mean(c["word_f1"] for c in ctrl)}
        for cls in ("table_dense", "text"):
            s[f"num_recall_{cls}"] = mean(c["num_recall"] for c in ctrl if c["page_class"] == cls)
        for diff in ("easy", "medium", "hard"):
            sub = [q for q in mq if q["difficulty"] == diff]
            s[f"questions_{diff}"] = f"{sum(q['supported'] for q in sub)}/{len(sub)}"
        s["questions_total"] = f"{sum(q['supported'] for q in mq)}/{len(mq)}"
        s["agreement_noncontrol"] = mean(agree[m])
        summary.append(s)

    def write(name, data):
        if not data:
            return
        with open(results / name, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(dict.fromkeys(k for d in data for k in d)))
            w.writeheader()
            w.writerows(data)

    write("score_summary.csv", summary)
    write("score_pages.csv", page_rows)
    write("score_questions.csv", q_rows)
    write("disagreements.csv", dis_rows)

    cols = ["model", "run", "missing", "empty", "num_recall", "num_precision", "word_f1",
            "questions_easy", "questions_medium", "questions_hard", "questions_total",
            "agreement_noncontrol"]
    width = {c: max(len(c), *(len(str(s.get(c))) for s in summary)) for c in cols}
    print("  ".join(c.ljust(width[c]) for c in cols))
    for s in summary:
        print("  ".join(str(s.get(c)).ljust(width[c]) for c in cols))
    print(f"\ndetails: {results}/score_pages.csv, score_questions.csv, disagreements.csv")


if __name__ == "__main__":
    main()
