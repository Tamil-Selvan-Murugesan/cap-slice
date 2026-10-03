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
# docling: cu130 when the driver supports CUDA >= 13.0, else cu128.
# mineru: cu130 on CUDA 13 drivers, else cu129 (vLLM's +cu129 build; runs on 12.x drivers).
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
# Always use the uv version the pins were resolved with: images can ship an older
# uv (runpod/pytorch has 0.9.0, which doesn't know --torch-backend cu130).
UV_VERSION=0.12.5
if [ "$("$HOME/.local/bin/uv" --version 2>/dev/null | awk '{print $2}')" != "$UV_VERSION" ]; then
  curl -LsSf "https://astral.sh/uv/$UV_VERSION/install.sh" | env UV_NO_MODIFY_PATH=1 sh
fi
export PATH=$HOME/.local/bin:$PATH
hash -r
uv --version
[ "$(uv --version | awk '{print $2}')" = "$UV_VERSION" ] || { echo "wrong uv on PATH: $(command -v uv)"; exit 1; }

echo "== CUDA version supported by the driver"
cuda=$(nvidia-smi | sed -n 's/.*CUDA Version: *\([0-9]*\)\.\([0-9]*\).*/\1\2/p' | head -1)
if [ -z "$cuda" ]; then echo "nvidia-smi shows no CUDA version — is this a GPU pod?"; exit 1; fi
if [ "$cuda" -ge 130 ]; then BACKEND=cu130; elif [ "$cuda" -ge 128 ]; then BACKEND=cu128; else
  echo "Driver supports CUDA ${cuda:0:2}.${cuda:2} — need >= 12.8. Pick a pod with a newer driver (RunPod: filter by CUDA version)."; exit 1; fi
# MinerU's vLLM wheels (>= 0.19, required by MinerU 4) are built for CUDA 13, so the
# MinerU env always uses cu130 pins and needs a CUDA 13 driver. (A cu128 MinerU set
# resolved fine but mixed CUDA 12.8 torch with CUDA-13 vLLM: libcudart.so.13 errors.)
# MinerU: vLLM's PyPI wheel is a CUDA 13 build -> cu130 pins on CUDA 13 drivers;
# on CUDA 12.x drivers use vLLM's +cu129 GitHub build with cu129 torch (runs on any
# 12.x driver via CUDA minor-version compatibility).
if [ "$cuda" -ge 130 ]; then MINERU_BACKEND=cu130; else MINERU_BACKEND=cu129; fi
# vLLM refuses Blackwell GPUs (RTX 50xx, compute capability 12.x) unless the driver
# supports CUDA >= 12.9 ("SM 12.x requires CUDA >= 12.9" — seen on a driver-570 pod).
sm=$(nvidia-smi --query-gpu=compute_cap --format=csv,noheader | head -1 | cut -d. -f1)
if [ "${sm:-0}" -ge 12 ] && [ "$cuda" -lt 129 ]; then
  echo "WARNING: $(nvidia-smi --query-gpu=name --format=csv,noheader | head -1) needs a CUDA >= 12.9 driver for vLLM (MinerU);"
  echo "         this driver supports CUDA ${cuda:0:2}.${cuda:2}. Docling will work here; MinerU will not."
  echo "         For MinerU, deploy a pod with RunPod's CUDA version filter = 13.0."
  SKIP_MINERU=1
fi
echo "driver CUDA ${cuda:0:2}.${cuda:2} -> docling: $BACKEND pins (or existing env), mineru: $MINERU_BACKEND pins"

mkdir -p "$VENVS" "$MODELS/hf" "$MODELS/mineru"
export UV_CACHE_DIR=$WS/.uv-cache UV_LINK_MODE=copy
for env in docling mineru; do
  py="$VENVS/$env/bin/python"
  [ "$env" = mineru ] && [ "${SKIP_MINERU:-0}" = 1 ] && { echo "== venv: mineru — skipped (driver too old for vLLM on this GPU)"; continue; }
  # CUDA build of an existing env, read from its installed torch (e.g. 2.11.0+cu128).
  have=""; [ -x "$py" ] && have=$("$py" -c "import torch; print(torch.__version__.split('+')[1])" 2>/dev/null || true)
  if [ "$env" = mineru ]; then
    backend=$MINERU_BACKEND                     # cu130, or cu129 vLLM build on CUDA 12.x drivers
  else
    backend=${have:-$BACKEND}                   # keep a working Docling env (cu128 runs fine on a CUDA 13 driver)
  fi
  echo "== venv: $env ($backend)"
  if [ -n "$have" ] && [ "$have" != "$backend" ]; then
    echo "   existing env has torch +$have, need +$backend — recreating"
    rm -rf "$VENVS/$env"
  fi
  [ -x "$py" ] || uv venv "$VENVS/$env" -p python3.12
  req="docker/requirements-$env-$backend.txt"
  if [ ! -f "$req" ]; then                     # no pinned list yet (cu129): resolve on the pod from the .in file
    req="docker/$env-$backend.in"
    echo "   no pinned list for $backend — installing from $req and freezing the result"
  fi
  uv pip install -p "$py" --torch-backend "$backend" -r "$req"
  uv pip install -p "$py" --no-deps -e .
  if [ "$env" = docling ]; then
    # Docling's OCR (RapidOCR) runs on onnxruntime; the pinned CPU build silently ignores
    # the GPU. Swap in onnxruntime-gpu built for this CUDA major version (uninstall the CPU
    # build first — both packages share files). 1.22.0 = CUDA 12 build (verified on a
    # driver-570 pod); current PyPI releases are CUDA 13 builds (need libcublasLt.so.13).
    case "$backend" in cu12*) ORT_GPU="onnxruntime-gpu==1.22.0";; *) ORT_GPU="onnxruntime-gpu";; esac
    if ! "$py" -c "import onnxruntime as o; o.get_device()=='GPU' or exit(1)" 2>/dev/null; then
      uv pip uninstall -p "$py" onnxruntime >/dev/null 2>&1 || true
      uv pip install -p "$py" "$ORT_GPU"
    fi
    m=$("$py" -c "import rapidocr, os; print(os.path.join(os.path.dirname(rapidocr.__file__), 'models', 'PP-OCRv6_det_small.onnx'))")
    if [ -f "$m" ]; then
      "$py" -c "import torch, onnxruntime as o; s=o.InferenceSession('$m', providers=['CUDAExecutionProvider','CPUExecutionProvider']); p=s.get_providers(); print('   docling OCR providers:', p); exit(0 if p[0]=='CUDAExecutionProvider' else 1)" \
        || echo "   WARNING: Docling OCR will run on CPU (onnxruntime-gpu could not use CUDA here)"
    fi
  fi
  case "$req" in *.in) uv pip freeze -p "$py" | grep -v "^-e " > "docker/requirements-$env-$backend.txt"
                       echo "   froze docker/requirements-$env-$backend.txt (commit it on the gpu-run branch)";; esac
  if uv pip list -p "$py" 2>/dev/null | grep -qiE "cu13|nvidia-cuda-runtime +13" && [ "$backend" != cu130 ]; then
    echo "   WARNING: CUDA 13 packages in a $backend env:"; uv pip list -p "$py" | grep -iE "cu13|nvidia-cuda-runtime"; fi
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
[ "${SKIP_MINERU:-0}" = 1 ] || "$VENVS/mineru/bin/python" -c "import torch, vllm, mineru; print('mineru env: torch', torch.__version__, 'vllm', vllm.__version__, 'cuda', torch.cuda.is_available())"
df -h "$WS" | tail -1
echo "Setup done. Next: tools/gpu/session.sh models"
