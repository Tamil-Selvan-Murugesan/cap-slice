#!/usr/bin/env bash
# Inside the MinerU container: start the MinerU2.5-Pro VLM server (vLLM), wait
# until it answers, run cap-slice-parse against it, then stop the server.
#   tools/gpu/mineru_run.sh [cap-slice-parse args...]
# e.g. tools/gpu/mineru_run.sh --out parsed --workers 8
set -euo pipefail
LOG=${MINERU_SERVER_LOG:-/tmp/mineru_vlm_server.log}
mineru-kit vlm-server --engine vllm ${MINERU_SERVER_ARGS:-} >"$LOG" 2>&1 &
SERVER=$!
trap 'kill $SERVER 2>/dev/null || true; wait $SERVER 2>/dev/null || true' EXIT
echo "waiting for VLM server (log: $LOG) ..."
for i in $(seq 1 180); do
  curl -sf -m 2 "${CAP_SLICE_MINERU_SERVER}/v1/models" >/dev/null && break
  kill -0 $SERVER 2>/dev/null || { echo "VLM server exited:"; tail -40 "$LOG"; exit 1; }
  sleep 5
done
curl -sf -m 2 "${CAP_SLICE_MINERU_SERVER}/v1/models" >/dev/null || { echo "VLM server not ready after 15 min"; tail -40 "$LOG"; exit 1; }
echo "VLM server ready."
cap-slice-parse --parser mineru "$@"
