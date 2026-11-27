"""
Lay out our data the way main's parser-evaluation tools expect, so they run unchanged on our corpus.

Main (commit MAIN_COMMIT) decided its parser with tools that assume its own repository layout:
  data/<SYMBOL>/<doc type dir>/<file>.pdf            source PDFs (inventory.py, number_check.py)
  data/golden/...                                    golden facts / page inventory
  <cache>/<parser>/<SYMBOL>/<doc type dir>/<file>/pages.json   {"pages": [[page_no, text], ...]}
and find the repository root from their own file location. So this builds a self-contained workspace
(default <data>/main_repl/) with:
  src/, tools/, pyproject.toml   main's code at MAIN_COMMIT (git archive, unmodified)
  data/<SYMBOL>/<dir>/<doc_id>.pdf   hard links to sets/full/pdfs/<doc_id>.pdf (the PDFs both runs parsed;
                                     not symlinks: main's doc_id_for() resolves them out of data/)
  parsed/paddleocr_vl/...        our full PaddleOCR-VL run, page text made exactly as main's adapter does
  parsed_ocr/mineru/...          our full MinerU advanced run (parse_mode=ocr), likewise
  data/golden/                   empty: our own golden sets go here

Page text: main's adapters' last step, applied to our saved per-page Markdown --
  Paddle: drop picture placeholders (IMG), then to_pipe_tables()
  MinerU: to_pipe_tables() (our .md is already MinerU's own per-page renderer, as main's adapter uses)

Needs main's package importable (to reuse its IMG / to_pipe_tables): run with the replica's venv, e.g.
  uv venv -p 3.12 <ws>/.venv && uv pip install -p <ws>/.venv pymupdf==1.28.2 pillow
  python parsing_eval/main_repl/build_workspace.py --code-only      # code first, then:
  uv pip install -p <ws>/.venv --no-deps -e <ws>
  <ws>/.venv/bin/python parsing_eval/main_repl/build_workspace.py   # data + caches
"""
import argparse
import json
import os
import sqlite3
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # parsing_eval/ (paths.py)
from paths import DB_PATH, DATA, REPO, RESULTS, SETS  # noqa: E402

MAIN_COMMIT = "5e35ee3"
# our curated_kind -> main's document-type folder (main: periodic_results for results; no credit ratings)
KIND_DIR = {"annual_report": "annual_reports", "concall_transcript": "concall_transcripts",
            "investor_presentation": "investor_presentations", "financial_results": "periodic_results",
            "credit_rating": "credit_ratings"}
RUNS = {"parsed/paddleocr_vl": "paddleocr-vl-1.6", "parsed_ocr/mineru": "mineru2.5-pro"}


def copy_code(ws: Path):
    ws.mkdir(parents=True, exist_ok=True)
    archive = subprocess.run(["git", "-C", str(REPO), "archive", MAIN_COMMIT, "src", "tools", "pyproject.toml", "README.md"],
                             check=True, capture_output=True).stdout
    subprocess.run(["tar", "-x", "-C", str(ws)], input=archive, check=True)
    (ws / "MAIN_COMMIT").write_text(MAIN_COMMIT + "\n")
    print(f"main's code at {MAIN_COMMIT} -> {ws}")


def page_text(model: str, md: str) -> str:
    from cap_slice.parsing.mineru_vlm import to_pipe_tables
    from cap_slice.parsing.paddleocr_vl import IMG
    return to_pipe_tables(IMG.sub("", md)).strip() if model.startswith("paddle") else to_pipe_tables(md)


def build_data(ws: Path):
    db = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
    docs = {r[0]: (r[1], KIND_DIR[r[2]]) for r in db.execute(
        "SELECT id, symbol, curated_kind FROM ingestion_documents WHERE ingestion_format = 'pdf'")}
    pages = defaultdict(list)
    for line in (SETS / "full" / "manifest.jsonl").read_text().splitlines():
        r = json.loads(line)
        pages[r["doc_id"]].append(r["pdf_page"])
    for doc_id, (sym, kdir) in docs.items():
        link = ws / "data" / sym / kdir / f"{doc_id}.pdf"
        link.parent.mkdir(parents=True, exist_ok=True)
        if link.is_symlink():
            link.unlink()
        if not link.exists():
            os.link(SETS / "full" / "pdfs" / f"{doc_id}.pdf", link)
    (ws / "data" / "golden").mkdir(exist_ok=True)
    print(f"{len(docs)} PDFs linked under {ws / 'data'}")

    for cache, model in RUNS.items():
        md_dir = RESULTS / "full" / model / "full" / "md"
        missing = 0
        for doc_id, (sym, kdir) in docs.items():
            out, rows = ws / cache / sym / kdir / str(doc_id), []
            for n in sorted(pages[doc_id]):
                f = md_dir / f"{doc_id}_p{n:03d}.md"
                if f.exists():
                    rows.append([n, page_text(model, f.read_text())])
                else:
                    missing += 1
            out.mkdir(parents=True, exist_ok=True)
            (out / "pages.json").write_text(json.dumps(
                {"parser": cache.split("/")[-1], "doc": str(ws / "data" / sym / kdir / f"{doc_id}.pdf"),
                 "source": f"cap-slice results/full/{model}/full", "page_count": len(pages[doc_id]),
                 "pages": rows}, ensure_ascii=False))
        print(f"{cache}: {len(docs)} documents, {missing} pages without output")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ws", type=Path, default=DATA / "main_repl")
    ap.add_argument("--code-only", action="store_true")
    a = ap.parse_args()
    if a.code_only:
        copy_code(a.ws)
    else:
        build_data(a.ws)


if __name__ == "__main__":
    main()
