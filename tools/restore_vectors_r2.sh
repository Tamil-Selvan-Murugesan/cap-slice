#!/usr/bin/env bash
# Restore one embedding run (and its chunk corpus) from Cloudflare R2 — the reverse of backup_vectors_r2.sh.
#
#   tools/restore_vectors_r2.sh voyage-4-large-2048__r2-b2
#
# Copies <bucket>/tamil/cap-slice/vectors/<tag>/vectors/ to parsed_advanced/_vectors/<tag>/ and the chunk file to
# parsed_advanced/_chunks/ (skipped if an identical file is already there), then checks both. Afterwards
# `cap-slice-retrieval-dense load ...` rebuilds the Qdrant collection without calling the embedding API.
set -euo pipefail
cd "$(dirname "$0")/.."
TAG=${1:?usage: $0 <tag, e.g. voyage-4-large-2048__r2-b2>}
set -a; . tools/gpu/r2.env; set +a
export PATH=$HOME/.local/bin:$PATH
export RCLONE_CONFIG_R2_TYPE=s3 RCLONE_CONFIG_R2_PROVIDER=Cloudflare \
       RCLONE_CONFIG_R2_ACCESS_KEY_ID=$R2_ACCESS_KEY_ID RCLONE_CONFIG_R2_SECRET_ACCESS_KEY=$R2_SECRET_ACCESS_KEY \
       RCLONE_CONFIG_R2_ENDPOINT=https://$R2_ACCOUNT_ID.r2.cloudflarestorage.com \
       RCLONE_CONFIG_R2_REGION=auto RCLONE_CONFIG_R2_NO_CHECK_BUCKET=true RCLONE_CONFIG=/dev/null
SRC="r2:$R2_BUCKET/tamil/cap-slice/vectors/$TAG"
OPTS=(--transfers 8 --checkers 16 --retries 5 --stats 30s --stats-one-line)
rclone copy "$SRC/vectors" "parsed_advanced/_vectors/$TAG" "${OPTS[@]}"
rclone copy "$SRC/chunks" parsed_advanced/_chunks "${OPTS[@]}"
rclone check "$SRC/vectors" "parsed_advanced/_vectors/$TAG" --one-way -q && echo "   ok   vectors"
rclone check "$SRC/chunks" parsed_advanced/_chunks --one-way -q && echo "   ok   chunks"
