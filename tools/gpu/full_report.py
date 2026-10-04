"""Exhaustive parser comparison from the full-run caches and run logs.

    python tools/gpu/full_report.py --gpu-price 0.99 [--vcpu-price 0.04] [--tokens]

Reads, for each parser present under parsed/ (baseline, pymupdf4llm, docling, mineru):
  parsed/<parser>/<doc>/meta.json + pages.json   per-document results
  parsed/<parser>/_runs/*_summary.json, *_gpu.csv  wall time, CPU time, GPU samples
  review/v2/<parser>.json, review/v1/<parser>.json  golden-set scores (cap-slice-score)
and writes review/gpu/COMPARISON.md + comparison.json with:
  coverage    docs ok/failed, pages returned, empty pages, low-text pages recovered
  speed       pages/s and docs/h over the run's wall time; per-document and per-page
              latency (p50/p90/p99/max); seconds per page by document type
  resources   GPU utilisation / peak memory / average power, energy per 1,000 pages,
              CPU-seconds per page, peak process memory, parallel processes used
  cost        $ per 1,000 pages at the GPU price; this collection; 11M and 14M pages;
              CPU-only cost from CPU-seconds (--vcpu-price) for CPU parsers
  output      characters per page, output size, chunks and tokens (--tokens) per page
  accuracy    golden v2 (150 facts) and v1 (28 facts) at L1-L4, plus key groups
Standard library only, except --tokens (needs cap-slice + voyageai, e.g. the docling env).
"""

from __future__ import annotations

import argparse
import csv
import json
import statistics
from collections import defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
PARSERS = ("baseline", "pymupdf4llm", "docling", "mineru", "paddleocr_vl")
SCALE = (11_000_000, 14_000_000)
MIN_TEXT = 50


def pct(xs: list[float], q: float) -> float:
    if not xs:
        return float("nan")
    xs = sorted(xs)
    k = (len(xs) - 1) * q
    lo, hi = int(k), min(int(k) + 1, len(xs) - 1)
    return xs[lo] + (xs[hi] - xs[lo]) * (k - lo)


def union_seconds(intervals: list[tuple[float, float]]) -> float:
    total, end = 0.0, None
    for a, b in sorted(intervals):
        if end is None or a > end:
            total += b - a
            end = b
        elif b > end:
            total += b - end
            end = b
    return total


def gpu_samples(csv_paths: list[Path]) -> dict:
    util, mem, power = [], [], []
    for p in csv_paths:
        for r in csv.DictReader(p.open()):
            try:
                util.append(float(r["util_pct"]))
                mem.append(float(r["mem_used_mib"]))
                power.append(float(r["power_w"]))
            except (KeyError, ValueError):
                continue
    if not util:
        return {}
    return {"gpu_util_avg_pct": statistics.mean(util), "gpu_mem_peak_gb": max(mem) / 1024,
            "gpu_power_avg_w": statistics.mean(power)}


def load_inventory() -> dict[tuple[str, int], dict]:
    inv = {}
    for r in csv.DictReader((REPO / "data/golden/page_inventory.csv").open()):
        inv[(r["doc"], int(r["page"]))] = r
    return inv


def doc_type_of(doc_path: str) -> str:
    parts = Path(doc_path).parts
    return parts[-2] if len(parts) >= 2 else "?"


def parser_metrics(parser: str, root: Path, inv: dict, args) -> dict | None:
    pdir = root / parser
    meta_files = sorted(pdir.glob("*/*/*/meta.json"))
    if not meta_files:
        return None
    metas = []
    for f in meta_files:
        x = json.loads(f.read_text())
        x["_dir"] = f.parent                       # cache folder of this document
        x["_doc_rel"] = str(Path("data") / f.parent.relative_to(pdir)) + ".pdf"
        metas.append(x)
    ok = [m for m in metas if m["status"] == "ok"]
    m = {"parser": parser, "docs_ok": len(ok), "docs_failed": len(metas) - len(ok)}
    pages_total = sum(x["page_count"] for x in ok)
    m["pages"] = pages_total
    m["pages_returned_pct"] = 100 * sum(x.get("pages_returned", 0) for x in ok) / max(pages_total, 1)

    # output: chars/page, empty pages, low-text pages recovered
    chars, empty, low_total, low_recovered, out_bytes = [], 0, 0, 0, 0
    per_type = defaultdict(lambda: [0.0, 0])
    for x in ok:
        ddir, doc_rel = x["_dir"], x["_doc_rel"]
        pj = ddir / "pages.json"
        if not pj.exists():
            continue
        out_bytes += sum(f.stat().st_size for f in ddir.iterdir() if f.is_file())
        texts = dict((n, t) for n, t in json.loads(pj.read_text())["pages"])
        for n in range(1, x["page_count"] + 1):
            t = texts.get(n, "")
            chars.append(len(t))
            empty += len(t.strip()) < MIN_TEXT
            row = inv.get((doc_rel, n))
            if row and row["low_text"] == "1":
                low_total += 1
                low_recovered += len(t.strip()) >= MIN_TEXT
        per_type[doc_type_of(doc_rel)][0] += x["seconds"]
        per_type[doc_type_of(doc_rel)][1] += x["page_count"]
    m.update({"chars_per_page_avg": statistics.mean(chars) if chars else 0,
              "empty_pages_pct": 100 * empty / max(len(chars), 1),
              "low_text_pages": low_total, "low_text_recovered": low_recovered,
              "output_mb_per_1000_pages": out_bytes / 2**20 / max(pages_total, 1) * 1000})

    # latency
    doc_s = [x["seconds"] for x in ok]
    page_s = [x["seconds"] / max(x["page_count"], 1) for x in ok]
    m.update({"doc_latency_p50_s": pct(doc_s, .5), "doc_latency_p90_s": pct(doc_s, .9),
              "doc_latency_p99_s": pct(doc_s, .99), "doc_latency_max_s": max(doc_s) if doc_s else 0,
              "page_latency_p50_s": pct(page_s, .5), "page_latency_p90_s": pct(page_s, .9),
              "s_per_page_by_type": {k: v[0] / max(v[1], 1) for k, v in sorted(per_type.items())}})

    # throughput over wall time (union of all runs' intervals, parallel processes overlap)
    sums = [s for s in (json.loads(f.read_text()) for f in (pdir / "_runs").glob("*_summary.json"))
            if s.get("pages_ok")]
    # Wall time: union of timed runs (parallel processes overlap) + untimed runs' own wall time.
    timed = [s for s in sums if "started_unix" in s]
    intervals = [(s["started_unix"], s["ended_unix"]) for s in timed]
    wall = union_seconds(intervals) + sum(s["wall_seconds"] for s in sums if "started_unix" not in s)
    run_pages = sum(s["pages_ok"] for s in sums)
    procs = max((sum(1 for a, b in intervals if a <= t < b) for t, _ in intervals), default=1)
    with_cpu = [s for s in sums if "cpu_seconds" in s]
    rss = [s["peak_rss_mb"] for s in sums if s.get("peak_rss_mb")]
    m.update({"wall_hours": wall / 3600,
              # throughput from the runs' own page counts (a cache can hold docs from older runs)
              "pages_per_s": run_pages / max(wall, 1e-9),
              "docs_per_hour": sum(s["docs_ok"] for s in sums) / max(wall, 1e-9) * 3600,
              "parallel_processes": procs,
              "cpu_seconds_per_page": (sum(s["cpu_seconds"] for s in with_cpu)
                                       / max(sum(s["pages_ok"] for s in with_cpu), 1)) if with_cpu else None,
              "peak_rss_mb": max(rss) if rss else None})
    m.update(gpu_samples(list((pdir / "_runs").glob("*_gpu.csv"))))
    if "gpu_power_avg_w" in m:
        m["energy_wh_per_1000_pages"] = m["gpu_power_avg_w"] * wall / 3600 / max(pages_total, 1) * 1000

    # cost
    pps = m["pages_per_s"]
    per_k = args.gpu_price / (pps * 3600) * 1000 if pps else float("nan")
    m.update({"usd_per_1000_pages": per_k, "usd_this_collection": per_k * pages_total / 1000,
              "usd_11m_pages": per_k * SCALE[0] / 1000, "usd_14m_pages": per_k * SCALE[1] / 1000})
    if args.vcpu_price and m["cpu_seconds_per_page"]:
        m["usd_per_1000_pages_cpu_only"] = m["cpu_seconds_per_page"] * 1000 / 3600 * args.vcpu_price

    # stage breakdown (Docling)
    stages = defaultdict(float)
    for x in ok:
        for k, v in (x.get("info", {}) or {}).get("stage_seconds", {}).items():
            stages[k] += v
    if stages:
        tot = stages.get("pipeline_total") or sum(stages.values())
        m["stage_share_pct"] = {k: 100 * v / tot for k, v in stages.items()
                                if k in ("ocr", "layout", "table_structure", "page_parse") and tot}

    # accuracy
    for tag in ("v2", "v1"):
        f = REPO / args.review / tag / f"{parser}.json"
        if f.exists():
            s = json.loads(f.read_text())["summary"]
            m[f"golden_{tag}"] = {**s["levels"], "scored": s["scored"], "of": s["facts"],
                                  "groups": s.get("l4_by_group", {})}

    if args.tokens:
        m.update(token_stats(parser, pdir, ok))
    return m


def token_stats(parser: str, pdir: Path, ok: list[dict]) -> dict:
    import voyageai
    from cap_slice.score import chunks_for
    tok = voyageai.Client(api_key="local-tokenizer-only")
    n_chunks = n_tokens = pages = 0
    for x in ok:
        pj = x["_dir"] / "pages.json"
        if not pj.exists():
            continue
        chunks = chunks_for(parser, json.loads(pj.read_text())["pages"])
        n_chunks += len(chunks)
        n_tokens += sum(tok.count_tokens([c.text], model="voyage-finance-2") for c in chunks)
        pages += x["page_count"]
    return {"chunks_per_page": n_chunks / max(pages, 1), "tokens_per_page": n_tokens / max(pages, 1),
            "tokens_per_chunk": n_tokens / max(n_chunks, 1), "voyage_usd_this_collection": n_tokens / 1e6 * 0.12}


def same_text(rows: list[dict], ref: dict[str, str]) -> None:
    """Share of pages whose text is identical to the reference setting's (same parser, same
    documents): more processes or bigger batches should not change what a parser outputs."""
    by_parser = defaultdict(list)
    for r in rows:
        by_parser[r["_parser"]].append(r)
    for parser, rs in by_parser.items():
        base = next((r for r in rs if r["parser"] == ref.get(parser)), rs[0])

        def pages(r):
            out = {}
            for pj in (r["_root"] / parser).glob("*/*/*/pages.json"):
                doc = pj.parent.relative_to(r["_root"] / parser)
                for n, t in json.loads(pj.read_text())["pages"]:
                    out[(str(doc), n)] = t
            return out
        bp = pages(base)
        for r in rs:
            rp = pages(r)
            common = bp.keys() & rp.keys()
            r["same_text_ref"] = base["parser"]
            r["same_text_pct"] = 100 * sum(bp[k] == rp[k] for k in common) / len(common) if common else float("nan")


def fmt(v, nd=2):
    if v is None:
        return "—"
    if isinstance(v, float):
        return "—" if v != v else (f"{v:,.0f}" if abs(v) >= 1000 else f"{v:.{nd}f}")
    return f"{v:,}" if isinstance(v, int) else str(v)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--gpu-price", type=float, required=True, help="pod $/hour")
    ap.add_argument("--vcpu-price", type=float, help="$/vCPU-hour, for CPU-only cost of CPU parsers")
    ap.add_argument("--root", default="parsed")
    ap.add_argument("--tokens", action="store_true", help="also count chunks/tokens (slower)")
    ap.add_argument("--parsers", nargs="*", default=list(PARSERS))
    ap.add_argument("--review", default="review", help="folder holding v2/ and v1/ score files")
    ap.add_argument("--out", default="review/gpu")
    ap.add_argument("--variants", action="store_true",
                    help="--root holds one folder per setting (e.g. parsed_tune/mineru_p12_w12/mineru/...); one "
                         "column per setting, scores from <setting>/review/{v2,v1}/")
    ap.add_argument("--ref", nargs="*", default=[], metavar="PARSER=VARIANT",
                    help="with --variants: setting each other setting's output is compared to (default: the "
                         "first one per parser, by name)")
    args = ap.parse_args()
    inv = load_inventory()
    root = Path(args.root) if Path(args.root).is_absolute() else REPO / args.root
    if args.variants:
        rows = []
        for vdir in sorted(d for d in root.iterdir() if d.is_dir() and d.name != "review"):
            for p in args.parsers:
                if (vdir / p).is_dir():
                    args.review = str(vdir / "review")
                    if (m := parser_metrics(p, vdir, inv, args)):
                        m["parser"], m["_parser"], m["_root"] = vdir.name, p, vdir
                        rows.append(m)
        same_text(rows, dict(x.split("=", 1) for x in args.ref))
    else:
        rows = [r for p in args.parsers if (r := parser_metrics(p, root, inv, args))]
    out = REPO / args.out
    out.mkdir(parents=True, exist_ok=True)
    for r in rows:
        for k in ("_dir", "_root"):
            r.pop(k, None)
    (out / "comparison.json").write_text(json.dumps(rows, indent=1, default=str))

    cols = [r["parser"] for r in rows]
    title = "settings compared on " + args.root if args.variants else (
        "full collection" if args.root == "parsed" else args.root)
    lines = [f"# Parser comparison — {title}\n",
             f"Pod price ${args.gpu_price}/h. Generated by `tools/gpu/full_report.py`; raw numbers in `comparison.json`.\n",
             "| Metric | " + " | ".join(cols) + " |", "|---|" + "---|" * len(cols)]

    def row(label, key, nd=2, sub=None):
        vals = []
        for r in rows:
            v = r.get(key) if sub is None else (r.get(key) or {}).get(sub)
            vals.append(fmt(v, nd))
        lines.append(f"| {label} | " + " | ".join(vals) + " |")

    lines.append("| **Coverage** |" + " |" * len(cols))
    lines.append("| Documents ok / failed | " + " | ".join(f"{r['docs_ok']} / {r['docs_failed']}" for r in rows) + " |")
    row("Pages", "pages", 0)
    row("Pages returned (%)", "pages_returned_pct", 1)
    row("Empty pages (< 50 chars, %)", "empty_pages_pct", 1)
    if args.variants:
        row("Same reference setting", "same_text_ref", 0)
        row("Pages with identical text to it (%)", "same_text_pct", 1)
    lines.append("| Low-text pages recovered | " + " | ".join(f"{r['low_text_recovered']} / {r['low_text_pages']}" for r in rows) + " |")
    lines.append("| **Accuracy (golden sets)** |" + " |" * len(cols))
    for tag in ("v2", "v1"):
        for lvl in ("L4+", "L3+", "L2+", "L1+"):
            lines.append(f"| {tag} facts at {lvl[:-1]} | " + " | ".join(
                (f"{r[f'golden_{tag}'][lvl]}/{r[f'golden_{tag}']['scored']}" if f"golden_{tag}" in r else "—") for r in rows) + " |")
    for g in ("tag:two_level_header", "tag:bad_text_layer", "tag:image_only_page", "kind:table", "kind:qa"):
        lines.append(f"| v2 L4 — {g.split(':')[1]} | " + " | ".join(
            r.get("golden_v2", {}).get("groups", {}).get(g, "—") for r in rows) + " |")
    lines.append("| **Speed** |" + " |" * len(cols))
    row("Throughput (pages/s)", "pages_per_s", 3)
    row("Documents per hour", "docs_per_hour", 0)
    row("Wall time (h)", "wall_hours", 2)
    row("Parallel processes", "parallel_processes", 0)
    row("Per-document latency p50 (s)", "doc_latency_p50_s", 1)
    row("Per-document latency p90 (s)", "doc_latency_p90_s", 1)
    row("Per-document latency p99 (s)", "doc_latency_p99_s", 1)
    row("Per-document latency max (s)", "doc_latency_max_s", 1)
    row("Per-page time p50 (s)", "page_latency_p50_s", 3)
    row("Per-page time p90 (s)", "page_latency_p90_s", 3)
    types = sorted({t for r in rows for t in r.get("s_per_page_by_type", {})})
    for t in types:
        row(f"s/page — {t}", "s_per_page_by_type", 3, t)
    lines.append("| **Resources** |" + " |" * len(cols))
    row("GPU utilisation avg (%)", "gpu_util_avg_pct", 0)
    row("GPU memory peak (GB)", "gpu_mem_peak_gb", 1)
    row("GPU power avg (W)", "gpu_power_avg_w", 0)
    row("GPU energy (Wh / 1,000 pages)", "energy_wh_per_1000_pages", 0)
    row("CPU-seconds per page", "cpu_seconds_per_page", 2)
    row("Peak process memory (MB)", "peak_rss_mb", 0)
    for st in ("ocr", "layout", "table_structure"):
        row(f"Stage share — {st} (%)", "stage_share_pct", 0, st)
    lines.append("| **Cost** |" + " |" * len(cols))
    row("$ per 1,000 pages (pod)", "usd_per_1000_pages", 3)
    row("$ this collection", "usd_this_collection", 2)
    row("$ for 11M pages", "usd_11m_pages", 0)
    row("$ for 14M pages", "usd_14m_pages", 0)
    if args.vcpu_price:
        row(f"$ per 1,000 pages, CPU-only at ${args.vcpu_price}/vCPU-h", "usd_per_1000_pages_cpu_only", 4)
    lines.append("| **Output** |" + " |" * len(cols))
    row("Characters per page", "chars_per_page_avg", 0)
    row("Cache size (MB / 1,000 pages)", "output_mb_per_1000_pages", 1)
    if args.tokens:
        row("Chunks per page", "chunks_per_page", 2)
        row("Tokens per page (Voyage)", "tokens_per_page", 0)
        row("Tokens per chunk", "tokens_per_chunk", 0)
        row("Voyage embedding $ (this collection, list price)", "voyage_usd_this_collection", 2)
    lines += ["", "Notes: throughput uses wall time across all runs of a parser (parallel processes counted once); "
              "per-document latency is measured inside each process, so with parallel processes it includes "
              "contention. MinerU's CPU-seconds exclude its VLM server process. GPU figures come from 5-second "
              "nvidia-smi samples during the runs. Accuracy assumes perfect retrieval (see review/README.md)."]
    (out / "COMPARISON.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
