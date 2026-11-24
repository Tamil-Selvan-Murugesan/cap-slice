#!/usr/bin/env bash
# One round-2 chunking variant end to end: embed -> back up to R2 (verified) -> load into Qdrant ->
# search every filter setup -> score -> drop the collection (it reloads from the vectors without API calls).
#
#   tools/round2/run_variant.sh b1
#
# Needs VOYAGE_API_KEY in the environment and the local Qdrant server (tools/qdrant/serve.sh start).
# Local vector shards are kept only if KEEP_VECTORS=1; otherwise they are removed after the R2 backup
# has been verified and the searches have run (restore: copy back from R2, then `load`).
set -euo pipefail
cd "$(dirname "$0")/../.."
V=${1:?usage: $0 <variant>}
TAG=voyage-4-large-2048__r2-$V
OUT=review/retrieval/round2
run() { uv run --quiet "$@"; }

echo "== $V: embed"
run cap-slice-retrieval-dense embed --corpus "$V"
echo "== $V: back up to R2"
tools/backup_vectors_r2.sh "$TAG" | grep -E "^==|ok|files"
echo "== $V: load"
run cap-slice-retrieval-dense load --corpus "$V"
echo "== $V: search"
run cap-slice-retrieval-dense search --corpus "$V" --filter none --exact --out "$OUT/dense-$TAG-exact.jsonl"
for f in none company question question_next answer_key; do
  run cap-slice-retrieval-dense search --corpus "$V" --filter "$f"
  [ "$f" = none ] || run cap-slice-retrieval-dense search --corpus "$V" --filter "$f" --soft
done
echo "== $V: score"
for r in "$OUT"/dense-"$TAG"*.jsonl; do
  base=review/retrieval/$(basename "$r" | sed "s/__r2-$V//")
  run cap-slice-retrieval-score "$r" --compare "$base" | head -2
done
echo "== $V: drop collection"
curl -s -X DELETE "http://127.0.0.1:6333/collections/r2__voyage-4-large-2048__$V" >/dev/null
[ "${KEEP_VECTORS:-0}" = 1 ] || rm -rf "parsed_advanced/_vectors/$TAG"
df -h /mnt/c | tail -1
echo "== $V: done"
