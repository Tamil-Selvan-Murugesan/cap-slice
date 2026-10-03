#!/usr/bin/env bash
# Set up a RunPod pod for the GPU parse — no Docker (pods can't run it).
# Run once, from the repo root on the pod (repo at /workspace/cap-slice):
#
#   tools/gpu/setup_runpod.sh
#
# Creates two separate Python environments (vLLM pins its own PyTorch, which
# can clash with Docling's) from the same pinned files the Dockerfiles use:
#   /workspace/venvs/docling   docker/requirements-docling-<cuda>.txt + cap-slice
#   /workspace/venvs/mineru    docker/requirements-mineru-<cuda>.txt  + cap-slice (no deps)
# <cuda> is cu130 when the driver supports CUDA >= 13.0, else cu128.
# Writes tools/gpu/env.sh (sourced by session.sh): model/cache locations on /workspace.
# Everything lives on /workspace (the persistent volume); the container disk is wiped on restart.
set -euo pipefail
cd "$(dirname "$0")/../.."
WS=${WORKSPACE:-/workspace}
VENVS=$WS/venvs
MODELS=$WS/models

echo "== system packages"
export DEBIAN_FRONTEND=noninteractive
apt-get update -qq
# build-essential + python3.12-dev: Triton (used by vLLM) compiles small C helpers at runtime.
apt-get install -y -qq --no-install-recommends python3.12 python3.12-venv python3.12-dev \
    build-essential git curl rsync tmux ca-certificates libgl1 libglib2.0-0 libgomp1 >/dev/null

echo "== uv"
command -v uv >/dev/null || curl -LsSf https://astral.sh/uv/install.sh | sh
export PATH=$HOME/.local/bin:$PATH
uv --version

echo "== CUDA version supported by the driver"
cuda=$(nvidia-smi | sed -n 's/.*CUDA Version: *\([0-9]*\)\.\([0-9]*\).*/\1\2/p' | head -1)
if [ -z "$cuda" ]; then echo "nvidia-smi shows no CUDA version — is this a GPU pod?"; exit 1; fi
if [ "$cuda" -ge 130 ]; then BACKEND=cu130; elif [ "$cuda" -ge 128 ]; then BACKEND=cu128; else
  echo "Driver supports CUDA ${cuda:0:2}.${cuda:2} — need >= 12.8. Pick a pod with a newer driver (RunPod: filter by CUDA version)."; exit 1; fi
echo "driver CUDA ${cuda:0:2}.${cuda:2} -> using $BACKEND pins"

mkdir -p "$VENVS" "$MODELS/hf" "$MODELS/mineru"
export UV_CACHE_DIR=$WS/.uv-cache UV_LINK_MODE=copy
for env in docling mineru; do
  echo "== venv: $env"
  [ -x "$VENVS/$env/bin/python" ] || uv venv "$VENVS/$env" -p python3.12
  uv pip install -p "$VENVS/$env/bin/python" --torch-backend "$BACKEND" -r "docker/requirements-$env-$BACKEND.txt"
  uv pip install -p "$VENVS/$env/bin/python" --no-deps -e .
done

cat > tools/gpu/env.sh <<EOF
# Written by setup_runpod.sh — sourced by session.sh. Not committed.
export WS=$WS VENVS=$VENVS MODELS=$MODELS TORCH_BACKEND=$BACKEND
export HF_HOME=$MODELS/hf MINERU_HOME=$MODELS/mineru
export CAP_SLICE_DEVICE=cuda CAP_SLICE_MINERU_SERVER=http://127.0.0.1:30000
export PATH=$HOME/.local/bin:\$PATH
EOF

echo "== checks"
"$VENVS/docling/bin/python" -c "import torch, docling; print('docling env: torch', torch.__version__, 'cuda', torch.cuda.is_available(), torch.cuda.get_device_name(0))"
"$VENVS/mineru/bin/python" -c "import torch, vllm, mineru; print('mineru env: torch', torch.__version__, 'vllm', vllm.__version__, 'cuda', torch.cuda.is_available())"
df -h "$WS" | tail -1
echo "Setup done. Next: tools/gpu/session.sh models"
