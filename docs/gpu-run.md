# GPU run — runbook

Parse all 228 PDFs (12,980 pages) with **MinerU 4 + MinerU2.5-Pro** and **Docling** on one rented GPU, measure speed and cost, and bring the caches home. Plan and reasoning: [`plan.md`](plan.md). Everything below is copy-paste; every parse step resumes if interrupted.

> Agents working on the GPU box: read `AGENTS.md`, `PROGRESS.md`, this file and `bugs_resolved.md` first. Don't change parser code mid-run — measured speeds must stay comparable.

## 0. Rent the machine — a bare Ubuntu VM
Docker must run on the machine, so it has to be a **real VM** (not a container-based pod such as a RunPod pod, where Docker can't run).
- **OS:** Ubuntu **24.04** (the pinned packages were resolved for its glibc 2.39).
- **GPU:** RTX 5090 (planned; A40 fallback if the 5090 fails at step 4). Prices noted 2026-10-02: A40 $0.53/h, RTX 5090 $0.99/h, A100 $1.59/h. Note the price — the report needs it.
- **≥ 8 CPU cores, ≥ 32 GB RAM, ≥ 100 GB disk** (images ~15–20 GB, models ~5 GB), **public SSH** (for rsync).

## 1. Machine setup (once, as a sudo user)
Skip any line the provider has already done (check with `nvidia-smi`, `docker --version`).
```bash
# NVIDIA driver: R580+ (the images use CUDA 13.0). The RTX 5090 needs the *open* kernel modules.
sudo apt update && sudo apt install -y nvidia-driver-580-open && sudo reboot
nvidia-smi                                   # after reboot: shows the GPU and "CUDA Version: 13.x"

# Docker
curl -fsSL https://get.docker.com | sudo sh
sudo usermod -aG docker $USER && newgrp docker

# NVIDIA Container Toolkit (lets Docker use the GPU) — NVIDIA's apt repo, then configure Docker
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg
curl -fsSL https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list \
  | sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' \
  | sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list
sudo apt update && sudo apt install -y nvidia-container-toolkit
sudo nvidia-ctk runtime configure --runtime=docker && sudo systemctl restart docker

# Tools
sudo apt install -y git rsync tmux python3
curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash - && sudo apt install -y nodejs
sudo npm install -g @anthropic-ai/claude-code @openai/codex     # agents on the host, not in the images
```
Package names and repo URLs can change — if a line fails, follow the provider's / NVIDIA's current install guide for that step.

**Repo:**
```bash
git clone git@github.com:Tamil-Selvan-Murugesan/cap-slice.git && cd cap-slice   # or your SSH alias
git checkout -b gpu-run                      # all cloud commits go here, not main
```
- **GitHub access from the box:** add a *repo-scoped* deploy key with write access (or a fine-grained token for this repo only) — not your personal login.
- **Claude Code memory:** copy `~/.claude/projects/-home-tamil-work-cap-slice/memory/` from the laptop to the box, renamed to match the repo path there (for `/home/ubuntu/cap-slice` it is `-home-ubuntu-cap-slice`). It carries preferences such as "no AI attribution in commits".

## 2. Data (from the laptop)
Code comes from git; only the PDFs are copied — never rsync the whole repo over the clone.
```bash
# on the laptop, from the repo root
rsync -av --prune-empty-dirs --include='*/' --include='*.pdf' --exclude='*' \
      data/ USER@HOST:~/cap-slice/data/
```

## 3. Check the host
```bash
tools/gpu/check_host.sh          # driver, docker --gpus, CPUs, disk, 228 PDFs, golden set
```

## 4. Build, models, smoke (~30–45 min, mostly downloads)
The pipeline code was tested on the laptop (CPU); what's new here is only the images, so `build` + `smoke` are where a setup problem would show up.
```bash
tools/gpu/session.sh build       # both images — run this first: a build problem shows up within ~15 min
tools/gpu/session.sh models      # MinerU small models + MinerU2.5-Pro-2605-1.2B into ~/models; Docling warm-up
tools/gpu/session.sh smoke       # ~1-2 min: each parser on one 4-page PDF; both must print "ok"
```
If `smoke` fails on an RTX 5090 with CUDA/arch errors ("no kernel image", "sm_120"), stop and switch to the A40 instead of debugging on the meter.

## 5. Benchmark (200 fixed pages, same set on any GPU)
```bash
GPU_PRICE=0.99 tools/gpu/session.sh bench     # builds data/bench/, runs 4 variants, prints the report
```
Variants: MinerU `standard` and `advanced` (4 docs in flight), Docling with batch 4 and 16. The report gives pages/s, **$ per 1,000 pages**, time for this collection, and projected cost for 11–14M pages.

**Pick the full-run settings from it:**
- MinerU tier: run `standard` for the full collection. Also run `advanced` in full **only if** its projected time for this collection is under ~4 h.
- Docling batch: whichever variant was faster.
- MinerU workers: start at 8; if GPU utilisation in the report is < 70 %, try 16 on the next step.

## 6. Full run (MinerU first, then Docling — one at a time, so speeds stay clean)
```bash
MINERU_TIER=standard MINERU_WORKERS=8 tools/gpu/session.sh full-mineru
DOCLING_BATCH=16                       tools/gpu/session.sh full-docling
```
Run them inside `tmux` so a dropped SSH session doesn't stop them. Progress prints one line per document with the running pages/s. To run `advanced` too, it needs its own cache folder:
```bash
docker run --rm --gpus all --shm-size 8g --user "$(id -u):$(id -g)" -e HOME=/tmp \
  -e CAP_SLICE_MINERU_TIER=advanced -v "$PWD":/app -v ~/models:/models -w /app cap-slice-mineru \
  tools/gpu/mineru_run.sh --out parsed_advanced --workers 8 --largest-first
```
Failed documents are listed in `parsed/<parser>/_runs/<run_id>.jsonl`; re-run with `--retry-failed` once.

## 7. Bring results home, then stop the machine
```bash
# on the box: commit run logs and summaries (not caches — they're big and gitignored)
git add -f parsed*/*/_runs parsed_bench/*/*/_runs data/bench/manifest.csv
git commit -m "GPU run: benchmark and full-run logs" && git push -u origin gpu-run
```
```bash
# on the laptop: pull the caches (check `df -h /mnt/c` first)
rsync -av --include='*/' --include='pages.json' --include='meta.json' --exclude='*' \
      USER@HOST:~/cap-slice/parsed/ parsed/           # per-page text only: ~60 MB
rsync -av USER@HOST:~/cap-slice/parsed/ /some/bigger/disk/parsed/   # + raw JSON (~0.5 GB)
```
Expected sizes (from the laptop tests): Docling `docling.json` ~30 KB/page (~0.4 GB total), MinerU `mineru_middle.json` ~3 KB/page (~40 MB), `pages.json` ~2 KB/page per parser.

**Stop the GPU** once the rsync has finished.

## 8. Afterwards (laptop, no GPU)
```bash
uv run cap-slice-score --parser mineru     # golden v2 -> review/v2/mineru.md
uv run cap-slice-score --parser docling
```
Then record speeds, cost and scores in `PROGRESS.md` and decide the parser (plan step 3).

## What each piece is
| File | Role |
|---|---|
| `docker/*.Dockerfile`, `docker/requirements-*.txt` | The two images, pinned (see `docker/README.md`) |
| `tools/gpu/check_host.sh` | Host checks |
| `tools/gpu/session.sh` | build / models / smoke / bench / report / full-mineru / full-docling |
| `tools/gpu/mineru_run.sh` | Inside the MinerU image: start the vLLM server, wait, run the parser, stop |
| `tools/gpu/make_bench.py` | 200 random pages (seed 20261003) → `data/bench/`, same pages on every machine |
| `tools/gpu/bench_report.py` | Speed and cost table from the run summaries |
| `src/cap_slice/batch_parse.py` (`cap-slice-parse`) | Batch runner: per-document cache, resume, per-run logs, GPU sampling |
| `src/cap_slice/parsing/mineru_vlm.py`, `docling_md.py` | Parser adapters (raw JSON + per-page Markdown) |
| `src/cap_slice/score.py` (`cap-slice-score`) | Golden v2 scoring from the caches |
