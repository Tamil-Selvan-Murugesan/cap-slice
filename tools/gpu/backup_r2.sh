#!/usr/bin/env bash
# Back up everything a GPU run produced to Cloudflare R2 (S3-compatible), then verify.
#
#   tools/gpu/backup_r2.sh             # upload + verify
#   BACKUP_DRY_RUN=1 tools/gpu/backup_r2.sh   # show what would be uploaded, upload nothing
#
# Config — environment variables, or tools/gpu/r2.env (gitignored; see r2.env.example):
#   R2_ACCOUNT_ID         Cloudflare account ID (endpoint https://<id>.r2.cloudflarestorage.com)
#   R2_BUCKET             bucket name
#   R2_ACCESS_KEY_ID      R2 API token, Object Read & Write on that bucket
#   R2_SECRET_ACCESS_KEY
#   R2_PREFIX             [tamil/cap-slice/gpu-run-<today>] folder inside the bucket
#
# Uploads (mirrored file by file with rclone; re-runs send only new/changed files):
#   parsed/ parsed_advanced/ parsed_tune/ parsed_rehearsal/ parsed_bench/   every parser cache
#   review/                                                                scores and reports
#   /workspace/*.log, /tmp/mineru_vlm_server.log  -> logs/                 console + server logs
#   data/download_manifest.csv                    -> data/
# Never deletes anything, locally or in R2 (rclone copy, not sync). PDFs are not uploaded.
set -euo pipefail
cd "$(dirname "$0")/../.."

[ -f tools/gpu/r2.env ] && { set -a; . tools/gpu/r2.env; set +a; }
for v in R2_ACCOUNT_ID R2_BUCKET R2_ACCESS_KEY_ID R2_SECRET_ACCESS_KEY; do
  [ -n "${!v:-}" ] || { echo "missing $v (export it, or put it in tools/gpu/r2.env)"; exit 1; }
done
PREFIX=${R2_PREFIX:-tamil/cap-slice/gpu-run-$(date +%F)}

# rclone: one static binary, installed to ~/.local/bin if missing (no unzip needed)
if ! command -v rclone >/dev/null; then
  echo "== installing rclone"
  mkdir -p ~/.local/bin
  curl -fsSL -o /tmp/rclone.zip https://downloads.rclone.org/rclone-current-linux-amd64.zip
  python3 - <<'EOF'
import zipfile, os, stat
z = zipfile.ZipFile("/tmp/rclone.zip")
name = next(n for n in z.namelist() if n.endswith("/rclone"))
dst = os.path.expanduser("~/.local/bin/rclone")
open(dst, "wb").write(z.read(name))
os.chmod(dst, os.stat(dst).st_mode | stat.S_IEXEC)
EOF
  export PATH=$HOME/.local/bin:$PATH
fi
rclone version | head -1

# remote "r2" defined from the environment only: no rclone.conf, keys never written to disk
# provider "Other" (generic S3): the RunPod image ships rclone 1.58, which predates "Cloudflare" (1.59+)
export RCLONE_CONFIG_R2_TYPE=s3 RCLONE_CONFIG_R2_PROVIDER=Other RCLONE_CONFIG_R2_FORCE_PATH_STYLE=true \
       RCLONE_CONFIG_R2_ACCESS_KEY_ID=$R2_ACCESS_KEY_ID RCLONE_CONFIG_R2_SECRET_ACCESS_KEY=$R2_SECRET_ACCESS_KEY \
       RCLONE_CONFIG_R2_ENDPOINT=https://$R2_ACCOUNT_ID.r2.cloudflarestorage.com \
       RCLONE_CONFIG_R2_REGION=auto RCLONE_CONFIG_R2_NO_CHECK_BUCKET=true
export RCLONE_CONFIG=/dev/null   # no config file needed (silences "rclone.conf not found")
DEST="r2:$R2_BUCKET/$PREFIX"
OPTS=(--transfers 16 --checkers 32 --retries 5 --stats 30s --stats-one-line)
[ "${BACKUP_DRY_RUN:-0}" = 1 ] && OPTS+=(--dry-run)
echo "== destination: $R2_BUCKET/$PREFIX"

# what goes where: <local path> <remote subfolder>
items=()
for d in parsed parsed_advanced parsed_tune parsed_rehearsal parsed_bench review; do
  [ -d "$d" ] && items+=("$d" "$d")
done
logdir=$(mktemp -d)
cp /workspace/*.log /tmp/mineru_vlm_server.log "$logdir"/ 2>/dev/null || true
[ -n "$(ls -A "$logdir")" ] && items+=("$logdir" logs)
mkdir -p "$logdir.data" && cp data/download_manifest.csv "$logdir.data"/ && items+=("$logdir.data" data)

rc=0
for ((i = 0; i < ${#items[@]}; i += 2)); do
  src=${items[i]} sub=${items[i+1]}
  echo "== upload $src -> $sub/ ($(du -sh "$src" | cut -f1), $(find "$src" -type f | wc -l) files)"
  rclone copy "$src" "$DEST/$sub" "${OPTS[@]}" || rc=1
done
[ "${BACKUP_DRY_RUN:-0}" = 1 ] && { echo "dry run: nothing uploaded"; exit $rc; }

echo "== verify (every local file present in R2 with the same size/checksum)"
for ((i = 0; i < ${#items[@]}; i += 2)); do
  src=${items[i]} sub=${items[i+1]}
  if rclone check "$src" "$DEST/$sub" --one-way --checkers 32 -q; then echo "   ok   $sub"
  else echo "   FAIL $sub (re-run this script; it only sends what is missing)"; rc=1; fi
done
echo "== in R2 now:"; rclone size "$DEST"
rm -rf "$logdir" "$logdir.data"
exit $rc
