#!/usr/bin/env bash
# Back up data/ to Cloudflare R2 (S3-compatible) under sirisha/data/, then verify.
#
#   ./backup_r2.sh                          # upload all of data/ + verify
#   ./backup_r2.sh parsing_eval/results     # only these paths inside data/ (same layout in R2)
#   BACKUP_DRY_RUN=1 ./backup_r2.sh         # show what would be uploaded, upload nothing
#
# Config — environment variables, or r2.env in the repo root (gitignored):
#   R2_ACCOUNT_ID         Cloudflare account ID (endpoint https://<id>.r2.cloudflarestorage.com)
#   R2_BUCKET             bucket name
#   R2_ACCESS_KEY_ID      R2 API token, Object Read & Write on that bucket
#   R2_SECRET_ACCESS_KEY
#   R2_PREFIX             [sirisha/data] folder inside the bucket
#
# Layout: data/<path> -> <bucket>/sirisha/data/<path> (filings per company, parsing_eval/, SQLite).
# pipeline.sqlite3 is uploaded as a consistent snapshot (SQLite backup API), never the live file;
# its -wal/-shm/.lock files and partial downloads are skipped.
# Never deletes anything, locally or in R2 (rclone copy, not sync); re-runs send only new/changed files.
set -euo pipefail
cd "$(dirname "$0")"

[ -f r2.env ] && { set -a; . ./r2.env; set +a; }
for v in R2_ACCOUNT_ID R2_BUCKET R2_ACCESS_KEY_ID R2_SECRET_ACCESS_KEY; do
  [ -n "${!v:-}" ] || { echo "missing $v (export it, or put it in r2.env)"; exit 1; }
done
PREFIX=${R2_PREFIX:-sirisha/data}

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
export RCLONE_CONFIG_R2_TYPE=s3 RCLONE_CONFIG_R2_PROVIDER=Other RCLONE_CONFIG_R2_FORCE_PATH_STYLE=true \
       RCLONE_CONFIG_R2_ACCESS_KEY_ID=$R2_ACCESS_KEY_ID RCLONE_CONFIG_R2_SECRET_ACCESS_KEY=$R2_SECRET_ACCESS_KEY \
       RCLONE_CONFIG_R2_ENDPOINT=https://$R2_ACCOUNT_ID.r2.cloudflarestorage.com \
       RCLONE_CONFIG_R2_REGION=auto RCLONE_CONFIG_R2_NO_CHECK_BUCKET=true
export RCLONE_CONFIG=/dev/null   # no config file needed (silences "rclone.conf not found")
DEST="r2:$R2_BUCKET/$PREFIX"
OPTS=(--transfers 16 --checkers 32 --retries 5 --stats 30s --stats-one-line)
[ "${BACKUP_DRY_RUN:-0}" = 1 ] && OPTS+=(--dry-run)
FILTER=(--exclude "/pipeline.sqlite3*" --exclude "*.part" --exclude "*.tmp")
echo "== destination: $R2_BUCKET/$PREFIX"

paths=("$@"); [ ${#paths[@]} -eq 0 ] && paths=(.)
rc=0
for p in "${paths[@]}"; do
  p=${p#data/}; p=${p%/}
  [ -e "data/$p" ] || { echo "   skip $p (not in data/)"; rc=1; continue; }
  sub=$([ "$p" = . ] && echo "" || echo "/$p")
  echo "== upload data/$p -> $PREFIX$sub ($(du -sh "data/$p" | cut -f1))"
  rclone copy "data/$p" "$DEST$sub" "${FILTER[@]}" "${OPTS[@]}" || rc=1
done

# SQLite: snapshot only when backing up all of data/
snap=""
if [ "${paths[0]}" = . ] && [ -f data/pipeline.sqlite3 ]; then
  snap=$(mktemp -d)
  python3 -c "import sqlite3,sys; s=sqlite3.connect(sys.argv[1]); d=sqlite3.connect(sys.argv[2]); s.backup(d); d.close()" \
    data/pipeline.sqlite3 "$snap/pipeline.sqlite3"
  echo "== upload pipeline.sqlite3 snapshot ($(du -sh "$snap/pipeline.sqlite3" | cut -f1))"
  rclone copy "$snap/pipeline.sqlite3" "$DEST" "${OPTS[@]}" || rc=1
fi
[ "${BACKUP_DRY_RUN:-0}" = 1 ] && { echo "dry run: nothing uploaded"; [ -n "$snap" ] && rm -rf "$snap"; exit $rc; }

echo "== verify (every local file present in R2 with the same size/checksum)"
for p in "${paths[@]}"; do
  p=${p#data/}; p=${p%/}; [ -e "data/$p" ] || continue
  sub=$([ "$p" = . ] && echo "" || echo "/$p")
  if rclone check "data/$p" "$DEST$sub" "${FILTER[@]}" --one-way --checkers 32 -q; then echo "   ok   data/$p"
  else echo "   FAIL data/$p (re-run this script; it only sends what is missing)"; rc=1; fi
done
if [ -n "$snap" ]; then
  if rclone check "$snap" "$DEST" --include pipeline.sqlite3 --one-way -q; then echo "   ok   pipeline.sqlite3"
  else echo "   FAIL pipeline.sqlite3"; rc=1; fi
  rm -rf "$snap"
fi
echo "== in R2 now:"; rclone size "$DEST"
exit $rc
