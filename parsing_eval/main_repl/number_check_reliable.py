"""
Main's number-fidelity check (tools/golden/number_check.py), unchanged, but only on pages whose PDF text
layer is real text.

Main's check treats the text layer as ground truth. Some of our PDFs use fonts with a shifted glyph map
(e.g. Reliance AR 2017-18, doc 9: "Quantities" stored as "4XDQWLWLHV"), so numbers the parsers read
correctly are counted as "changed". This writes a filtered page inventory (pages passing
vlm_bench/score.py's gold_reliable()) into a side workspace that links to the same PDFs and caches, and
runs main's script there.

  <ws>/.venv/bin/python parsing_eval/main_repl/number_check_reliable.py   # -> <ws>/reliable/review/number_fidelity/
  ... --exclude-docs 9 --name reliable_no_doc9   # also drop whole documents (doc 9's table fonts are garbled although
                                         # its body text passes gold_reliable) -> <ws>/reliable_no_doc9/
"""
import argparse
import csv
import os
import subprocess
import sys
from pathlib import Path

import pymupdf

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "vlm_bench"))
from score import gold_reliable  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from paths import DATA  # noqa: E402

WS = DATA / "main_repl"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--exclude-docs", nargs="*", default=[], help="document ids to drop entirely")
    ap.add_argument("--name", default="reliable")
    a = ap.parse_args()
    SIDE = WS / a.name
    (SIDE / "data" / "golden").mkdir(parents=True, exist_ok=True)
    for d in list((WS / "data").iterdir()) + [WS / "parsed", WS / "parsed_ocr", WS / "tools"]:
        if d.name == "golden":
            continue
        link = SIDE / ("data" if d.parent.name == "data" else "") / d.name
        if not link.exists():
            link.symlink_to(d)
    rows = list(csv.DictReader((WS / "data/golden/page_inventory.csv").open()))
    keep, dropped, docs = [], 0, {}
    for r in rows:
        if Path(r["doc"]).stem in a.exclude_docs:
            continue
        eligible = r["low_text"] == "0" and int(r["chars"]) >= 300 and float(r["image_cover"] or 0) < 0.1
        if eligible:
            if r["doc"] not in docs:
                docs[r["doc"]] = pymupdf.open(WS / r["doc"])
            if not gold_reliable(docs[r["doc"]][int(r["page"]) - 1].get_text()):
                dropped += 1
                continue
        keep.append(r)
    with (SIDE / "data/golden/page_inventory.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(keep)
    print(f"dropped {dropped} eligible pages with an unreliable text layer")
    subprocess.run([sys.executable, "tools/golden/number_check.py", "parsed_ocr/mineru", "parsed/paddleocr_vl",
                    "--out", "review/number_fidelity"], cwd=SIDE, check=True, env=os.environ)


if __name__ == "__main__":
    main()
