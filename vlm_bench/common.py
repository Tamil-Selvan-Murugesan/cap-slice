"""Shared helpers for the OCR throughput benchmark.

Every runner writes the same artifacts so models are directly comparable:
  results/<model>/<run>/pages.jsonl      one line per page/request (latency, tokens, errors)
  results/<model>/<run>/md/<page_id>.md  raw parsed output (for your offline accuracy eval)
  results/<model>/<run>/gpu.csv          nvidia-smi samples
  results/<model>/<run>/server.jsonl     vLLM /metrics gauge samples
  results/<model>/<run>/summary.json     headline numbers
"""
from __future__ import annotations

import json
import re
import statistics
import subprocess
import threading
import time
import urllib.request
from pathlib import Path

import psutil


# --------------------------------------------------------------------------- manifest
def load_manifest(path: str, limit: int | None = None) -> list[dict]:
    rows = [json.loads(l) for l in Path(path).read_text().splitlines() if l.strip()]
    return rows[:limit] if limit else rows


def run_dir(results_root: str, model: str, run_name: str) -> Path:
    d = Path(results_root) / model / run_name
    (d / "md").mkdir(parents=True, exist_ok=True)
    return d


# --------------------------------------------------------------------------- GPU monitor
class GpuMonitor:
    """Samples nvidia-smi every 500 ms into gpu.csv while the run is active."""

    def __init__(self, out_csv: Path, interval_ms: int = 500):
        self.out_csv, self.interval_ms, self.proc = out_csv, interval_ms, None

    def __enter__(self):
        self.fh = open(self.out_csv, "w")
        self.proc = subprocess.Popen(
            ["nvidia-smi",
             "--query-gpu=timestamp,utilization.gpu,memory.used,memory.total,power.draw",
             "--format=csv,noheader,nounits", f"-lms={self.interval_ms}"],
            stdout=self.fh, stderr=subprocess.DEVNULL)
        return self

    def __exit__(self, *exc):
        if self.proc:
            self.proc.terminate()
            self.proc.wait(timeout=5)
        self.fh.close()

    @staticmethod
    def stats(csv_path: Path) -> dict:
        util, mem = [], []
        for line in Path(csv_path).read_text().splitlines():
            parts = [p.strip() for p in line.split(",")]
            try:
                util.append(float(parts[1]))
                mem.append(float(parts[2]))
            except (IndexError, ValueError):
                continue
        if not util:
            return {}
        return {"gpu_util_mean": round(statistics.mean(util), 1),
                "gpu_util_p90": round(percentile(util, 90), 1),
                "gpu_mem_max_mb": max(mem)}


# --------------------------------------------------------------------------- CPU + vLLM sampler
_GAUGES = {
    "running": re.compile(r"^vllm:num_requests_running(?:\{[^}]*\})?\s+([\d.eE+-]+)"),
    "waiting": re.compile(r"^vllm:num_requests_waiting(?:\{[^}]*\})?\s+([\d.eE+-]+)"),
    # metric was renamed across vLLM versions; accept both
    "kv_cache": re.compile(r"^vllm:(?:gpu_cache_usage_perc|kv_cache_usage_perc)(?:\{[^}]*\})?\s+([\d.eE+-]+)"),
}
_COUNTERS = {
    "gen_tokens": re.compile(r"^vllm:generation_tokens_total(?:\{[^}]*\})?\s+([\d.eE+-]+)"),
    "prompt_tokens": re.compile(r"^vllm:prompt_tokens_total(?:\{[^}]*\})?\s+([\d.eE+-]+)"),
    "requests_ok": re.compile(r"^vllm:request_success_total(?:\{[^}]*\})?\s+([\d.eE+-]+)"),
}


def _scrape(metrics_url: str, patterns: dict) -> dict:
    try:
        text = urllib.request.urlopen(metrics_url, timeout=3).read().decode()
    except Exception:
        return {}
    out = {k: 0.0 for k in patterns}
    for line in text.splitlines():
        for k, pat in patterns.items():
            m = pat.match(line)
            if m:
                out[k] += float(m.group(1))  # sum across label sets
    return out


def scrape_counters(metrics_url: str) -> dict:
    return _scrape(metrics_url, _COUNTERS)


class Sampler:
    """Background thread: system CPU % plus vLLM queue/KV gauges once per second."""

    def __init__(self, out_jsonl: Path, metrics_url: str | None, interval: float = 1.0):
        self.out, self.url, self.interval = out_jsonl, metrics_url, interval
        self._stop = threading.Event()
        self.rows: list[dict] = []

    def _loop(self):
        psutil.cpu_percent(interval=None)
        while not self._stop.is_set():
            time.sleep(self.interval)
            row = {"t": time.time(), "cpu": psutil.cpu_percent(interval=None)}
            if self.url:
                row.update(_scrape(self.url, _GAUGES))
            self.rows.append(row)

    def __enter__(self):
        self.th = threading.Thread(target=self._loop, daemon=True)
        self.th.start()
        return self

    def __exit__(self, *exc):
        self._stop.set()
        self.th.join(timeout=5)
        with open(self.out, "w") as f:
            for r in self.rows:
                f.write(json.dumps(r) + "\n")

    def stats(self) -> dict:
        out = {}
        for k in ("cpu", "running", "waiting", "kv_cache"):
            vals = [r[k] for r in self.rows if k in r]
            if vals:
                out[f"{k}_mean"] = round(statistics.mean(vals), 3)
                out[f"{k}_max"] = round(max(vals), 3)
        return out


# --------------------------------------------------------------------------- summary
def percentile(xs: list[float], p: float) -> float:
    if not xs:
        return float("nan")
    xs = sorted(xs)
    k = (len(xs) - 1) * p / 100
    lo, hi = int(k), min(int(k) + 1, len(xs) - 1)
    return xs[lo] + (xs[hi] - xs[lo]) * (k - lo)


def write_summary(d: Path, *, model: str, run_name: str, config: dict, n_pages: int,
                  wall_s: float, latencies: list[float], failures: int,
                  counters_before: dict, counters_after: dict, sampler: Sampler) -> dict:
    pps = n_pages / wall_s if wall_s else 0.0
    s = {
        "model": model, "run": run_name, **config,
        "pages": n_pages, "failures": failures,
        "wall_s": round(wall_s, 2),
        "pages_per_s": round(pps, 3),
        "pages_per_hour": round(pps * 3600),
        "gpu_hours_per_1M_pages": round(1e6 / pps / 3600, 1) if pps else None,
        "lat_p50_s": round(percentile(latencies, 50), 3) if latencies else None,
        "lat_p95_s": round(percentile(latencies, 95), 3) if latencies else None,
    }
    if counters_before and counters_after:
        gen = counters_after["gen_tokens"] - counters_before["gen_tokens"]
        prm = counters_after["prompt_tokens"] - counters_before["prompt_tokens"]
        reqs = counters_after["requests_ok"] - counters_before["requests_ok"]
        s.update({"server_gen_tokens": int(gen), "server_prompt_tokens": int(prm),
                  "server_requests": int(reqs),
                  "gen_tok_per_s": round(gen / wall_s, 1),
                  "gen_tokens_per_page": round(gen / n_pages, 1) if n_pages else None,
                  "vlm_requests_per_page": round(reqs / n_pages, 2) if n_pages else None})
    s.update(GpuMonitor.stats(d / "gpu.csv"))
    s.update(sampler.stats())
    (d / "summary.json").write_text(json.dumps(s, indent=2))
    print(json.dumps(s, indent=2))
    return s
