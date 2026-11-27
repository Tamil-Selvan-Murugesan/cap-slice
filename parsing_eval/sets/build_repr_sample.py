"""
Representative sample for the full-vision decision: ~600 pages drawn uniformly at random from ALL pages of
the 369 selected PDFs (<data>/page_profile/pages.csv), so the page mix (mostly born-digital annual-report
text, some scans/charts) matches the real corpus. Used to measure realistic throughput (incl. parallel
clients) and full-vision accuracy on typical pages.

Output: <data>/sets/repr/ (zipped to <data>/sets/repr_set.zip), same layout as the bench set:
  pdfs/<doc_id>.pdf, manifest.jsonl, warmup.jsonl, gold/<page_id>.txt (born-digital pages), summary.csv
Warm-up pages are disjoint from the sample. Read-only with respect to cap-slice (SQLite mode=ro).

Run:
  python parsing_eval/sets/build_repr_sample.py
"""
import csv
import json
import random
import shutil
import sqlite3
from collections import Counter, defaultdict
from pathlib import Path

import pymupdf

from build_sample import CONTROL_CLASSES, DB_PATH, PROFILE, SETS, copy_pages

OUT = SETS / "repr"
SEED = 20261004
N_PAGES = 600
WARMUP_PAGES = 16


def main():
    rng = random.Random(SEED)
    with open(PROFILE, newline="") as f:
        profile = {(int(r["doc_id"]), int(r["pdf_page"])): r for r in csv.DictReader(f)}
    keys = sorted(profile)
    rng.shuffle(keys)
    sample, warmup = keys[:N_PAGES], keys[N_PAGES:N_PAGES + WARMUP_PAGES]

    if OUT.exists():
        shutil.rmtree(OUT)
    (OUT / "pdfs").mkdir(parents=True)
    (OUT / "gold").mkdir()
    db = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
    paths = dict(db.execute("SELECT id, ingestion_path FROM ingestion_documents"))

    by_doc = defaultdict(list)
    for d, p in sample + warmup:
        by_doc[d].append(p)
    warm_set = set(warmup)
    rows = {"manifest.jsonl": [], "warmup.jsonl": []}
    for d in sorted(by_doc):
        pages = sorted(by_doc[d])
        src = pymupdf.open(paths[d])
        sub, kept_widgets = copy_pages(src, [p - 1 for p in pages])
        for idx, p in enumerate(pages):
            r = profile[(d, p)]
            control = r["page_class"] in CONTROL_CLASSES
            row = {"page_id": f"{d}_p{p:03d}", "doc_id": d, "pdf_page": p, "pdf": f"pdfs/{d}.pdf",
                   "page_no": idx, "run_id": f"{d}_p{p:03d}", "symbol": r["symbol"], "kind": r["kind"],
                   "filing_date": r["filing_date"], "page_class": r["page_class"],
                   "selected_as": "warmup" if (d, p) in warm_set else "random", "control": control}
            if control and (d, p) not in warm_set:
                (OUT / "gold" / f"{row['page_id']}.txt").write_text(src[p - 1].get_text(), encoding="utf-8")
            rows["warmup.jsonl" if (d, p) in warm_set else "manifest.jsonl"].append(row)
        sub.save(OUT / "pdfs" / f"{d}.pdf", garbage=3, deflate=True)
        sub.close()
        src.close()

    for name, rs in rows.items():
        with open(OUT / name, "w") as f:
            for r in rs:
                f.write(json.dumps(r) + "\n")
    summ = Counter((r["page_class"], r["kind"]) for r in rows["manifest.jsonl"])
    with open(OUT / "summary.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["page_class", "kind", "pages"])
        for k, n in sorted(summ.items()):
            w.writerow([*k, n])
    archive = shutil.make_archive(str(SETS / "repr_set"), "zip", OUT)

    m = rows["manifest.jsonl"]
    corpus = Counter(r["page_class"] for r in profile.values())
    print(f"sample: {len(m)} pages from {len({r['doc_id'] for r in m})} docs | warm-up {len(rows['warmup.jsonl'])}")
    for cls, n in Counter(r["page_class"] for r in m).most_common():
        print(f"  {cls:18s} {n:4d} ({100*n/len(m):4.1f}%)   corpus {100*corpus[cls]/len(profile):4.1f}%")
    print("by kind:", dict(Counter(r["kind"] for r in m)))
    print(f"control pages with gold: {len(list((OUT / 'gold').iterdir()))}")
    print(f"zip -> {archive} ({Path(archive).stat().st_size / 1e6:.1f} MB)")


if __name__ == "__main__":
    main()
