#!/usr/bin/env bash
# One GPU session, step by step. Run from the repo root on the GPU machine.
#
#   tools/gpu/session.sh models       # download MinerU models; warm up Docling's models
#   tools/gpu/session.sh smoke        # both parsers on one 4-page PDF (~minutes)
#   tools/gpu/session.sh bench        # 200-page benchmark: MinerU standard/advanced, Docling 1 vs N processes
#   tools/gpu/session.sh report       # benchmark table: pages/s and $ per 1,000 pages (set GPU_PRICE)
#   tools/gpu/session.sh full-mineru  # all PDFs with MinerU (MINERU_TIER, MINERU_WORKERS)
#   tools/gpu/session.sh full-docling # all PDFs with Docling (DOCLING_PROCS parallel processes, DOCLING_BATCH)
#   tools/gpu/session.sh build        # Docker mode only: build both images
#
# Two modes, same steps:
#   RunPod pod (no Docker): run tools/gpu/setup_runpod.sh first; it writes
#     tools/gpu/env.sh, and every step then runs from /workspace/venvs/{mineru,docling}.
#   Docker host: no env.sh -> steps run in the cap-slice-mineru / cap-slice-docling images.
# Every parse step is resumable: re-running skips documents already parsed.
# Knobs [defaults]: GPU_PRICE [0.99]  MINERU_TIER [standard]  MINERU_WORKERS [8]  DOCLING_BATCH [4]
#   DOCLING_PROCS [auto = CPUs allowed / 3, max 4] — parallel Docling processes, each on its own
#   share of the PDFs (pod 1: 4 processes x 3 threads = 1.2x one process; batch 16 = no gain).
set -euo pipefail
cd "$(dirname "$0")/../.."
mkdir -p parsed parsed_bench
SMOKE_PDF=data/C2C/periodic_results/2025-10-22_H1-FY2025-26-half-yearly-SME.pdf
BENCH=(data/bench/bench_01.pdf data/bench/bench_02.pdf data/bench/bench_03.pdf data/bench/bench_04.pdf)

if [ -f tools/gpu/env.sh ]; then
  MODE=venv
  # shellcheck disable=SC1091
  source tools/gpu/env.sh
  in_mineru()  { PATH="$VENVS/mineru/bin:$PATH" "$@"; }
  in_docling() { PATH="$VENVS/docling/bin:$PATH" "$@"; }
else
  MODE=docker
  MODELS=${MODELS:-$HOME/models}
  mkdir -p "$MODELS"
  RUN=(docker run --rm --gpus all --shm-size 8g --user "$(id -u):$(id -g)" -e HOME=/tmp
       -v "$PWD":/app -v "$MODELS":/models -w /app)
  in_mineru()  { "${RUN[@]}" ${EXTRA_ENV:+-e "$EXTRA_ENV"} cap-slice-mineru "$@"; }
  in_docling() { "${RUN[@]}" ${EXTRA_ENV:+-e "$EXTRA_ENV"} cap-slice-docling "$@"; }
fi

mineru()  { EXTRA_ENV="CAP_SLICE_MINERU_TIER=$1" CAP_SLICE_MINERU_TIER="$1" in_mineru tools/gpu/mineru_run.sh "${@:2}"; }

# CPUs this container may use (cgroup quota; nproc shows the whole host on RunPod).
cpus_allowed() {
  local q p; [ -r /sys/fs/cgroup/cpu.max ] || { nproc; return; }
  read -r q p < /sys/fs/cgroup/cpu.max
  [ "$q" = max ] && nproc || echo $(( q / p ))
}
# Parallel Docling: split the PDFs (largest first, round-robin by size) into N lists and
# run one cap-slice-parse per list, so no two processes ever touch the same file.
#   docling_parallel <procs> <batch> <out> [pdf...]   (no pdfs = every data/*/*/*.pdf)
docling_parallel() {
  local procs=$1 batch=$2 out=$3; shift 3
  local cpus; cpus=$(cpus_allowed); local threads=$(( cpus / procs )); [ "$threads" -lt 1 ] && threads=1
  local dir; dir=$(mktemp -d)
  if [ $# -gt 0 ]; then ls -S "$@"; else ls -S data/*/*/*.pdf; fi \
    | awk -v n="$procs" -v d="$dir" '{print > (d "/shard_" (NR % n) ".txt")}'
  echo "docling: $procs process(es) x $threads threads (CPUs allowed: $cpus), batch $batch -> $out"
  local i pids=()
  for i in $(seq 0 $(( procs - 1 ))); do
    [ -s "$dir/shard_$i.txt" ] || continue
    OMP_NUM_THREADS=$threads docling "$batch" --paths-file "$dir/shard_$i.txt" --out "$out" \
      2> >(grep --line-buffered -E "^\[|^done:|Error|Traceback" >&2) &
    pids+=($!)
  done
  local rc=0; for p in "${pids[@]}"; do wait "$p" || rc=1; done; return $rc
}
DOCLING_PROCS=${DOCLING_PROCS:-auto}
if [ "$DOCLING_PROCS" = auto ]; then DOCLING_PROCS=$(( $(cpus_allowed) / 3 )); [ "$DOCLING_PROCS" -gt 4 ] && DOCLING_PROCS=4; [ "$DOCLING_PROCS" -lt 1 ] && DOCLING_PROCS=1; fi
docling() { EXTRA_ENV="CAP_SLICE_DOCLING_BATCH=$1" CAP_SLICE_DOCLING_BATCH="$1" in_docling cap-slice-parse --parser docling "${@:2}"; }
export -f in_mineru in_docling 2>/dev/null || true

case "${1:-}" in
  build)
    [ "$MODE" = docker ] || { echo "Pod mode: use tools/gpu/setup_runpod.sh instead of build."; exit 1; }
    docker build -f docker/mineru.Dockerfile -t cap-slice-mineru .
    docker build -f docker/docling.Dockerfile -t cap-slice-docling .
    ;;
  models)
    in_mineru mineru-kit models download --tier standard --vlm-engine vllm
    in_mineru mineru-kit models show
    # Docling downloads its layout/table models on first use into $HF_HOME.
    docling 4 --paths "$SMOKE_PDF" --out /tmp/warmup
    ;;
  smoke)
    mineru standard --paths "$SMOKE_PDF" --out parsed_bench/smoke_mineru_standard --retry-failed
    docling 4 --paths "$SMOKE_PDF" --out parsed_bench/smoke_docling --retry-failed
    for f in parsed_bench/smoke_*/*/C2C/periodic_results/*/meta.json; do
      python3 -c "import json; m=json.load(open('$f')); print(m['status'], m['seconds'], 's', m.get('pages_returned'), 'pages', m.get('error', ''), '$f')"
    done
    ;;
  bench)
    [ -f data/bench/manifest.csv ] || in_docling python tools/gpu/make_bench.py
    mineru standard --paths "${BENCH[@]}" --out parsed_bench/mineru_standard_w4 --workers 4
    mineru advanced --paths "${BENCH[@]}" --out parsed_bench/mineru_advanced_w4 --workers 4
    docling_parallel 1 4 parsed_bench/docling_b4 "${BENCH[@]}"
    docling_parallel "$DOCLING_PROCS" 4 "parsed_bench/docling_b4_x$DOCLING_PROCS" "${BENCH[@]}"
    "$0" report
    ;;
  report)
    python3 tools/gpu/bench_report.py --price "${GPU_PRICE:-0.99}"
    ;;
  full-mineru)
    mineru "${MINERU_TIER:-standard}" --out parsed --workers "${MINERU_WORKERS:-8}" --largest-first
    ;;
  full-docling)
    docling_parallel "$DOCLING_PROCS" "${DOCLING_BATCH:-4}" parsed
    ;;
  *)
    sed -n '2,19p' "$0"; exit 1 ;;
esac
