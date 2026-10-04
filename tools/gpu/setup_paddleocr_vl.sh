#!/usr/bin/env bash
# Add PaddleOCR-VL-1.6 to a pod already set up with tools/gpu/setup_runpod.sh (run that first).
# Mirrors the setup the co-founder tested on a RunPod RTX 5090 (branch main-sirisha, vlm_bench/):
#   $VENVS/paddle   PaddlePaddle 3.2.1 (cu129 build: Blackwell sm_120 needs it) + paddleocr[doc-parser]
#                   -> the layout model and pipeline, run by cap-slice-parse --parser paddleocr_vl
#   $VENVS/vllm030  vLLM >= 0.30 -> serves the 0.9B VLM (their `serve.sh paddle030`: ~2x faster than the
#                   vLLM 0.10.2 that PaddleOCR's own server helper pins, same output). PaddlePaddle and
#                   vLLM must not share an env.
#   weights         PaddlePaddle/PaddleOCR-VL-1.6 from HuggingFace via PaddleX's own downloader, into
#                   $MODELS/paddlex/official_models/PaddleOCR-VL-1.6 (the path their server read)
# Needs a driver with CUDA >= 12.9. Safe to re-run: finished envs (.ok marker) are skipped.
#   tools/gpu/setup_paddleocr_vl.sh
set -euo pipefail
cd "$(dirname "$0")/../.."
[ -f tools/gpu/env.sh ] || { echo "run tools/gpu/setup_runpod.sh first (writes tools/gpu/env.sh)"; exit 1; }
source tools/gpu/env.sh
export PATH=$HOME/.local/bin:$PATH UV_LINK_MODE=copy UV_CACHE_DIR=${UV_CACHE_DIR:-$WS/.uv-cache}
export PADDLE_PDX_CACHE_HOME=$MODELS/paddlex HF_HOME=${HF_HOME:-$MODELS/hf}
mkdir -p "$PADDLE_PDX_CACHE_HOME"
df -h "$WS" | tail -1

mk() { [ -f "$VENVS/$1/.ok" ] && { echo "== $1 env done, skipping"; return 1; }
       echo "== $1 env"; uv venv --python 3.12 --seed --allow-existing "$VENVS/$1"; }

if mk paddle; then
  py=$VENVS/paddle/bin/python
  # wheel straight from Baidu's CDN; its dependencies come from PyPI
  uv pip install -p "$py" "https://paddle-whl.cdn.bcebos.com/stable/cu129/paddlepaddle-gpu/paddlepaddle_gpu-3.2.1-cp312-cp312-linux_x86_64.whl"
  uv pip install -p "$py" "paddleocr[doc-parser]>=3.6.0" pymupdf psutil
  uv pip install -p "$py" --no-deps -e .     # cap-slice-parse / cap-slice-score without docling+torch
  touch "$VENVS/paddle/.ok"
fi

if mk vllm030; then
  uv pip install -p "$VENVS/vllm030/bin/python" "vllm>=0.30.0" "transformers>=5.0.0"
  touch "$VENVS/vllm030/.ok"
fi

echo "== PaddleOCR-VL-1.6 weights"
"$VENVS/paddle/bin/python" -c "
from paddlex.inference.utils.official_models import official_models
print('weights:', official_models['PaddleOCR-VL-1.6'])"

# session.sh reads these from env.sh
grep -q PADDLE_PDX_CACHE_HOME tools/gpu/env.sh || cat >> tools/gpu/env.sh <<EOF
export PADDLE_PDX_CACHE_HOME=$PADDLE_PDX_CACHE_HOME
export CAP_SLICE_PADDLE_SERVER=http://127.0.0.1:8118/v1
EOF

echo "== checks"
"$VENVS/paddle/bin/python" -c "import paddle; print('paddle', paddle.__version__, 'cuda:', paddle.device.is_compiled_with_cuda()); paddle.utils.run_check()" 2>&1 | tail -2
"$VENVS/vllm030/bin/python" -c "import vllm, torch; print('vllm', vllm.__version__, '| torch', torch.__version__, '| gpu', torch.cuda.get_device_name(0), torch.cuda.get_device_capability(0))"
"$VENVS/paddle/bin/python" -c "import cap_slice.parsing.paddleocr_vl; print('cap-slice adapter ok')"
du -sh "$VENVS/paddle" "$VENVS/vllm030" "$PADDLE_PDX_CACHE_HOME" 2>/dev/null
echo "Done. Next: tools/gpu/session.sh paddle-server (own tmux window), then smoke-paddle"
