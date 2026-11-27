"""GLM-OCR throughput run using the FULL SDK pipeline (PP-DocLayoutV3 layout + GLM-OCR via vLLM).

Concurrency here = number of worker processes, each with its own GlmOcr parser
(layout model on GPU). The SDK additionally fans out region requests in parallel inside
each parse, so server-side concurrency = workers x regions-in-flight. Check the
'running_mean' gauge in summary.json to see what vLLM actually saw.

  python run_glm.py --manifest pages/manifest.jsonl --warmup-manifest pages/warmup.jsonl --workers 8
  python run_glm.py ... --cfg pipeline.layout.use_polygon=false   # any config.yaml override
"""
import argparse
import json
import multiprocessing as mp
import shutil
import time
from pathlib import Path

import yaml

from common import (GpuMonitor, Sampler, load_manifest, run_dir, scrape_counters,
                    write_summary)

_parser = None


# ------------------------------------------------------------------ config
def patch_sdk_config(host: str, port: int, model: str, overrides: list[str],
                     charts: bool = True, keep_headers: bool = True) -> Path:
    """The SDK reads glmocr/config.yaml. Point it at our vLLM server (backup kept).

    charts=True: the SDK's default config SKIPS 'chart' and 'image' layout regions (kept as cropped
    images, never sent to the model), so chart values never reach the output. For a like-for-like
    comparison with Paddle (use_chart_recognition) and Unlimited (crop pass), send charts with the
    "Table Recognition:" prompt and images with "Text Recognition:".
    """
    import glmocr
    cfg_path = Path(glmocr.__file__).parent / "config.yaml"
    backup = cfg_path.with_suffix(".yaml.orig")
    if not backup.exists():
        shutil.copy(cfg_path, backup)
    cfg = yaml.safe_load(backup.read_text()) or {}
    pipe = cfg.setdefault("pipeline", {})
    pipe.setdefault("maas", {})["enabled"] = False
    ocr = pipe.setdefault("ocr_api", {})
    ocr.update({"api_host": host, "api_port": port, "model": model})
    if charts:
        ltm = pipe.setdefault("layout", {}).setdefault("label_task_mapping", {})
        skip = ltm.get("skip") or []
        for label, task in (("chart", "table"), ("image", "text")):
            if label in skip:
                skip.remove(label)
            if label not in (ltm.get(task) or []):
                ltm.setdefault(task, []).append(label)
        ltm["skip"] = skip
        # The result formatter renders labels in its "image" category as a picture reference and drops
        # the recognised text, so move them into the categories whose content is kept.
        lvm = pipe.setdefault("result_formatter", {}).setdefault("label_visualization_mapping", {})
        img = lvm.get("image") or []
        for label, task in (("chart", "table"), ("image", "text")):
            if label in img:
                img.remove(label)
            if label not in (lvm.get(task) or []):
                lvm.setdefault(task, []).append(label)
        lvm["image"] = img
    if keep_headers:
        # Default config ABANDONS header/footnote/aside_text (never sent to the model). Recognise them as
        # text so nothing is lost at extraction; footers / page numbers stay abandoned.
        ltm = pipe.setdefault("layout", {}).setdefault("label_task_mapping", {})
        abandon = ltm.get("abandon") or []
        for label in ("header", "footnote", "aside_text"):
            if label in abandon:
                abandon.remove(label)
            if label not in (ltm.get("text") or []):
                ltm.setdefault("text", []).append(label)
        ltm["abandon"] = abandon
        lvm = pipe.setdefault("result_formatter", {}).setdefault("label_visualization_mapping", {})
        for label in ("header", "footnote", "aside_text"):
            if label not in (lvm.get("text") or []):
                lvm.setdefault("text", []).append(label)
    for ov in overrides:
        key, val = ov.split("=", 1)
        node = cfg
        *parents, leaf = key.split(".")
        for p in parents:
            node = node.setdefault(p, {})
        node[leaf] = yaml.safe_load(val)
    cfg_path.write_text(yaml.safe_dump(cfg, sort_keys=False))
    return cfg_path


# ------------------------------------------------------------------ workers
def _init(layout_device: str):
    global _parser
    from glmocr import GlmOcr
    _parser = GlmOcr(layout_device=layout_device)


def _markdown(result, scratch: Path) -> str:
    for attr in ("markdown_result", "markdown", "md_result"):
        v = getattr(result, attr, None)
        if isinstance(v, str) and v.strip():
            return v
    # fallback: let the SDK save, then read whatever .md it wrote
    scratch.mkdir(parents=True, exist_ok=True)
    result.save(output_dir=str(scratch))
    mds = sorted(scratch.rglob("*.md"))
    return "\n\n".join(p.read_text() for p in mds)


def _work(args):
    row, md_dir = args
    t0 = time.perf_counter()
    rec = {"page_id": row["page_id"]}
    try:
        result = _parser.parse(row["path"])
        rec["latency_s"] = time.perf_counter() - t0
        if md_dir:
            md = _markdown(result, Path(md_dir) / "_scratch" / row["page_id"])
            (Path(md_dir) / f"{row['page_id']}.md").write_text(md)
            rec["empty"] = not md.strip()
    except Exception as e:
        rec.update(latency_s=time.perf_counter() - t0, error=repr(e)[:300])
    return rec


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", required=True)
    ap.add_argument("--warmup-manifest", help="pages used only for warm-up (not measured)")
    ap.add_argument("--limit", type=int)
    ap.add_argument("--host", default="localhost")
    ap.add_argument("--port", type=int, default=8080)
    ap.add_argument("--model-name", default="glm-ocr")
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--layout-device", default="cuda:0")
    ap.add_argument("--cfg", action="append", default=[], help="dotted.key=value override")
    ap.add_argument("--no-charts", dest="charts", action="store_false",
                    help="keep the SDK default of skipping chart/image regions")
    ap.add_argument("--drop-headers", dest="keep_headers", action="store_false",
                    help="keep the SDK default of abandoning header/footnote/aside_text regions")
    ap.add_argument("--warmup", type=int, default=16)
    ap.add_argument("--results", default="results")
    ap.add_argument("--run-name")
    a = ap.parse_args()

    cfg_path = patch_sdk_config(a.host, a.port, a.model_name, a.cfg, a.charts, a.keep_headers)
    print(f"patched SDK config: {cfg_path}")

    rows = load_manifest(a.manifest, a.limit)
    run_name = a.run_name or f"w{a.workers}"
    d = run_dir(a.results, "glm-ocr", run_name)
    metrics_url = f"http://{a.host}:{a.port}/metrics"

    ctx = mp.get_context("spawn")
    with ctx.Pool(a.workers, initializer=_init, initargs=(a.layout_device,)) as pool:
        warm = load_manifest(a.warmup_manifest) if a.warmup_manifest else rows[:a.warmup]
        print(f"warmup: {len(warm)} pages across {a.workers} workers "
              f"({'separate pages' if a.warmup_manifest else 'first pages of the set'})")
        list(pool.imap_unordered(_work, [(r, None) for r in warm]))

        before = scrape_counters(metrics_url)
        with GpuMonitor(d / "gpu.csv"), Sampler(d / "server.jsonl", metrics_url) as smp:
            t0 = time.perf_counter()
            records = list(pool.imap_unordered(_work, [(r, str(d / "md")) for r in rows]))
            wall = time.perf_counter() - t0
        after = scrape_counters(metrics_url)

    shutil.rmtree(d / "md" / "_scratch", ignore_errors=True)
    with open(d / "pages.jsonl", "w") as f:
        for r in records:
            f.write(json.dumps(r) + "\n")
    ok = [r for r in records if "error" not in r]
    empties = sum(1 for r in ok if r.get("empty"))
    if empties > 0.01 * max(len(ok), 1):
        # The SDK swallows layout errors (e.g. CUDA OOM when too many workers each load a layout
        # model next to the vLLM server) and returns an empty page instead of raising.
        print(f"WARNING: {empties}/{len(ok)} empty pages - run is INVALID. Check the log for "
              f"'Layout detection failed' / 'out of memory'; use fewer --workers.")
    write_summary(d, model="glm-ocr", run_name=run_name,
                  config={"workers": a.workers, "chart_recognition": a.charts,
                          "keep_headers": a.keep_headers,
                          "empty_outputs": sum(1 for r in ok if r.get("empty"))},
                  n_pages=len(ok), wall_s=wall,
                  latencies=[r["latency_s"] for r in ok],
                  failures=len(records) - len(ok),
                  counters_before=before, counters_after=after, sampler=smp)


if __name__ == "__main__":
    main()
