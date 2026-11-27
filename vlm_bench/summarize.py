"""Collect every results/*/*/summary.json into one table + CSV.

  python summarize.py --results results --gpu-hourly 0.86 --pages 1000000
"""
import argparse
import csv
import json
from pathlib import Path

COLS = ["model", "run", "pages", "failures", "empty_outputs", "pages_per_s", "gen_tok_per_s",
        "gen_tokens_per_page", "vlm_requests_per_page", "lat_p50_s", "lat_p95_s",
        "gpu_util_mean", "gpu_mem_max_mb", "cpu_mean", "running_mean", "waiting_mean",
        "kv_cache_mean", "gpu_hours", "cost_usd"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", default="results")
    ap.add_argument("--gpu-hourly", type=float, default=None, help="$/hr of the pod")
    ap.add_argument("--pages", type=int, default=1_000_000)
    a = ap.parse_args()

    rows = []
    for p in sorted(Path(a.results).glob("*/*/summary.json")):
        s = json.loads(p.read_text())
        pps = s.get("pages_per_s") or 0
        s["gpu_hours"] = round(a.pages / pps / 3600, 1) if pps else None
        s["cost_usd"] = round(s["gpu_hours"] * a.gpu_hourly) if (a.gpu_hourly and pps) else None
        rows.append(s)
    if not rows:
        print("no summaries found")
        return

    rows.sort(key=lambda s: (s["model"], -(s.get("pages_per_s") or 0)))
    with open(Path(a.results) / "comparison.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLS, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)

    show = ["model", "run", "empty_outputs", "pages_per_s", "gen_tok_per_s", "lat_p95_s", "gpu_util_mean",
            "cpu_mean", "running_mean", "gpu_hours", "cost_usd", "failures"]
    widths = {c: max(len(c), *(len(str(r.get(c, ""))) for r in rows)) for c in show}
    print("  ".join(c.ljust(widths[c]) for c in show))
    for r in rows:
        print("  ".join(str(r.get(c, "")).ljust(widths[c]) for c in show))
    print(f"\nprojection for {a.pages:,} pages; full table: {Path(a.results) / 'comparison.csv'}")

    best = {}
    for r in rows:
        if (r.get("empty_outputs") or 0) > 0.01 * max(r.get("pages") or 0, 1):
            print(f"  (ignoring {r['model']}/{r['run']}: {r['empty_outputs']} empty pages - invalid run)")
            continue
        if (r.get("pages_per_s") or 0) > (best.get(r["model"], {}).get("pages_per_s") or 0):
            best[r["model"]] = r
    print("\nbest config per model:")
    for m, r in best.items():
        print(f"  {m:20s} {r['run']:12s} {r['pages_per_s']} pages/s -> {r['gpu_hours']} GPU-h")


if __name__ == "__main__":
    main()
