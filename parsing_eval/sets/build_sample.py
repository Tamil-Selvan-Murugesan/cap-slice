"""
Build the ~800-page vision-model benchmark set (accuracy + throughput in one run).

Selection (fixed seed, reproducible):
  1. Required pages: the 15 hand-checked pack pages + every evidence page of the
     25 questions in parsing_eval/eval_set/questions.json.
  2. Per page class (from <data>/page_profile/pages.csv) up to a quota, taken as
     runs of up to RUN_LEN consecutive pages of that class, round-robin over
     documents (shuffled, interleaved by company and document kind), with at most
     DOC_CAP pages per document.
  3. A separate 16-page warm-up set that shares no page with the sample.

Output (<data>/sets/bench/, zipped to <data>/sets/bench_set.zip; <data> = paths.DATA):
  pdfs/<doc_id>.pdf      only the selected pages of each filing (sample + warm-up)
  manifest.jsonl         one row per sample page (see FIELDS)
  warmup.jsonl           warm-up pages, same format
  gold/<page_id>.txt     text-layer ground truth for born-digital control pages
  questions.json         copy of the 25-question eval set
  page_checks.json       manual per-page checks for the 15 hand-checked pages
  summary.csv            pages per class / kind / company

page_id = "<doc_id>_p<NNN>", NNN = 1-based page of the ORIGINAL filing.
Read-only with respect to cap-slice (SQLite mode=ro).

Run:
  python parsing_eval/sets/build_sample.py      (needs pymupdf; run build_pack.py first)
"""
import csv
import json
import random
import shutil
import sqlite3
from collections import Counter, defaultdict
from pathlib import Path

import pymupdf

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # parsing_eval/ (paths.py)
from paths import DB_PATH, PACK, PROFILE, QUESTIONS, SETS  # noqa: E402

PACK_MANIFEST = PACK / "manifest.json"
OUT = SETS / "bench"

SEED = 20261003
RUN_LEN = 4          # consecutive pages per run
DOC_CAP = 12         # max sampled pages per document (required pages excluded)
WARMUP_PAGES = 16
QUOTAS = {           # page_class -> pages
    "scanned_old_ocr": 200,
    "scanned_no_text": 150,
    "chart_or_graphic": 200,
    "table_dense": 150,
    "text": 80,
}
# Born-digital classes: their text layer is the ground truth for scoring.
CONTROL_CLASSES = {"table_dense", "text"}


def copy_pages(src, pages_0based):
    """Copy pages into a new PDF, keeping form fields/signature appearances. Some filings
    have broken form-field xrefs (e.g. doc 1); only for those are widgets dropped."""
    for widgets in (True, False):
        sub = pymupdf.open()
        try:
            for p in pages_0based:
                sub.insert_pdf(src, from_page=p, to_page=p, widgets=widgets)
            return sub, widgets
        except Exception:
            sub.close()
    raise RuntimeError(f"could not copy pages from {src.name}")


def load_profile():
    pages = {}
    with open(PROFILE, newline="") as f:
        for r in csv.DictReader(f):
            pages[(int(r["doc_id"]), int(r["pdf_page"]))] = r
    return pages


def required_pages():
    req = set()
    for d in json.loads(PACK_MANIFEST.read_text())["documents"]:
        req.update((d["id"], p["pdf_page"]) for p in d["pages"])
    for q in json.loads(QUESTIONS.read_text())["questions"]:
        req.update((e["doc_id"], e["pdf_page"]) for e in q["evidence"])
    return req


def runs_for(doc_pages, length):
    """Split a sorted list of page numbers into runs of consecutive pages (max `length`)."""
    runs, cur = [], []
    for p in doc_pages:
        if cur and (p != cur[-1] + 1 or len(cur) == length):
            runs.append(cur)
            cur = []
        cur.append(p)
    if cur:
        runs.append(cur)
    return runs


def interleave(docs, meta):
    """Order documents so consecutive picks alternate company and document kind."""
    buckets = defaultdict(list)
    for d in docs:
        buckets[(meta[d]["symbol"], meta[d]["kind"])].append(d)
    order, keys = [], list(buckets)
    while any(buckets.values()):
        for k in keys:
            if buckets[k]:
                order.append(buckets[k].pop())
    return order


def select(profile, required, rng):
    chosen = {key: "required" for key in required if key in profile}
    per_doc = Counter()
    meta = {d: {"symbol": r["symbol"], "kind": r["kind"]} for (d, _), r in profile.items()}

    for cls, quota in QUOTAS.items():
        have = sum(1 for k in chosen if profile[k]["page_class"] == cls)
        by_doc = defaultdict(list)
        for (d, p), r in profile.items():
            if r["page_class"] == cls and (d, p) not in chosen:
                by_doc[d].append(p)
        doc_runs = {}
        for d, ps in by_doc.items():
            rs = runs_for(sorted(ps), RUN_LEN)
            rng.shuffle(rs)
            doc_runs[d] = rs
        docs = list(doc_runs)
        rng.shuffle(docs)
        docs = interleave(docs, meta)
        progress = True
        while have < quota and progress:
            progress = False
            for d in docs:
                if have >= quota:
                    break
                if not doc_runs[d] or per_doc[d] >= DOC_CAP:
                    continue
                run = doc_runs[d].pop()[: min(RUN_LEN, DOC_CAP - per_doc[d], quota - have)]
                for p in run:
                    chosen[(d, p)] = cls
                per_doc[d] += len(run)
                have += len(run)
                progress = True
    return chosen


def pick_warmup(profile, chosen, rng):
    """One page per (class, kind) where possible, from documents/pages not in the sample."""
    pool = defaultdict(list)
    for key, r in profile.items():
        if key not in chosen:
            pool[(r["page_class"], r["kind"])].append(key)
    warm = []
    groups = list(pool)
    rng.shuffle(groups)
    while len(warm) < WARMUP_PAGES and any(pool.values()):
        for g in groups:
            if pool[g] and len(warm) < WARMUP_PAGES:
                warm.append(pool[g].pop(rng.randrange(len(pool[g]))))
    return warm


def main():
    rng = random.Random(SEED)
    profile = load_profile()
    required = required_pages()
    chosen = select(profile, required, rng)
    warmup = pick_warmup(profile, chosen, rng)

    if OUT.exists():
        shutil.rmtree(OUT)
    (OUT / "pdfs").mkdir(parents=True)
    (OUT / "gold").mkdir()

    db = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
    paths = dict(db.execute("SELECT id, ingestion_path FROM ingestion_documents"))

    by_doc = defaultdict(list)
    for d, p in list(chosen) + warmup:
        by_doc[d].append(p)

    sample_rows, warm_rows = [], []
    warm_set = set(warmup)
    for d in sorted(by_doc):
        pages = sorted(by_doc[d])
        src = pymupdf.open(paths[d])
        sub, kept_widgets = copy_pages(src, [p - 1 for p in pages])
        if not kept_widgets:
            print(f"  doc {d}: form fields dropped (broken in source)")
        run_id, prev = None, None
        for idx, p in enumerate(pages):
            if prev is None or p != prev + 1:
                run_id = f"{d}_r{p:03d}"
            prev = p
            r = profile[(d, p)]
            reason = "warmup" if (d, p) in warm_set else chosen[(d, p)]
            control = r["page_class"] in CONTROL_CLASSES
            row = {
                "page_id": f"{d}_p{p:03d}", "doc_id": d, "pdf_page": p,
                "pdf": f"pdfs/{d}.pdf", "page_no": idx, "run_id": run_id,
                "symbol": r["symbol"], "kind": r["kind"], "filing_date": r["filing_date"],
                "page_class": r["page_class"], "selected_as": reason,
                "control": control,
            }
            if control and (d, p) not in warm_set:
                (OUT / "gold" / f"{row['page_id']}.txt").write_text(
                    src[p - 1].get_text(), encoding="utf-8")
            (warm_rows if (d, p) in warm_set else sample_rows).append(row)
        sub.save(OUT / "pdfs" / f"{d}.pdf", garbage=3, deflate=True)
        sub.close()
        src.close()

    for name, rows in (("manifest.jsonl", sample_rows), ("warmup.jsonl", warm_rows)):
        with open(OUT / name, "w") as f:
            for r in rows:
                f.write(json.dumps(r) + "\n")
    shutil.copy(QUESTIONS, OUT / "questions.json")
    # Per-page manual checks (row attribution, chart values) for the 15 hand-checked pages
    checks = [{"page_id": f"{d['id']}_p{pg['pdf_page']:03d}", "category": pg["category"],
               "why_hard": pg["why_hard"], "check": pg["check"]}
              for d in json.loads(PACK_MANIFEST.read_text())["documents"] for pg in d["pages"]]
    (OUT / "page_checks.json").write_text(json.dumps(checks, indent=2, ensure_ascii=False))

    summary = Counter((r["page_class"], r["kind"], r["symbol"]) for r in sample_rows)
    with open(OUT / "summary.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["page_class", "kind", "symbol", "pages"])
        for k, n in sorted(summary.items()):
            w.writerow([*k, n])

    archive = shutil.make_archive(str(SETS / "bench_set"), "zip", OUT)
    cls = Counter(r["page_class"] for r in sample_rows)
    print(f"sample: {len(sample_rows)} pages from {len({r['doc_id'] for r in sample_rows})} docs "
          f"| warm-up: {len(warm_rows)} pages")
    print("by class:", dict(cls))
    print("by selection:", dict(Counter(r["selected_as"] for r in sample_rows)))
    print("by company:", dict(Counter(r["symbol"] for r in sample_rows)))
    print("by kind:", dict(Counter(r["kind"] for r in sample_rows)))
    print(f"control pages with gold: {len(list((OUT / 'gold').iterdir()))}")
    print(f"zip -> {archive} ({Path(archive).stat().st_size / 1e6:.1f} MB)")


if __name__ == "__main__":
    main()
