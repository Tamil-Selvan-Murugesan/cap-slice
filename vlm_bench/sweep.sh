#!/usr/bin/env bash
# Concurrency sweep for one model (server must already be up via serve.sh).
#   ./sweep.sh paddle    ./sweep.sh glm    ./sweep.sh unlimited
# Every run saves per-page markdown, so the same sweep gives throughput AND the outputs
# that score.py grades for accuracy. Warm-up uses separate pages (WARMUP manifest).
set -euo pipefail
WS=/workspace
export HF_HOME=$WS/hf_cache                      # client-side layout models land on the volume
export PADDLE_PDX_CACHE_HOME=$WS/paddlex_cache
cd "$(dirname "$0")"
MANIFEST=${MANIFEST:-$WS/data/pages/manifest.jsonl}
WARMUP=${WARMUP:-$WS/data/pages/warmup.jsonl}
RESULTS=${RESULTS:-$WS/results}
WARM_ARG=""
[ -f "$WARMUP" ] && WARM_ARG="--warmup-manifest $WARMUP"

case "${1:-}" in
  paddle)
    source $WS/venvs/paddle_client/bin/activate
    for c in ${LEVELS:-16 32 64 128 256}; do
      python run_paddle.py --manifest $MANIFEST $WARM_ARG --results $RESULTS --concurrency $c
    done ;;
  glm)
    source $WS/venvs/glm_client/bin/activate
    for w in ${LEVELS:-2 4 8 16}; do
      python run_glm.py --manifest $MANIFEST $WARM_ARG --results $RESULTS --workers $w
    done ;;
  unlimited)
    source $WS/venvs/tools/bin/activate      # client: openai + pillow + psutil
    for c in ${LEVELS:-8 32 64 128 256}; do
      python3 run_unlimited.py --manifest $MANIFEST $WARM_ARG --results $RESULTS --concurrency $c
    done
    # multi-page mode (its headline feature), a couple of points; skip with MULTI=0
    [ "${MULTI:-1}" = "0" ] && exit 0
    for c in 8 32; do
      python3 run_unlimited.py --manifest $MANIFEST $WARM_ARG --results $RESULTS \
        --concurrency $c --pages-per-request 4
    done ;;
  *) echo "usage: $0 paddle|glm|unlimited"; exit 1 ;;
esac
