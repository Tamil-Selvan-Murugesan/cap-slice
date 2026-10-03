#!/usr/bin/env bash
# One GPU session, step by step. Run from the repo root on the GPU machine.
#
#   tools/gpu/session.sh models       # download MinerU models; warm up Docling's models
#   tools/gpu/session.sh vlm-server   # MinerU VLM server, kept running in its own tmux window (optional, saves restarts)
#   tools/gpu/session.sh smoke        # all four parsers on one 4-page PDF (~minutes)
#   tools/gpu/session.sh bench        # 200-page benchmark: MinerU standard/advanced, Docling and PyMuPDF4LLM 1 vs N processes, baseline
#   tools/gpu/session.sh report       # benchmark table: pages/s and $ per 1,000 pages (set GPU_PRICE)
#   tools/gpu/session.sh rehearse     # all four parsers on 5 golden docs + scores + report -> parsed_rehearsal/ (~20 min)
#   tools/gpu/session.sh full-mineru  # all PDFs with MinerU (MINERU_TIER, MINERU_WORKERS)
#   tools/gpu/session.sh full-docling # all PDFs with Docling (DOCLING_PROCS parallel processes, DOCLING_BATCH)
#   tools/gpu/session.sh full-pymupdf4llm  # all PDFs with PyMuPDF4LLM on GPU (P4L_PROCS)
#   tools/gpu/session.sh full-baseline     # all PDFs with the current pipeline's extraction, CPU only (BASELINE_PROCS)
#   tools/gpu/session.sh compare      # golden v1+v2 scores for every parser + review/gpu/COMPARISON.md (GPU_PRICE, VCPU_PRICE)
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
REHEARSE=(data/E2E/annual_reports/2023-09-21_FY2022-23.pdf data/APARINDS/investor_presentations/Nov-2017-a.pdf
          data/E2E/concall_transcripts/May-2024.pdf data/APARINDS/investor_presentations/May-2025.pdf
          data/E2E/periodic_results/2026-04-20_Q4-FY2025-26-quarterly.pdf)
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
# Parallel runs (Docling, PyMuPDF4LLM, baseline): split the PDFs (largest first, round-robin
# by size) into N lists and run one cap-slice-parse per list, so no two processes ever touch
# the same file. Threads per process = CPUs allowed / N.
#   parse_parallel <parser> <procs> <out> [pdf...]   (no pdfs = every data/*/*/*.pdf)
parse_parallel() {
  local parser=$1 procs=$2 out=$3; shift 3
  local cpus; cpus=$(cpus_allowed); local threads=$(( cpus / procs )); [ "$threads" -lt 1 ] && threads=1
  local dir; dir=$(mktemp -d)
  if [ $# -gt 0 ]; then ls -S "$@"; else ls -S data/*/*/*.pdf; fi \
    | awk -v n="$procs" -v d="$dir" '{print > (d "/shard_" (NR % n) ".txt")}'
  echo "$parser: $procs process(es) x $threads threads (CPUs allowed: $cpus) -> $out"
  local i pids=()
  for i in $(seq 0 $(( procs - 1 ))); do
    [ -s "$dir/shard_$i.txt" ] || continue
    EXTRA_ENV="CAP_SLICE_DOCLING_BATCH=${DOCLING_BATCH:-4}" CAP_SLICE_DOCLING_BATCH=${DOCLING_BATCH:-4} \
    OMP_NUM_THREADS=$threads in_docling cap-slice-parse --parser "$parser" --paths-file "$dir/shard_$i.txt" --out "$out" \
      2> >(grep --line-buffered -E "^\[|^done:|Error|Traceback" >&2) &
    pids+=($!)
  done
  local rc=0; for p in "${pids[@]}"; do wait "$p" || rc=1; done; return $rc
}
docling_parallel() { local procs=$1 batch=$2; shift 2; DOCLING_BATCH=$batch parse_parallel docling "$procs" "$@"; }
DOCLING_PROCS=${DOCLING_PROCS:-auto}
if [ "$DOCLING_PROCS" = auto ]; then DOCLING_PROCS=$(( $(cpus_allowed) / 3 )); [ "$DOCLING_PROCS" -gt 4 ] && DOCLING_PROCS=4; [ "$DOCLING_PROCS" -lt 1 ] && DOCLING_PROCS=1; fi
P4L_PROCS=${P4L_PROCS:-$DOCLING_PROCS}       # PyMuPDF4LLM: GPU OCR/layout + CPU work, like Docling
BASELINE_PROCS=${BASELINE_PROCS:-$(cpus_allowed)}   # baseline is single-threaded CPU work
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
  vlm-server)
    # keep MinerU's VLM server up in its own tmux window; every MinerU step then reuses it
    # instead of paying the start-up (5-15 min on a network volume) each time. Ctrl+C stops it.
    in_mineru mineru-kit vlm-server --engine vllm ${MINERU_SERVER_ARGS:-} 2>&1 | tee /tmp/mineru_vlm_server.log
    ;;
  smoke)
    mineru standard --paths "$SMOKE_PDF" --out parsed_bench/smoke_mineru_standard --retry-failed
    docling 4 --paths "$SMOKE_PDF" --out parsed_bench/smoke_docling --retry-failed
    CAP_SLICE_DEVICE=${CAP_SLICE_DEVICE:-cuda} parse_parallel pymupdf4llm 1 parsed_bench/smoke_pymupdf4llm "$SMOKE_PDF"
    parse_parallel baseline 1 parsed_bench/smoke_baseline "$SMOKE_PDF"
    for f in parsed_bench/smoke_*/*/C2C/periodic_results/*/meta.json; do
      python3 -c "import json; m=json.load(open('$f')); print(m['status'], m['seconds'], 's', m.get('pages_returned'), 'pages', m.get('error', ''), m.get('info', {}).get('ocr_gpu', ''), '$f')"
    done
    ;;
  bench)
    [ -f data/bench/manifest.csv ] || in_docling python tools/gpu/make_bench.py
    mineru standard --paths "${BENCH[@]}" --out parsed_bench/mineru_standard_w4 --workers 4
    mineru advanced --paths "${BENCH[@]}" --out parsed_bench/mineru_advanced_w4 --workers 4
    docling_parallel 1 4 parsed_bench/docling_b4 "${BENCH[@]}"
    docling_parallel "$DOCLING_PROCS" 4 "parsed_bench/docling_b4_x$DOCLING_PROCS" "${BENCH[@]}"
    parse_parallel pymupdf4llm 1 parsed_bench/pymupdf4llm "${BENCH[@]}"
    parse_parallel pymupdf4llm "$P4L_PROCS" "parsed_bench/pymupdf4llm_x$P4L_PROCS" "${BENCH[@]}"
    parse_parallel baseline 1 parsed_bench/baseline "${BENCH[@]}"
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
  full-pymupdf4llm)
    parse_parallel pymupdf4llm "$P4L_PROCS" parsed
    ;;
  full-baseline)
    parse_parallel baseline "$BASELINE_PROCS" parsed
    ;;
  rehearse)
    # dress rehearsal of the full run on 5 golden documents (240 pages, incl. a 164-page AR with
    # scanned statements): every parser, both golden sets, the full report -> parsed_rehearsal/
    R=parsed_rehearsal; rm -rf "$R"
    mineru standard --paths "${REHEARSE[@]}" --out "$R" --workers 4 --largest-first
    docling_parallel "$DOCLING_PROCS" 4 "$R" "${REHEARSE[@]}"
    parse_parallel pymupdf4llm "$P4L_PROCS" "$R" "${REHEARSE[@]}"
    parse_parallel baseline "$BASELINE_PROCS" "$R" "${REHEARSE[@]}"
    for p in baseline pymupdf4llm docling mineru; do
      [ -d "$R/$p" ] || continue
      in_docling cap-slice-score --parser "$p" --cache "$R" --out "$R/review/v2" | tail -1
      in_docling cap-slice-score --parser "$p" --cache "$R" --facts data/golden/parse_facts.csv --out "$R/review/v1" | tail -1
    done
    in_docling python tools/gpu/full_report.py --gpu-price "${GPU_PRICE:-0.99}" --root "$R" --review "$R/review" --out "$R/review/gpu" --tokens
    ;;
  compare)
    # golden-set scores (v2: 150 facts, v1: 28 facts) for every parser that has a cache,
    # then the full comparison table -> review/gpu/COMPARISON.md
    for p in baseline pymupdf4llm docling mineru; do
      [ -d "parsed/$p" ] || continue
      in_docling cap-slice-score --parser "$p" --cache parsed --out review/v2
      in_docling cap-slice-score --parser "$p" --cache parsed --facts data/golden/parse_facts.csv --out review/v1
    done
    in_docling python tools/gpu/full_report.py --gpu-price "${GPU_PRICE:-0.99}" ${VCPU_PRICE:+--vcpu-price "$VCPU_PRICE"} --tokens
    ;;
  *)
    sed -n '2,21p' "$0"; exit 1 ;;
esac
