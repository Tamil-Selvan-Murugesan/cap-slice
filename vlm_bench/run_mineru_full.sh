#!/usr/bin/env bash
# Pod: wait for the Paddle full run to exit, then MinerU 4 (advanced, parse_mode=ocr) on all 15,683 pages.
# 4 processes x 1 PDF each (MINERU_PROCS / MINERU_WORKERS). Smoke on the 3 smallest PDFs first; the full
# run starts only if every smoke page was written. Re-run to resume (--skip-existing).
set -uo pipefail
source /workspace/ocr_bench/env.sh
FP=/workspace/data/full_pages
PROCS=${MINERU_PROCS:-4} WORKERS=${MINERU_WORKERS:-1}
echo "== $(date +%T) waiting for the Paddle run to exit"
while pgrep -f "run_paddle.py" >/dev/null; do sleep 30; done
echo "== $(date +%T) Paddle done: $(find /workspace/results_full/paddleocr-vl-1.6/full/md -name "*.json" | wc -l) page JSONs"
pkill -f "vllm serve"; sleep 20
./serve.sh mineru || { tail -40 $WS/logs/mineru_server.log; exit 1; }
source $WS/venvs/mineru/bin/activate
# RAM (pod limit 62 GB): each process holds its own models and one page window. Give freed memory back
# after every window, and use 32-page windows (default 64, ~12 GB peak per process on large reports).
export MINERU_MALLOC_TRIM=1 MALLOC_ARENA_MAX=2 MINERU_PROCESSING_WINDOW_SIZE=${MINERU_PROCESSING_WINDOW_SIZE:-32}
python - <<PY
import json, collections
rows=[json.loads(l) for l in open("$FP/manifest.jsonl")]
by=collections.defaultdict(list)
for r in rows: by[r["pdf"]].append(r)
small=sorted(by, key=lambda p: len(by[p]))[:3]
open("/workspace/data/mineru_smoke.jsonl","w").writelines(json.dumps(r)+"\n" for p in small for r in by[p])
print("smoke:", [(p.split("/")[-1], len(by[p])) for p in small])
PY
PYTHONUNBUFFERED=1 python run_mineru.py --manifest /workspace/data/mineru_smoke.jsonl --procs 3 --workers 1 \
  --results /workspace/results_full --run-name smoke 2>&1 | tee $WS/logs/mineru_smoke.log
want=$(wc -l < /workspace/data/mineru_smoke.jsonl)
got=$(find /workspace/results_full/mineru2.5-pro/smoke/md -name "*.json" | wc -l)
echo "== smoke: $got / $want pages"
[ "$got" -eq "$want" ] && [ ! -f /workspace/results_full/mineru2.5-pro/smoke/failures.jsonl ] \
  || { echo "SMOKE FAILED - not starting the full run"; exit 1; }
echo "== $(date +%T) full run: $PROCS processes x $WORKERS PDF(s)"
PYTHONUNBUFFERED=1 python run_mineru.py --manifest $FP/manifest.jsonl --procs $PROCS --workers $WORKERS \
  --skip-existing --results /workspace/results_full --run-name full 2>&1 | tee -a $WS/logs/mineru_full.log
