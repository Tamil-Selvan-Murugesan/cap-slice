#!/usr/bin/env bash
# Inside the MinerU container: start the MinerU2.5-Pro VLM server (vLLM), wait
# until it answers, run cap-slice-parse against it, then stop the server.
#   tools/gpu/mineru_run.sh [cap-slice-parse args...]
# e.g. tools/gpu/mineru_run.sh --out parsed --workers 8
set -euo pipefail
LOG=${MINERU_SERVER_LOG:-/tmp/mineru_vlm_server.log}
# FlashInfer's sampler is JIT-compiled with the image's nvcc (CUDA 12.8 on the RunPod image), which
# can't target the RTX 5090 (sm_120) -> "FlashInfer requires GPUs with sm75 or higher". vLLM's
# PyTorch sampler needs no compiler (bugs_resolved.md I15).
export VLLM_USE_FLASHINFER_SAMPLER=${VLLM_USE_FLASHINFER_SAMPLER:-0}
WAIT_MIN=${MINERU_SERVER_WAIT_MIN:-45}   # first start on a network volume: imports alone took 5 min (pod 2)
up() { curl -sf -m 2 "${CAP_SLICE_MINERU_SERVER}/v1/models" >/dev/null; }
# A server already running (e.g. tools/gpu/session.sh vlm-server in its own tmux window) is
# reused and left running; otherwise start one for this run and stop it afterwards.
if up; then
  echo "using the VLM server already running at $CAP_SLICE_MINERU_SERVER"
else
  mineru-kit vlm-server --engine vllm ${MINERU_SERVER_ARGS:-} >"$LOG" 2>&1 &
  SERVER=$!
  trap 'kill $SERVER 2>/dev/null || true; wait $SERVER 2>/dev/null || true' EXIT
  echo "waiting for VLM server, up to $WAIT_MIN min (log: $LOG) ..."
  for i in $(seq 1 $(( WAIT_MIN * 12 ))); do
    up && break
    kill -0 $SERVER 2>/dev/null || { echo "VLM server exited:"; tail -40 "$LOG"; exit 1; }
    sleep 5
  done
  up || { echo "VLM server not ready after $WAIT_MIN min"; tail -40 "$LOG"; exit 1; }
fi
echo "VLM server ready."
cap-slice-parse --parser mineru "$@"
