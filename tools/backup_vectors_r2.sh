#!/usr/bin/env bash
# Back up one embedding run (and the chunk corpus it was made from) to Cloudflare R2, then verify.
#
#   tools/backup_vectors_r2.sh voyage-4-large-2048            # upload + verify
#   tools/backup_vectors_r2.sh voyage-4-large-2048__r2-b1     # a round-2 chunking variant
#   BACKUP_DRY_RUN=1 tools/backup_vectors_r2.sh voyage-4-large-2048
#
# Uploads to <bucket>/tamil/cap-slice/vectors/<tag>/:
#   vectors/   parsed_advanced/_vectors/<tag>/ (float32 shards, manifest.json with the corpus sha256,
#              log.jsonl, queries.json)
#   chunks/    the chunk corpus named in manifest.json (mineru.jsonl, or r2-<variant>.jsonl in round 2)
#   SOURCE.txt git commit, chunker tag, corpus sha256
# Restore: copy back to the same paths, then `cap-slice-retrieval-dense load --model ... --dim ...`
# rebuilds the Qdrant collection without calling the embedding API.
# Credentials from tools/gpu/r2.env (gitignored), passed to rclone through the environment only.
# Never deletes anything (rclone copy, not sync).
set -euo pipefail
cd "$(dirname "$0")/.."
TAG=${1:?usage: $0 <model-dim tag, e.g. voyage-4-large-2048>}
SRC=parsed_advanced/_vectors/$TAG
[ -f "$SRC/manifest.json" ] || { echo "no $SRC/manifest.json"; exit 1; }
CORPUS=$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["corpus"])' "$SRC/manifest.json")
CHUNKER=$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["chunker_version"])' "$SRC/manifest.json")
[ -f "$CORPUS" ] || { echo "corpus $CORPUS not found"; exit 1; }
set -a; . tools/gpu/r2.env; set +a
export PATH=$HOME/.local/bin:$PATH
export RCLONE_CONFIG_R2_TYPE=s3 RCLONE_CONFIG_R2_PROVIDER=Cloudflare \
       RCLONE_CONFIG_R2_ACCESS_KEY_ID=$R2_ACCESS_KEY_ID RCLONE_CONFIG_R2_SECRET_ACCESS_KEY=$R2_SECRET_ACCESS_KEY \
       RCLONE_CONFIG_R2_ENDPOINT=https://$R2_ACCOUNT_ID.r2.cloudflarestorage.com \
       RCLONE_CONFIG_R2_REGION=auto RCLONE_CONFIG_R2_NO_CHECK_BUCKET=true RCLONE_CONFIG=/dev/null
DEST="r2:$R2_BUCKET/tamil/cap-slice/vectors/$TAG"
OPTS=(--transfers 8 --checkers 16 --retries 5 --stats 30s --stats-one-line)
[ "${BACKUP_DRY_RUN:-0}" = 1 ] && OPTS+=(--dry-run)
info=$(mktemp -d)
{ echo "git commit:      $(git rev-parse HEAD)"
  echo "chunker version: $CHUNKER"
  echo "corpus:          $CORPUS"
  echo "corpus sha256:   $(sha256sum "$CORPUS" | cut -d' ' -f1)"
  echo "uploaded:        $(date -Iseconds)"; } > "$info/SOURCE.txt"
echo "== destination: $R2_BUCKET/tamil/cap-slice/vectors/$TAG"
rclone copy "$SRC" "$DEST/vectors" "${OPTS[@]}"
rclone copy "$CORPUS" "$DEST/chunks" "${OPTS[@]}"
rclone copy "$info/SOURCE.txt" "$DEST" "${OPTS[@]}"
[ "${BACKUP_DRY_RUN:-0}" = 1 ] && { echo "dry run: nothing uploaded"; exit 0; }
echo "== verify"
rclone check "$SRC" "$DEST/vectors" --one-way -q && echo "   ok   vectors"
rclone check "$(dirname "$CORPUS")" "$DEST/chunks" --one-way -q --include "$(basename "$CORPUS")" && echo "   ok   chunks"
rclone ls "$DEST" | awk '{n++; s+=$1} END {printf "   %d files, %.1f MB in R2\n", n, s/1e6}'
