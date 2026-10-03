#!/usr/bin/env bash
# Sanity-check the GPU host before building anything. Run on the host (not in a container).
set -u
ok() { printf '  \033[32mOK\033[0m   %s\n' "$1"; }; bad() { printf '  \033[31mFAIL\033[0m %s\n' "$1"; FAILED=1; }; FAILED=0
echo "== GPU / driver";   nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader && ok "nvidia-smi" || bad "nvidia-smi not working"
drv=$(nvidia-smi --query-gpu=driver_version --format=csv,noheader 2>/dev/null | head -1 | cut -d. -f1)
[ -n "$drv" ] && { [ "$drv" -ge 580 ] && ok "driver $drv >= 580 (CUDA 13 / cu130 images OK)" || bad "driver $drv < 580: build images with --build-arg TORCH_BACKEND=cu126 (not possible on RTX 50xx — upgrade the driver)"; }
echo "== Docker + GPU";   docker run --rm --gpus all ubuntu:24.04 nvidia-smi -L >/dev/null 2>&1 && ok "docker --gpus all works" || bad "docker cannot see the GPU (install nvidia-container-toolkit, restart docker)"
echo "== CPU / RAM / disk"
c=$(nproc); [ "$c" -ge 8 ] && ok "$c CPUs" || bad "only $c CPUs (>= 8 recommended: page rendering + Docling pre-processing run on CPU)"
free -g | awk '/Mem:/{print "  RAM total " $2 " GB"}'
avail=$(df --output=avail -BG . | tail -1 | tr -dc 0-9); [ "$avail" -ge 60 ] && ok "${avail} GB free here" || bad "only ${avail} GB free (images ~15-20 GB, models ~5 GB, caches ~1 GB)"
echo "== Repo / data"
n=$(ls data/*/*/*.pdf 2>/dev/null | wc -l); [ "$n" -ge 228 ] && ok "$n PDFs under data/" || bad "$n PDFs under data/ (expected 228 — rsync them from the laptop)"
[ -f data/golden/v2_facts.csv ] && ok "golden set v2 present" || bad "data/golden/v2_facts.csv missing (git pull?)"
[ "$FAILED" = 0 ] && echo "All checks passed." || { echo "Fix the FAIL items first."; exit 1; }
