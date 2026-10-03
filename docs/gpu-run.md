# GPU run — runbook (RunPod)

Parse all 228 PDFs (12,980 pages) with **MinerU 4 + MinerU2.5-Pro** and **Docling** on one RunPod GPU pod, measure speed and cost, and bring the caches home. Plan and reasoning: [`plan.md`](plan.md). Everything below is copy-paste; every parse step resumes if interrupted.

> Agents working on the pod: read `AGENTS.md`, `PROGRESS.md`, this file and `bugs_resolved.md` first. Don't change parser code mid-run — measured speeds must stay comparable.

**How it runs on RunPod.** A pod is itself a container, so Docker can't run inside it. Instead `tools/gpu/setup_runpod.sh` builds the **same two isolated environments** the Dockerfiles define — `/workspace/venvs/docling` and `/workspace/venvs/mineru` — from the same pinned files in `docker/`. The pipeline code is the code tested on the laptop; only the setup differs. (The Dockerfiles stay for later: a pre-built image as a RunPod template would make every future pod start ready.)

## 0. Create the pod (RunPod console)
| Setting | Value |
|---|---|
| GPU | **RTX 5090** (A40 fallback if step 3 fails on the 5090). Prices noted 2026-10-02: A40 $0.53/h, RTX 5090 $0.99/h, A100 $1.59/h |
| Container image | `runpod/pytorch:1.0.2-cu1281-torch280-ubuntu2404` (Ubuntu 24.04 — the pins target it; its own PyTorch is not used) |
| Volume disk | **≥ 80 GB**, mounted at `/workspace` (venvs ~15 GB, models ~5 GB, PDFs ~1 GB, caches ~1 GB) |
| Container disk | ≥ 30 GB (system packages) |
| CUDA version filter | **≥ 13.0 required** (MinerU's vLLM is a CUDA 13 build). Docling would also run on 12.8 |
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
tools/gpu/session.sh smoke       # ~1–2 min: each parser on one 4-page PDF; both lines must start with "ok"
```
If `smoke` fails on the RTX 5090 with CUDA/arch errors ("no kernel image", "sm_120"), stop and move to an A40 pod instead of debugging on the meter.

## 4. Benchmark (200 fixed pages, same set on any GPU)
```bash
GPU_PRICE=0.99 tools/gpu/session.sh bench     # builds data/bench/, runs 4 variants, prints the report
```
Variants: MinerU `standard` and `advanced` (4 documents in flight), Docling with batch 4 and 16. The report gives pages/s, **$ per 1,000 pages**, time for this collection, and projected cost for 11–14M pages.

**Pick the full-run settings from it:**
- MinerU tier: run `standard` for the full collection. Also run `advanced` in full **only if** its projected time for this collection is under ~4 h.
- Docling batch: whichever variant was faster.
- MinerU workers: start at 8; if GPU utilisation in the report is < 70 %, use 16.

## 5. Full run (MinerU first, then Docling — one at a time, so speeds stay clean)
```bash
MINERU_TIER=standard MINERU_WORKERS=8 tools/gpu/session.sh full-mineru
DOCLING_BATCH=16                       tools/gpu/session.sh full-docling
```
Progress prints one line per document with the running pages/s. To also run `advanced` in full (its own cache folder):
```bash
source tools/gpu/env.sh && CAP_SLICE_MINERU_TIER=advanced PATH=$VENVS/mineru/bin:$PATH \
  tools/gpu/mineru_run.sh --out parsed_advanced --workers 8 --largest-first
```
Failed documents are listed in `parsed/<parser>/_runs/<run_id>.jsonl`; re-run the same command with `--retry-failed` added once.

## 6. Bring results home, then stop the pod
```bash
# on the pod: commit run logs and summaries (not caches — they're big and gitignored)
git add -f parsed*/*/_runs parsed_bench/*/*/_runs data/bench/manifest.csv
git commit -m "GPU run: benchmark and full-run logs" && git push -u origin gpu-run
```
```bash
# on the laptop: pull the caches (check `df -h /mnt/c` first — keep ≥ 500 MB free)
rsync -av -e "ssh -p PORT" --include='*/' --include='pages.json' --include='meta.json' --exclude='*' \
      root@IP:/workspace/cap-slice/parsed/ parsed/            # per-page text only: ~60 MB
rsync -av -e "ssh -p PORT" root@IP:/workspace/cap-slice/parsed/ /some/bigger/disk/parsed/   # + raw JSON (~0.5 GB)
```
Expected sizes (from the laptop tests): Docling `docling.json` ~30 KB/page (~0.4 GB total), MinerU `mineru_middle.json` ~3 KB/page (~40 MB), `pages.json` ~2 KB/page per parser.

**Stop the pod** once the rsync has finished (terminate it once you're sure nothing else is needed from the volume).

## 7. Afterwards (laptop, no GPU)
```bash
uv run cap-slice-score --parser mineru     # golden v2 -> review/v2/mineru.md
uv run cap-slice-score --parser docling
```
Then record speeds, cost and scores in `PROGRESS.md` and decide the parser (plan step 3).

## What each piece is
| File | Role |
|---|---|
| `tools/gpu/setup_runpod.sh` | Pod setup: system packages, uv, `/workspace/venvs/{docling,mineru}` from pinned files (CUDA 13.0 or 12.8 by driver), writes `tools/gpu/env.sh` |
| `tools/gpu/session.sh` | models / smoke / bench / report / full-mineru / full-docling (pod mode via env.sh; Docker mode otherwise) |
| `tools/gpu/mineru_run.sh` | Start the MinerU2.5-Pro vLLM server, wait until ready, run the parser, stop the server |
| `tools/gpu/make_bench.py` | 200 random pages (seed 20261003) → `data/bench/`, same pages on every machine |
| `tools/gpu/bench_report.py` | Speed and cost table from the run summaries |
| `docker/requirements-{docling,mineru}-{cu130,cu128}.txt` | The pinned environments (see `docker/README.md`) |
| `docker/*.Dockerfile`, `tools/gpu/check_host.sh` | Docker-host path (not used on RunPod pods) |
| `src/cap_slice/batch_parse.py` (`cap-slice-parse`) | Batch runner: per-document cache, resume, per-run logs, GPU sampling |
| `src/cap_slice/parsing/mineru_vlm.py`, `docling_md.py` | Parser adapters (raw JSON + per-page Markdown) |
| `src/cap_slice/score.py` (`cap-slice-score`) | Golden v2 scoring from the caches |
