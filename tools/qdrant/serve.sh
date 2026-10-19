#!/usr/bin/env bash
# Start a local Qdrant server (official binary, no Docker) for the retrieval experiments.
#   tools/qdrant/serve.sh            # start in the background; logs to data/qdrant/qdrant.log
#   tools/qdrant/serve.sh stop
# Binary: https://github.com/qdrant/qdrant/releases (v1.19.1, x86_64-unknown-linux-gnu; sha256
# eef986e769d4d3e806dd2d546e1b4ecdd416211e54d34b4ed764fac7c58e1085), unpacked to $QDRANT_HOME.
# Listens on 127.0.0.1 only (REST 6333, gRPC 6334); storage in data/qdrant/ (gitignored).
set -euo pipefail
REPO="$(cd "$(dirname "$0")/../.." && pwd)"
QDRANT_HOME="${QDRANT_HOME:-$HOME/.local/opt/qdrant/v1.19.1}"
DATA="$REPO/data/qdrant"
PIDFILE="$DATA/qdrant.pid"
if [[ "${1:-}" == "stop" ]]; then
  [[ -f "$PIDFILE" ]] && kill "$(cat "$PIDFILE")" && rm -f "$PIDFILE" && echo "stopped"
  exit 0
fi
if [[ -f "$PIDFILE" ]] && kill -0 "$(cat "$PIDFILE")" 2>/dev/null; then
  echo "already running (pid $(cat "$PIDFILE"))"; exit 0
fi
mkdir -p "$DATA/storage" "$DATA/snapshots"
cd "$DATA"
QDRANT__SERVICE__HOST=127.0.0.1 \
QDRANT__STORAGE__STORAGE_PATH="$DATA/storage" \
QDRANT__STORAGE__SNAPSHOTS_PATH="$DATA/snapshots" \
QDRANT__TELEMETRY_DISABLED=true \
  nohup "$QDRANT_HOME/qdrant" >> "$DATA/qdrant.log" 2>&1 &
echo $! > "$PIDFILE"
for _ in $(seq 30); do
  curl -sf http://127.0.0.1:6333/readyz >/dev/null && { echo "qdrant ready (pid $(cat "$PIDFILE"))"; exit 0; }
  sleep 1
done
echo "qdrant did not become ready; see $DATA/qdrant.log" >&2; exit 1
