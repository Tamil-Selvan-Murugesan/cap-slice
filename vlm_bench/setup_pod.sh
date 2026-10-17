#!/usr/bin/env bash
# One-time setup of the single benchmark pod (all three models, run one after another).
# Pod: 1x RTX 5090 (Blackwell, sm_120), image runpod/pytorch:1.0.2-cu1281-torch280-ubuntu2404,
# host driver must support CUDA >= 12.9 (PaddlePaddle's Blackwell build needs it).
# Everything goes on the persistent volume at /workspace, so a stopped pod resumes without
# reinstalling. Takes ~20-40 min. Safe to re-run: completed venvs (.ok marker) are skipped,
# a venv whose block failed is resumed in place.
set -euo pipefail

export WS=/workspace
export HF_HOME=$WS/hf_cache                      # model weights (HuggingFace)
export PADDLE_PDX_CACHE_HOME=$WS/paddlex_cache   # Paddle layout/VLM model downloads
export UV_CACHE_DIR=$WS/uv_cache                 # same filesystem as venvs -> hardlinks, no copies
export CUDA_HOME=/usr/local/cuda                 # image ships the toolkit but not on PATH
export PATH=$CUDA_HOME/bin:$PATH
mkdir -p $WS/venvs $HF_HOME $PADDLE_PDX_CACHE_HOME $UV_CACHE_DIR $WS/logs

# ---- system tools (container disk; re-run this block after a pod restart)
apt-get update -qq && apt-get install -y -qq rsync tmux unzip > /dev/null

# ---- sanity: GPU, driver CUDA version, nvcc (flash-attn may need to compile)
nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader
nvidia-smi | grep -oE "CUDA (UMD )?Version: [0-9.]+"
command -v nvcc >/dev/null && nvcc --version | tail -1 || echo "WARN: nvcc not found"

command -v uv >/dev/null || pip install -q uv

mk() {  # skip a venv only if its block completed before (.ok marker); else (re)enter it
  [ -f "$WS/venvs/$1/.ok" ] && { echo "venv $1 complete, skipping"; return 1; }
  uv venv --python 3.12 --seed --allow-existing "$WS/venvs/$1"
}
ok() { touch "$WS/venvs/$1/.ok"; echo "venv $1 done"; }

# 1) Paddle VLM server: vLLM installed by PaddleOCR's own pinned helper
if mk paddle_server; then
  source $WS/venvs/paddle_server/bin/activate
  uv pip install "paddleocr[doc-parser]>=3.6.0"
  # The helper installs vllm+torch, then flash-attn from source. flash-attn's setup.py imports
  # torch, which pip's isolated build env lacks -> "No module named 'torch'". If that happens,
  # install flash-attn without build isolation (setup.py then fetches the prebuilt
  # cu12/torch2.8/cp312 wheel from GitHub, no compile) and re-run the helper.
  if ! paddleocr install_genai_server_deps vllm; then
    echo "helper failed (flash-attn build isolation) -> installing flash-attn --no-build-isolation"
    uv pip install packaging ninja wheel setuptools
    MAX_JOBS=16 uv pip install "flash-attn==2.8.3" --no-build-isolation   # version the helper pins
    paddleocr install_genai_server_deps vllm
  fi
  python -c "import vllm, flash_attn; print('paddle_server: vllm', vllm.__version__, '| flash_attn', flash_attn.__version__)"
  deactivate
  ok paddle_server
fi

# 2) Paddle client: PaddlePaddle runs the layout model. Must NOT share an env with vLLM.
#    Blackwell (sm_120) needs the cu129 build (PaddleOCR-VL Blackwell guide).
if mk paddle_client; then
  source $WS/venvs/paddle_client/bin/activate
  # Wheel straight from Baidu's CDN (~10 MB/s); its dependencies (CUDA libs, numpy, ...) come
  # from PyPI (~100 MB/s). Using --index-url for Paddle's index would pull ALL deps through it.
  uv pip install "https://paddle-whl.cdn.bcebos.com/stable/cu129/paddlepaddle-gpu/paddlepaddle_gpu-3.2.1-cp312-cp312-linux_x86_64.whl"
  uv pip install "paddleocr[doc-parser]>=3.6.0" psutil pyyaml
  deactivate
  ok paddle_client
fi

# 3) vLLM server for GLM-OCR and Unlimited-OCR (Unlimited-OCR is in vLLM since v0.27.0)
if mk vllm_server; then
  source $WS/venvs/vllm_server/bin/activate
  uv pip install "vllm>=0.30.0" "transformers>=5.0.0"
  deactivate
  ok vllm_server
fi
# vLLM 0.30 bug: Unlimited-OCR's vision encoder (deepencoder.py) uses the plain global LOG2E inside a
# Triton kernel; Triton 3.7 (pulled in by torch 2.13) rejects non-constexpr globals ->
# "NameError: Cannot access global variable LOG2E from within @jit'ed function" at server startup.
# Inline the constant (same value). Idempotent; original kept as .orig.
DE=$WS/venvs/vllm_server/lib/python3.12/site-packages/vllm/model_executor/models/deepencoder.py
if [ -f "$DE" ] && grep -q "\* LOG2E" "$DE"; then
  [ -f "$DE.orig" ] || cp "$DE" "$DE.orig"
  sed -i -E 's/\* LOG2E\b/* 1.4426950408889634/g' "$DE"
  echo "patched deepencoder.py (LOG2E inlined for Triton 3.7)"
fi

# 4) GLM-OCR client: official SDK (PP-DocLayoutV3 layout + calls to the vLLM server)
if mk glm_client; then
  source $WS/venvs/glm_client/bin/activate
  uv pip install "glmocr[selfhosted]" psutil pyyaml
  deactivate
  ok glm_client
fi

# 5) Tools: page rendering, Unlimited-OCR client, summaries, scoring
if mk tools; then
  source $WS/venvs/tools/bin/activate
  uv pip install pymupdf psutil openai pillow
  deactivate
  ok tools
fi

# 6) MinerU 4 (MinerU2.5-Pro on its own vLLM 0.28 + the small layout/table models, client side).
#    Pinned set from main (requirements-mineru-cu130.txt); needs a CUDA 13 driver, like vllm_server.
#    Models (~3 GB) go to MINERU_HOME and HF_HOME on /workspace.
if mk mineru; then
  source $WS/venvs/mineru/bin/activate
  uv pip install -r $WS/ocr_bench/requirements-mineru-cu130.txt --extra-index-url https://download.pytorch.org/whl/cu130 --index-strategy unsafe-best-match   # +cu130 torch wheels; works with old uv (no --torch-backend cu130)
  MINERU_HOME=$WS/mineru_home mineru-kit models download --tier standard --vlm-engine vllm   # "standard" = small models + MinerU2.5-Pro (also what advanced uses)
  deactivate
  ok mineru
fi

# ---- verify each env imports and sees the GPU
$WS/venvs/paddle_client/bin/python -c "import paddle; print('paddle', paddle.__version__, 'cuda:', paddle.device.is_compiled_with_cuda()); paddle.utils.run_check()" 2>&1 | tail -2
$WS/venvs/vllm_server/bin/python -c "import vllm, torch; print('vllm', vllm.__version__, '| torch', torch.__version__, '| gpu', torch.cuda.get_device_name(0), torch.cuda.get_device_capability(0))"
$WS/venvs/paddle_server/bin/python -c "import vllm; print('paddle_server vllm', vllm.__version__)"
$WS/venvs/glm_client/bin/python -c "import glmocr; print('glmocr ok')"
$WS/venvs/tools/bin/python -c "import pymupdf, openai, PIL, psutil; print('tools ok')"
$WS/venvs/mineru/bin/python -c "import importlib.metadata as m, vllm, torch; print('mineru', m.version('mineru'), '| vllm', vllm.__version__, '| cuda', torch.cuda.is_available())"
du -sh $WS/venvs $UV_CACHE_DIR 2>/dev/null
echo "done. venvs in $WS/venvs"
