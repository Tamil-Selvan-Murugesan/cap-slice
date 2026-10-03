#!/usr/bin/env bash
# One GPU session, step by step. Run from the repo root on the GPU host.
#
#   tools/gpu/session.sh build        # build both images (~15-30 min, mostly downloads)
#   tools/gpu/session.sh models       # download MinerU models; warm up Docling's models
#   tools/gpu/session.sh smoke        # both parsers on one 4-page PDF (~minutes)
#   tools/gpu/session.sh bench        # 200-page benchmark: MinerU standard/advanced, Docling batch 4/16
#   tools/gpu/session.sh report       # benchmark table: pages/s and $ per 1,000 pages (set GPU_PRICE)
#   tools/gpu/session.sh full-mineru  # all PDFs with MinerU (MINERU_TIER, MINERU_WORKERS)
#   tools/gpu/session.sh full-docling # all PDFs with Docling (DOCLING_BATCH)
#
# Every step is resumable: re-running skips documents already parsed.
# Environment knobs (defaults in brackets):
#   MODELS [$HOME/models]   host folder mounted at /models (weights + caches)
#   GPU_PRICE [0.99]        $/hour, for the report
#   MINERU_TIER [standard]  MINERU_WORKERS [8]   DOCLING_BATCH [16]
set -euo pipefail
cd "$(dirname "$0")/../.."
MODELS=${MODELS:-$HOME/models}
mkdir -p "$MODELS" parsed parsed_bench
RUN=(docker run --rm --gpus all --shm-size 8g --user "$(id -u):$(id -g)" -e HOME=/tmp
     -v "$PWD":/app -v "$MODELS":/models -w /app)
SMOKE_PDF=data/C2C/periodic_results/2025-10-22_H1-FY2025-26-half-yearly-SME.pdf
BENCH=(data/bench/bench_01.pdf data/bench/bench_02.pdf data/bench/bench_03.pdf data/bench/bench_04.pdf)

mineru() { "${RUN[@]}" -e CAP_SLICE_MINERU_TIER="$1" cap-slice-mineru tools/gpu/mineru_run.sh "${@:2}"; }
docling() { "${RUN[@]}" -e CAP_SLICE_DOCLING_BATCH="$1" cap-slice-docling cap-slice-parse --parser docling "${@:2}"; }

case "${1:-}" in
  build)
    docker build -f docker/mineru.Dockerfile -t cap-slice-mineru .
    docker build -f docker/docling.Dockerfile -t cap-slice-docling .
    ;;
  models)
    "${RUN[@]}" cap-slice-mineru mineru-kit models download --tier standard --vlm-engine vllm
    "${RUN[@]}" cap-slice-mineru mineru-kit models show
    # Docling downloads its layout/table models on first use into /models/hf.
    docling 4 --paths "$SMOKE_PDF" --out /tmp/warmup
    ;;
  smoke)
    mineru standard --paths "$SMOKE_PDF" --out parsed_bench/smoke_mineru_standard --retry-failed
    docling 4 --paths "$SMOKE_PDF" --out parsed_bench/smoke_docling --retry-failed
    for f in parsed_bench/smoke_*/*/C2C/periodic_results/*/meta.json; do
      python3 -c "import json,sys; m=json.load(open('$f')); print(m['status'], m['seconds'], 's', m.get('pages_returned'), 'pages', '$f')"
    done
    ;;
  bench)
    [ -f data/bench/manifest.csv ] || "${RUN[@]}" cap-slice-docling python tools/gpu/make_bench.py
    mineru standard --paths "${BENCH[@]}" --out parsed_bench/mineru_standard_w4 --workers 4
    mineru advanced --paths "${BENCH[@]}" --out parsed_bench/mineru_advanced_w4 --workers 4
    docling 4  --paths "${BENCH[@]}" --out parsed_bench/docling_b4
    docling 16 --paths "${BENCH[@]}" --out parsed_bench/docling_b16
    "$0" report
    ;;
  report)
    python3 tools/gpu/bench_report.py --price "${GPU_PRICE:-0.99}"
    ;;
  full-mineru)
    mineru "${MINERU_TIER:-standard}" --out parsed --workers "${MINERU_WORKERS:-8}" --largest-first
    ;;
  full-docling)
    docling "${DOCLING_BATCH:-16}" --out parsed --largest-first
    ;;
  *)
    sed -n '2,20p' "$0"; exit 1 ;;
esac
