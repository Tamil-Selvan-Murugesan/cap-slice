# GPU run — runbook (RunPod)

Parse all 228 PDFs (12,980 pages) with **MinerU 4 + MinerU2.5-Pro** and **Docling** on one RunPod GPU pod, measure speed and cost, and bring the caches home. Plan and reasoning: [`plan.md`](plan.md). Everything below is copy-paste; every parse step resumes if interrupted.

> Agents working on the pod: read `AGENTS.md`, `PROGRESS.md`, this file and `bugs_resolved.md` first. Don't change parser code mid-run — measured speeds must stay comparable.

**Lessons from the first pod (2026-10-03):** the image ships uv 0.9.0 (setup now installs 0.12.5); a CUDA 12.8 driver can't run vLLM on an RTX 5090 — deploy with the CUDA 13.0 filter; the home upload of PDFs was slow — for later pods use a RunPod network volume or `runpodctl send/receive` between pods.

**How it runs on RunPod.** A pod is itself a container, so Docker can't run inside it. Instead `tools/gpu/setup_runpod.sh` builds the **same two isolated environments** the Dockerfiles define — `/workspace/venvs/docling` and `/workspace/venvs/mineru` — from the same pinned files in `docker/`. The pipeline code is the code tested on the laptop; only the setup differs. (The Dockerfiles stay for later: a pre-built image as a RunPod template would make every future pod start ready.)

## 0. Create the pod (RunPod console)
| Setting | Value |
|---|---|
| GPU | **RTX 5090** — prefer an offer with **≥ 16 vCPUs** (Docling is partly CPU-bound; pod 1 had 12.75) (A40 fallback if step 3 fails on the 5090). Prices noted 2026-10-02: A40 $0.53/h, RTX 5090 $0.99/h, A100 $1.59/h |
| Container image | `runpod/pytorch:1.0.2-cu1281-torch280-ubuntu2404` (Ubuntu 24.04 — the pins target it; its own PyTorch is not used) |
| Volume disk | **≥ 80 GB**, mounted at `/workspace` (venvs ~15 GB, models ~5 GB, PDFs ~1 GB, caches ~1 GB) |
| Container disk | ≥ 30 GB (system packages) |
| CUDA version filter | **13.0** — required for MinerU on an RTX 5090: vLLM refuses Blackwell GPUs unless the driver supports CUDA ≥ 12.9 (a driver-570 / CUDA 12.8 pod failed with "SM 12.x requires CUDA >= 12.9"). Docling also runs on CUDA 12.8 |
| Ports | **Expose TCP port 22** and add your SSH public key in RunPod settings. rsync needs this direct SSH; the `ssh.runpod.io` proxy doesn't support rsync/scp |

Note the hourly price — the report needs it. **Stop** the pod when idle (the volume keeps everything; only the volume is billed while stopped).

## 1. Repo and setup (on the pod, ~15–25 min, mostly downloads)
```bash
cd /workspace
git clone git@github.com:Tamil-Selvan-Murugesan/cap-slice.git && cd cap-slice   # or HTTPS + token
git checkout -b gpu-run                          # all pod commits go here, not main
tools/gpu/setup_runpod.sh                        # apt packages, uv, both venvs, CUDA check, tools/gpu/env.sh
```
It ends by printing each environment's torch/vLLM version and the GPU name — both must say `cuda True`.
- **GitHub access from the pod:** a *repo-scoped* deploy key with write access, or a fine-grained token for this repo only — not your personal login.
- **Agents (optional):** `apt-get install -y nodejs npm && npm install -g @anthropic-ai/claude-code @openai/codex` (use NodeSource for a recent Node if the apt one is too old).
- **Claude Code memory:** copy `~/.claude/projects/-home-tamil-work-cap-slice/memory/` from the laptop to `/root/.claude/projects/-workspace-cap-slice/memory/` on the pod. It carries preferences such as "no AI attribution in commits".
- **After a pod restart:** `/workspace` survives but system packages don't — re-run `tools/gpu/setup_runpod.sh` (quick: the venvs are already there).

## 2. Data (from the laptop)
Code comes from git; only the PDFs are copied — never rsync the whole repo over the clone.
```bash
# on the laptop, from the repo root. PORT/IP from the pod's "Connect" -> "SSH over exposed TCP".
rsync -av --prune-empty-dirs --include='*/' --include='*.pdf' --exclude='*' \
      -e "ssh -p PORT" data/ root@IP:/workspace/cap-slice/data/
```
On the pod: `ls data/*/*/*.pdf | wc -l` must print **228**.

## 3. Models and smoke (~10–20 min)
Run inside `tmux` from here on (`tmux new -s gpu`), so a dropped SSH connection doesn't stop anything.
```bash
tools/gpu/session.sh models      # MinerU small models + MinerU2.5-Pro-2605-1.2B -> /workspace/models; Docling warm-up
tools/gpu/session.sh smoke       # ~2–3 min: all four parsers on one 4-page PDF; every line must start with "ok"
                                 # (the PyMuPDF4LLM line should end in True = OCR on the GPU)
```
If `smoke` fails on the RTX 5090 with CUDA/arch errors ("no kernel image", "sm_120"), stop and move to an A40 pod instead of debugging on the meter.

## 4. Benchmark (200 fixed pages, same set on any GPU)
```bash
GPU_PRICE=0.99 tools/gpu/session.sh bench     # builds data/bench/, runs 7 variants, prints the report
```
Variants: MinerU `standard` and `advanced` (4 documents in flight); Docling with 1 process and with N parallel processes (N = CPUs allowed ÷ 3, max 4 — Docling is partly CPU-bound; batch size made no difference on pod 1); PyMuPDF4LLM on GPU with 1 and N processes (`P4L_PROCS`, default = Docling's N); baseline with 1 process (CPU only). The report gives pages/s, **$ per 1,000 pages**, time for this collection, and projected cost for 11–14M pages.

**Pick the full-run settings from it:**
- MinerU tier: run `standard` for the full collection. Also run `advanced` in full **only if** its projected time for this collection is under ~4 h.
- Docling: keep batch 4; use the process count of whichever Docling variant was faster (`DOCLING_PROCS=1` or the N shown).
- MinerU workers: start at 8; if GPU utilisation in the report is < 70 %, use 16.
- PyMuPDF4LLM: use the faster of its two variants (`P4L_PROCS=1` or N).

## 4b. Rehearsal (~20 min) — catches bugs before the multi-hour runs
```bash
GPU_PRICE=0.99 tools/gpu/session.sh rehearse   # all four parsers on 5 golden docs -> parsed_rehearsal/review/gpu/COMPARISON.md
```
Check: every parser 5 ok / 0 failed; MinerU and Docling score above baseline on the scanned E2E FY2022-23 facts; GPU columns filled for the GPU parsers.

## 5. Full run (one parser at a time, never two together, so speeds stay clean)
```bash
MINERU_TIER=standard MINERU_WORKERS=8 tools/gpu/session.sh full-mineru
DOCLING_PROCS=4                        tools/gpu/session.sh full-docling      # or 1, per the benchmark
P4L_PROCS=4                            tools/gpu/session.sh full-pymupdf4llm  # GPU; or 1, per the benchmark
                                       tools/gpu/session.sh full-baseline     # CPU only, one process per CPU allowed; minutes
GPU_PRICE=0.99                         tools/gpu/session.sh compare           # scores + review/gpu/COMPARISON.md
```
Rough times for 12,980 pages: MinerU and Docling several hours each (Docling ~6–8 h at pod-1 speed), PyMuPDF4LLM ~1–3 h, baseline a few minutes.
`compare` scores every parser on golden v2 (150 facts, `review/v2/`) and v1 (28 facts, `review/v1/`), then writes one table (`review/gpu/COMPARISON.md` + `comparison.json`) with coverage, accuracy (L1–L4, by group, hallucination check), throughput, per-document latency p50/p90/p99, per-page time by doc type, GPU utilisation/memory/power and energy per 1,000 pages, CPU-seconds per page, peak RAM, $ per 1,000 pages, cost for this collection and for 11–14M pages, output size, and tokens/chunks per page with Voyage embedding cost. Set `VCPU_PRICE` ($/vCPU-hour) to also price baseline on a CPU-only machine.
Progress prints one line per document with the running pages/s. To also run `advanced` in full (its own cache folder):
```bash
source tools/gpu/env.sh && CAP_SLICE_MINERU_TIER=advanced PATH=$VENVS/mineru/bin:$PATH \
  tools/gpu/mineru_run.sh --out parsed_advanced --workers 8 --largest-first
```
Failed documents are listed in `parsed/<parser>/_runs/<run_id>.jsonl`; re-run the same command with `--retry-failed` added once.

**MinerU RAM: set `MINERU_MALLOC_TRIM=1 MALLOC_ARENA_MAX=2`** in front of any MinerU command (e.g. `MINERU_MALLOC_TRIM=1 MALLOC_ARENA_MAX=2 MINERU_TIER=standard tools/gpu/session.sh full-mineru`). Without them, a runner's RAM climbs to the peak of its biggest page window (~12 GB on a 300-page annual report) and never comes back down. It looks like a leak, but it isn't one. MinerU frees the memory after each window of `MINERU_PROCESSING_WINDOW_SIZE` pages (default 64), but glibc keeps the freed memory reserved for the process.
- `MINERU_MALLOC_TRIM=1`: MinerU's own opt-in switch (`mineru/model/runtime/memory.py`). It calls `malloc_trim(0)` after each window, which gives freed heap memory back to the OS.
- `MALLOC_ARENA_MAX=2`: a glibc setting. By default glibc can create up to 8 memory pools ("arenas") per CPU core for a threaded process, and freed memory scattered across many pools is hard to give back. Two pools are enough here.

Measured on the RunPod pod (2026-10-04; one runner, the 4 largest PDFs, 945 pages): default RAM 4 → 10 → 12.4 GB and stays there; with both variables it goes up and down between ~4 and ~11.5 GB and ends at 4.8 GB, at the same speed (2.36 vs 2.37 pages/s). The **peak** barely changes (12.1 vs 12.6 GB): that is the real working set of one window. To lower it, try a smaller `MINERU_PROCESSING_WINDOW_SIZE` (e.g. 32; not measured yet). This matters when several runner processes share one container: the pod's limit was 62 GB, not the host's 515 GB that `free` shows, and runners holding their peaks plus the VLM server (~9.5 GB) reached it (`memory.events`: 9 OOM kills). Check real usage with `cat /sys/fs/cgroup/memory.current` (includes reclaimable file cache) and `cat /sys/fs/cgroup/memory.max`.

## 6. Bring results home, then stop the pod
```bash
# on the pod: commit run logs and summaries (not caches — they're big and gitignored)
git add -f parsed*/*/_runs parsed_bench/*/*/_runs data/bench/manifest.csv review/gpu review/v1 review/v2
git commit -m "GPU run: benchmark and full-run logs" && git push -u origin gpu-run
```
```bash
# on the laptop: pull the caches (check `df -h /mnt/c` first — keep ≥ 500 MB free)
rsync -av -e "ssh -p PORT" --include='*/' --include='pages.json' --include='meta.json' --include='_runs/***' --exclude='*' \
      root@IP:/workspace/cap-slice/parsed/ parsed/            # per-page text only: ~60 MB
rsync -av -e "ssh -p PORT" root@IP:/workspace/cap-slice/parsed/ /some/bigger/disk/parsed/   # + raw JSON (~0.5 GB)
```
Expected sizes (from the laptop tests): Docling `docling.json` ~30 KB/page (~0.4 GB total), MinerU `mineru_middle.json` ~3 KB/page (~40 MB), `pages.json` ~2 KB/page per parser.

**Stop the pod** once the rsync has finished (terminate it once you're sure nothing else is needed from the volume).

## 7. Afterwards (laptop, no GPU)
```bash
git fetch && git checkout origin/gpu-run -- review/   # the comparison tables written on the pod
# or recompute from the rsynced caches:
uv run python tools/gpu/full_report.py --gpu-price 0.99 --tokens
```
Then record speeds, cost and scores in `PROGRESS.md` and decide the parser (plan step 3).

## What each piece is
| File | Role |
|---|---|
| `tools/gpu/setup_runpod.sh` | Pod setup: system packages, uv, `/workspace/venvs/{docling,mineru}` from pinned files (CUDA 13.0 or 12.8 by driver), writes `tools/gpu/env.sh` |
| `tools/gpu/session.sh` | models / smoke / bench / report / full-mineru / full-docling / full-pymupdf4llm / full-baseline / compare (pod mode via env.sh; Docker mode otherwise) |
| `tools/gpu/full_report.py` | Exhaustive comparison of the full runs: coverage, accuracy, speed, latency, resources, cost, output size -> `review/gpu/` |
| `tools/gpu/mineru_run.sh` | Start the MinerU2.5-Pro vLLM server, wait until ready, run the parser, stop the server |
| `tools/gpu/make_bench.py` | 200 random pages (seed 20261003) → `data/bench/`, same pages on every machine |
| `tools/gpu/bench_report.py` | Speed and cost table from the run summaries |
| `docker/requirements-{docling,mineru}-{cu130,cu128}.txt` | The pinned environments (see `docker/README.md`) |
| `docker/*.Dockerfile`, `tools/gpu/check_host.sh` | Docker-host path (not used on RunPod pods) |
| `src/cap_slice/batch_parse.py` (`cap-slice-parse`) | Batch runner: per-document cache, resume, per-run logs, GPU sampling |
| `src/cap_slice/parsing/mineru_vlm.py`, `docling_md.py` | Parser adapters (raw JSON + per-page Markdown) |
| `src/cap_slice/score.py` (`cap-slice-score`) | Golden v2 scoring from the caches |
