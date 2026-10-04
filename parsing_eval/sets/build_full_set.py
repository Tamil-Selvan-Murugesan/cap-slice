"""
Full-corpus set for the full-vision run: EVERY page of every selected PDF (ingestion_documents, pdf).

Output: <data>/sets/full/ (rsync this folder to the pod; no zip — 1.5 GB of PDFs)
  pdfs/<doc_id>.pdf     the original filing, copied whole (renamed to its document id)
  manifest.jsonl        one row per page: page_id "<doc_id>_p<NNN>" (1-based), pdf, page_no (0-based),
                        symbol, kind, filing_date, page_class (from page_profile), control
  warmup.jsonl          16 random pages of the corpus (also processed in the main run; warm-up output is
                        discarded, so nothing is skipped)
  gold/<page_id>.txt    PDF text layer for born-digital pages (page_class text / table_dense), so score.py
                        can measure full-vision accuracy on the whole corpus (unreliable layers are
                        excluded by score.py's gold_reliable())
  summary.csv           pages per page_class / kind / company
Read-only with respect to cap-slice (SQLite mode=ro).

Run:
  python parsing_eval/sets/build_full_set.py
"""
import csv
import json
import random
import shutil
import sqlite3
from collections import Counter
from pathlib import Path

import pymupdf

from build_sample import CONTROL_CLASSES, DB_PATH, PROFILE, SETS

OUT = SETS / "full"
SEED = 20261004
WARMUP_PAGES = 16


def main():
    pymupdf.TOOLS.mupdf_display_errors(False)
    with open(PROFILE, newline="") as f:
        profile = {(int(r["doc_id"]), int(r["pdf_page"])): r for r in csv.DictReader(f)}
    db = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
    docs = db.execute(
        """SELECT id, symbol, curated_kind, filing_date, ingestion_path FROM ingestion_documents
           WHERE ingestion_format = 'pdf' ORDER BY id""").fetchall()

    if OUT.exists():
        shutil.rmtree(OUT)
    (OUT / "pdfs").mkdir(parents=True)
    (OUT / "gold").mkdir()

    rows = []
    for doc_id, symbol, kind, filing_date, path in docs:
        shutil.copy(path, OUT / "pdfs" / f"{doc_id}.pdf")
        src = pymupdf.open(path)
        for i, page in enumerate(src):
            p = i + 1
            prof = profile.get((doc_id, p), {})
            page_class = prof.get("page_class", "unknown")
            control = page_class in CONTROL_CLASSES
            row = {"page_id": f"{doc_id}_p{p:03d}", "doc_id": doc_id, "pdf_page": p,
                   "pdf": f"pdfs/{doc_id}.pdf", "page_no": i, "run_id": f"{doc_id}",
                   "symbol": symbol, "kind": kind, "filing_date": filing_date,
                   "page_class": page_class, "selected_as": "full", "control": control}
            if control:
                (OUT / "gold" / f"{row['page_id']}.txt").write_text(page.get_text(), encoding="utf-8")
            rows.append(row)
        src.close()

    with open(OUT / "manifest.jsonl", "w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    rng = random.Random(SEED)
    with open(OUT / "warmup.jsonl", "w") as f:
        for r in rng.sample(rows, WARMUP_PAGES):
            f.write(json.dumps(r) + "\n")
    summ = Counter((r["page_class"], r["kind"], r["symbol"]) for r in rows)
    with open(OUT / "summary.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["page_class", "kind", "symbol", "pages"])
        for k, n in sorted(summ.items()):
            w.writerow([*k, n])

    size = sum(p.stat().st_size for p in OUT.rglob("*") if p.is_file())
    print(f"{len(docs)} PDFs, {len(rows)} pages -> {OUT} ({size / 1e9:.2f} GB)")
    print("by class:", dict(Counter(r["page_class"] for r in rows)))
    print("by kind:", dict(Counter(r["kind"] for r in rows)))
    print(f"gold files: {sum(1 for r in rows if r['control'])}")


if __name__ == "__main__":
    main()
