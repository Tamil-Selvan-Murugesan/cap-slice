# Pod steps — before the full run

Run these by hand, in order, on a RunPod pod (RTX 5090, CUDA ≥ 13.0). Stop at any step whose check fails.
Laptop commands are marked **(laptop)**; everything else runs on the pod.
Replace `IP` and `PORT` with the pod's values from RunPod → Connect → "SSH over exposed TCP".

## Step 1 — Connect and check the pod
```bash
ssh root@IP -p PORT -i ~/.ssh/run_pod          # (laptop)
nvidia-smi | head -4                           # "CUDA Version" must be 13.0 or higher
cat /sys/fs/cgroup/cpu.max                     # first number ÷ second = CPUs you get
df -h /workspace /                             # free space on the volume and the local disk
```

## Step 2 — tmux
Everything from here runs inside tmux, so a dropped SSH connection doesn't stop it.
```bash
tmux new -s gpu                                # later: tmux attach -t gpu
```
Ctrl+b c = new window · Ctrl+b w = list windows · Ctrl+b d = detach.

## Step 3 — Clone the repo
```bash
cd /workspace
git clone https://github.com/Tamil-Selvan-Murugesan/cap-slice.git
cd cap-slice
git log --oneline -1                           # latest main commit
```
If the repo is already there: `cd /workspace/cap-slice && git pull`.

## Step 4 — Setup
```bash
tools/gpu/setup_runpod.sh 2>&1 | tee /workspace/setup.log
```
- If it stops with "CUDA can't start on this pod": terminate the pod and deploy another.
- Takes 20–40 min on a network volume (the install step looks stuck for a long time; it isn't).
- Check: `grep -iE "warn|error|skip" /workspace/setup.log` — no "skipping MinerU".

## Step 5 — Check the environments
```bash
cd /workspace/cap-slice && source tools/gpu/env.sh
$VENVS/docling/bin/python -c "import torch, onnxruntime as o; print(torch.__version__, torch.cuda.is_available(), o.__version__, o.get_device())"
$VENVS/mineru/bin/python -c "import torch, vllm; print(torch.__version__, torch.cuda.is_available(), vllm.__version__)"
$VENVS/docling/bin/python -c "from cap_slice.parsing.pymupdf4llm_md import _configure; print(_configure('cuda'))" 2>&1 | grep -E "Failed to load|WARNING|device"
```
Expect:
- `2.14.0+cu130 True … GPU`
- `2.13.0+cu130 True 0.28.0`
- only `{'device': 'cuda', 'layout_gpu': True, 'ocr_gpu': True}` (no "Failed to load", no "WARNING")

## Step 6 — PDFs: download on the pod
```bash
cd /workspace/cap-slice
curl -s -o /dev/null -w "%{http_code}|%{content_type}|%{size_download}\n" \
  -A "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36" \
  "https://archives.nseindia.com/annual_reports/SME_AR_31945_C2C_2025_2026_A_3304192_08092026201026.pdf"
```
Expect `200|application/pdf|3304192`. Then (~15–25 min, sequential, 3 s apart):
```bash
$VENVS/docling/bin/cap-slice-download --no-update-matrix 2>&1 | tee /workspace/download.log
```

## Step 7 — Check the PDFs against the laptop's hashes
```bash
cd /workspace/cap-slice
git show HEAD:data/download_manifest.csv > /tmp/laptop_manifest.csv
python3 - <<'EOF'
import csv, glob, hashlib
m = {r['path']: r['sha256'] for r in csv.DictReader(open('/tmp/laptop_manifest.csv')) if r['sha256'] and r['path'].endswith('.pdf')}
local = sorted(p for p in glob.glob('data/*/*/*.pdf') if '/bench/' not in p)
bad = [p for p in local if hashlib.sha256(open(p, 'rb').read()).hexdigest() != m.get(p)]
print(len(local), 'on pod;', len(bad), 'differ:', bad)
print('missing:'); print('\n'.join(sorted(set(m) - set(local))))
EOF
git checkout data/download_manifest.csv
```
Expect `228 on pod; 0 differ` and nothing under `missing:`. Last time 6 APAR files needed copying from the laptop:

## Step 8 — (laptop) Copy missing or differing files
List the paths from step 7 (relative to `data/`), one per line:
```bash
cd ~/work/cap-slice                            # (laptop)
printf '%s\n' \
  APARINDS/annual_reports/FY2011-12.pdf \
  APARINDS/annual_reports/FY2012-13.pdf \
  APARINDS/annual_reports/FY2015-16.pdf \
  APARINDS/concall_transcripts/Nov-2018-b.pdf \
  APARINDS/investor_presentations/Aug-2018.pdf \
  APARINDS/investor_presentations/May-2018.pdf \
| rsync -tv --no-owner --no-group --files-from=- \
  -e "ssh -p PORT -i ~/.ssh/run_pod" \
  data/ root@IP:/workspace/cap-slice/data/
```
Re-run step 7 until it shows `228 on pod; 0 differ`, nothing missing.

## Step 9 — (optional) Docling environment on the local disk
Only if `df -h /` shows more free space than the Docling env (~11 GB). The pod's local disk is wiped on every stop/restart — redo this after one.
```bash
cp -a /workspace/venvs/docling /root/docling-venv
mv /workspace/venvs/docling /workspace/venvs/docling.net
ln -s /root/docling-venv /workspace/venvs/docling
```
To undo (e.g. after a restart): `rm /workspace/venvs/docling && mv /workspace/venvs/docling.net /workspace/venvs/docling`.

## Step 10 — Models
```bash
cd /workspace/cap-slice
tools/gpu/session.sh models 2>&1 | tee /workspace/models.log
```
Expect `standard: … ready` for both MinerU repos (ONNX and GGUF "missing" is fine). The Docling warm-up at the end prints nothing for a few minutes.

## Step 11 — Start the MinerU server (own window, leave it running)
```bash
tmux new-window -t gpu -n vlm 'cd /workspace/cap-slice && tools/gpu/session.sh vlm-server; echo "SERVER EXITED"; exec bash'
until curl -sf http://127.0.0.1:30000/v1/models >/dev/null; do sleep 10; done; echo READY
```
10–20 min on the first start. Progress: `tail -f /tmp/mineru_vlm_server.log`. If the window shows "SERVER EXITED":
```bash
grep ERROR /tmp/mineru_vlm_server.log | tail -15
```

## Step 12 — Smoke test (all four parsers, one 4-page PDF)
Second pane: `watch -n 2 nvidia-smi`.
```bash
cd /workspace/cap-slice
tools/gpu/session.sh smoke 2>&1 | tee /workspace/smoke.log
grep -c "Fallback mode" /workspace/smoke.log
```
Expect:
- four lines starting with `ok`; the MinerU one fast (server already up)
- the PyMuPDF4LLM line ends in `True`
- Docling around 20–30 s (pod 1: 20 s) — much slower (60 s+) means a bad pod
- GPU busy during Docling and PyMuPDF4LLM
- `Fallback mode` count 0

## Step 13 — Rehearsal (all four parsers on 5 golden docs, 240 pages, ~20 min)
```bash
GPU_PRICE=0.99 tools/gpu/session.sh rehearse 2>&1 | tee /workspace/rehearse.log
grep -E "Error|Traceback" /workspace/rehearse.log | head
cat parsed_rehearsal/review/gpu/COMPARISON.md
```
Expect in the table:
- every parser `5 / 0` documents, 240 pages
- GPU rows filled for MinerU, Docling, PyMuPDF4LLM
- "Low-text pages recovered" above 0 for all but baseline
- tokens per page and Voyage $ filled

Then one scanned page (E2E FY2022-23, page 130) from each parser:
```bash
for p in baseline pymupdf4llm docling mineru; do echo "=== $p"; python3 -c "
import json; d=json.load(open('parsed_rehearsal/$p/E2E/annual_reports/2023-09-21_FY2022-23/pages.json'))
print(next((t for n,t in d['pages'] if n==130), '<no page 130>')[:600])"; done
```
Expect `<no page 130>` for baseline; financial-statement numbers with years for the other three.

## Step 14 — Benchmark (200 fixed pages, nothing else running)
```bash
GPU_PRICE=0.99 tools/gpu/session.sh bench 2>&1 | tee /workspace/bench.log
```
From the report, pick:
- Docling processes: the faster of `docling_b4` (1) and `docling_b4_xN` (N)
- PyMuPDF4LLM processes: the faster of `pymupdf4llm` (1) and `pymupdf4llm_xN` (N)
- MinerU workers: 8; 16 if its GPU utilisation is under 70 %

Full run after this: `docs/gpu-run.md` step 5.
