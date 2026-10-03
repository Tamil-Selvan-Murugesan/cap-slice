"""Summarise benchmark runs: speed, cost per 1,000 pages, projected full-scale cost.

    python3 tools/gpu/bench_report.py --price 0.99      # $/hour of this GPU

Reads parsed_bench/<variant>/<parser>/_runs/*_summary.json (written by
cap-slice-parse) and the matching GPU samples. Standard library only, so it
runs on the host without either image.
"""

from __future__ import annotations

import argparse
import csv
import json
import statistics
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
COLLECTION_PAGES = 12_980
SCALE_PAGES = (11_000_000, 14_000_000)  # 200k-250k documents x ~57 pages


def gpu_stats(csv_path: Path) -> str:
    if not csv_path.exists():
        return "-"
    rows = [r for r in csv.DictReader(csv_path.open()) if r.get("util_pct", "").strip().isdigit()]
    if not rows:
        return "-"
    util = statistics.mean(float(r["util_pct"]) for r in rows)
    mem = max(float(r["mem_used_mib"]) for r in rows)
    return f"{util:.0f}% avg util, {mem / 1024:.1f} GB peak"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--price", type=float, required=True, help="GPU $/hour")
    ap.add_argument("--root", default="parsed_bench")
    args = ap.parse_args()
    # Group every summary of a variant: parallel processes (several runner processes
    # writing to the same --out) count together — total pages / overall wall time.
    groups: dict[str, list[tuple[dict, Path]]] = {}
    for summ in sorted((REPO / args.root).glob("*/*/_runs/*_summary.json")):
        s = json.loads(summ.read_text())
        if s.get("pages_ok"):
            groups.setdefault(summ.parents[2].name, []).append((s, summ))
    rows = []
    for variant, items in groups.items():
        pages = sum(s["pages_ok"] for s, _ in items)
        failed = sum(s["docs_failed"] for s, _ in items)
        if all("started_unix" in s for s, _ in items):
            wall = max(s["ended_unix"] for s, _ in items) - min(s["started_unix"] for s, _ in items)
        else:  # older summaries: assume the processes ran side by side
            wall = max(s["wall_seconds"] for s, _ in items)
        pps = pages / max(wall, 1e-9)
        per_k = args.price / (pps * 3600) * 1000
        gpu = gpu_stats(items[0][1].with_name(items[0][1].name.replace("_summary.json", "_gpu.csv")))
        label = variant + (f" ({len(items)} processes)" if len(items) > 1 else "")
        rows.append((label, pages, failed, pps, per_k, gpu, items[0][0]["machine"].get("gpus", ["?"])[0]))
    if not rows:
        print("no benchmark summaries found under", args.root)
        return
    print(f"GPU price ${args.price}/h — {rows[0][6]}\n")
    print("| Variant | Pages | Failed docs | Pages/s | $ per 1,000 pages | This collection | 11–14M pages | GPU |")
    print("|---|---|---|---|---|---|---|---|")
    for v, pages, failed, pps, per_k, gpu, _ in rows:
        coll_h = COLLECTION_PAGES / pps / 3600
        lo, hi = (p / 1000 * per_k for p in SCALE_PAGES)
        print(f"| {v} | {pages} | {failed} | {pps:.2f} | ${per_k:.3f} | {coll_h:.1f} h, ${coll_h * args.price:.0f} "
              f"| ${lo:,.0f}–{hi:,.0f} | {gpu} |")
    print("\nOnly whole-run wall time counts (model load excluded only if the server was already up).")


if __name__ == "__main__":
    main()
