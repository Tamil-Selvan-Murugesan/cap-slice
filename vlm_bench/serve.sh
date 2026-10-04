#!/usr/bin/env bash
# Start ONE model server at a time:   ./serve.sh paddle | glm | unlimited
# Logs go to /workspace/logs/<model>_server.log. Stop with: pkill -f "vllm|genai_server"
#
# Single pod, one server at a time. GPU memory split: Paddle and GLM also run a layout model
# on the same GPU (client side), so their vLLM servers get 0.6 of VRAM. Unlimited-OCR has no
# layout stage -> 0.9.
set -euo pipefail
WS=/workspace
export HF_HOME=$WS/hf_cache
export PADDLE_PDX_CACHE_HOME=$WS/paddlex_cache
mkdir -p $WS/logs
MAX_SEQS=${MAX_SEQS:-256}

# vLLM >= 0.30 (GLM, Unlimited) uses FlashInfer, which finds nvcc via CUDA_HOME / PATH / /usr/local/cuda.
# The image's toolkit is CUDA 12.8, but FlashInfer needs >= 12.9 for the RTX 5090 (sm_120)
# ("SM 12.x requires CUDA >= 12.9" -> "FlashInfer requires GPUs with sm75 or higher"). Point it at the
# CUDA 13 nvcc that pip installed into the vllm_server venv (matches its torch cu130).
use_venv_cuda() {
  export CUDA_HOME=$WS/venvs/vllm_server/lib/python3.12/site-packages/nvidia/cu13
  export PATH=$CUDA_HOME/bin:$PATH
  # The only FlashInfer kernel that gets JIT-compiled is the top-k/top-p sampler, and that build fails
  # on this image ("CUDA compiler and CUDA toolkit headers are incompatible"). We decode greedily
  # (temperature 0), so use vLLM's PyTorch sampler instead: same output, nothing to compile.
  export VLLM_USE_FLASHINFER_SAMPLER=0
  echo "CUDA_HOME=$CUDA_HOME ($($CUDA_HOME/bin/nvcc --version | tail -1))"
}

case "${1:-}" in
  paddle)
    source $WS/venvs/paddle_server/bin/activate
    cat > $WS/logs/paddle_vllm.yml <<EOF
gpu-memory-utilization: ${GPU_UTIL:-0.6}
max-num-seqs: ${MAX_SEQS}
EOF
    nohup paddleocr genai_server --model_name PaddleOCR-VL-1.6-0.9B --backend vllm \
      --host 0.0.0.0 --port 8118 --backend_config $WS/logs/paddle_vllm.yml \
      > $WS/logs/paddle_server.log 2>&1 &
    PORT=8118 ;;

  paddle030)
    # Same PaddleOCR-VL-1.6 weights, chat template and served name as `paddle`, but on vLLM 0.30 instead of
    # the 0.10.2 that PaddleOCR's helper pins. On this pod the 0.10.2 server spent ~20 of the 31 CPU cores
    # on image preprocessing (pod CPU-throttled, GPU ~30% busy). The Paddle client works unchanged.
    source $WS/venvs/vllm_server/bin/activate
    use_venv_cuda
    nohup vllm serve $WS/paddlex_cache/official_models/PaddleOCR-VL-1.6 \
      --served-model-name PaddleOCR-VL-1.6-0.9B --port 8118 --trust-remote-code \
      --chat-template $WS/venvs/paddle_server/lib/python3.12/site-packages/paddlex/inference/genai/chat_templates/PaddleOCR-VL-1.6-0.9B.jinja \
      --api-server-count ${API_SERVERS:-4} --max-model-len 16384 --max-num-batched-tokens 131072 \
      --gpu-memory-utilization ${GPU_UTIL:-0.6} --max-num-seqs ${MAX_SEQS} \
      --no-enable-prefix-caching --mm-processor-cache-gb 0 \
      > $WS/logs/paddle030_server.log 2>&1 &
    PORT=8118 ;;

  glm)
    source $WS/venvs/vllm_server/bin/activate
    use_venv_cuda
    # MTP speculative decoding is part of GLM-OCR's published speed; keep it on.
    # The official recipe uses 1 speculative token (single MTP head). Try GLM_MTP=3 as a sweep point.
    nohup vllm serve zai-org/GLM-OCR --port 8080 --served-model-name glm-ocr \
      --speculative-config "{\"method\": \"mtp\", \"num_speculative_tokens\": ${GLM_MTP:-1}}" \
      --gpu-memory-utilization ${GPU_UTIL:-0.6} --max-num-seqs ${MAX_SEQS} \
      --max-model-len ${MAX_LEN:-16384} \
      > $WS/logs/glm_server.log 2>&1 &
    PORT=8080 ;;

  unlimited)
    # Unlimited-OCR is supported by stock vLLM since v0.27.0 (flags from the official recipe).
    # --moe-backend triton: its language model is MoE; vLLM 0.30 auto-picks FlashInfer CUTLASS, which
    # JIT-compiles fused_moe_120 for sm_120 and fails on this image (nvcc/header mismatch). Triton MoE
    # kernels compile fine (after the deepencoder LOG2E patch in setup_pod.sh).
    source $WS/venvs/vllm_server/bin/activate
    use_venv_cuda
    nohup vllm serve baidu/Unlimited-OCR --served-model-name unlimited-ocr --port 8000 \
      --trust-remote-code \
      --logits_processors vllm.model_executor.models.unlimited_ocr:NGramPerReqLogitsProcessor \
      --no-enable-prefix-caching --mm-processor-cache-gb 0 \
      --moe-backend triton \
      --allowed-local-media-path $WS \
      --gpu-memory-utilization ${GPU_UTIL:-0.9} --max-num-seqs ${MAX_SEQS} \
      > $WS/logs/unlimited_server.log 2>&1 &
    PORT=8000 ;;

  *) echo "usage: $0 paddle|paddle030|glm|unlimited"; exit 1 ;;
esac

echo -n "waiting for server on :$PORT "
for i in $(seq 1 180); do
  if curl -sf localhost:$PORT/v1/models >/dev/null 2>&1; then echo " up"; exit 0; fi
  echo -n "."; sleep 5
done
echo " timed out - see $WS/logs/"; exit 1
