# OCR VLM benchmark: PaddleOCR-VL-1.6 vs GLM-OCR vs Unlimited-OCR

Measures **accuracy and throughput in the same run** on a 780-page set drawn from our
BSE/NSE filings, on **one RTX 5090 pod**. The three models run one after another; each is
benchmarked as its **full official pipeline**:

| Model | Pipeline | Settings |
|---|---|---|
| PaddleOCR-VL-1.6 (0.9B) | PP-DocLayout + VLM via vLLM | `pipeline_version="v1.6"`, chart recognition and OCR in image blocks **on** |
| GLM-OCR (0.9B) | PP-DocLayoutV3 + VLM via vLLM (official SDK) | MTP speculative decoding, 1 token (official recipe); `GLM_MTP=3` to compare |
| Unlimited-OCR (3B) | End-to-end via vLLM + crop pass | Pass 1 `document parsing.`; pass 2 re-reads image regions with `Free OCR.` (charts) |

Unlimited-OCR is supported by stock vLLM since v0.27.0, so no special image or second pod is needed.

---

## 1. What goes where

**Local (this machine) → pod**, two folders:

| Local | Pod | What |
|---|---|---|
| `vlm_bench/` | `/workspace/ocr_bench/` | the benchmark code (this folder, `vlm_bench/` in the cap-slice repo) |
| `data/parsing_eval/sets/bench/` | `/workspace/data/bench_set/` | the 780-page set (268 MB): `pdfs/`, `manifest.jsonl`, `warmup.jsonl`, `gold/`, `questions.json`, `page_checks.json` |

Nothing else is needed: models download from HuggingFace / Paddle on first use.

**Pod → local**, after the runs:

| Pod | Local | What |
|---|---|---|
| `/workspace/results/` | `data/parsing_eval/results/bench/` | per-run summaries, per-page markdown, scores |
| `/workspace/logs/` | `data/parsing_eval/results/bench/logs/` | server logs (for debugging) |

**Pod layout** (`/workspace` is the 80 GB persistent volume; survives stop/start):

```
/workspace/
├── ocr_bench/          code (synced from here)
├── data/bench_set/     benchmark set (synced from here)
├── data/pages/         rendered PNGs + manifest.jsonl / warmup.jsonl / smoke.jsonl (made on the pod)
├── venvs/              paddle_server, paddle_client, vllm_server, glm_client, tools
├── hf_cache/ paddlex_cache/ uv_cache/     model weights and package cache
├── results/<model>/<run>/                 outputs (see section 3)
└── logs/               server logs
```

## 2. Execution pipeline

```
 local                         pod (RTX 5090)
 ─────                         ──────────────
 rsync code + bench set ──►  setup_pod.sh        (once: 5 venvs, ~20-40 min)
                             prep_pages.py       (PDF pages -> 200-DPI PNGs, ~1 min)
                             for model in paddle, glm, unlimited:
                                 serve.sh <model>      start its vLLM server (1st time downloads weights)
                                 smoke test (5 pages)  READ the output before spending GPU time
                                 sweep.sh <model>      3 full runs of 780 pages at 3 concurrency levels
                                 pkill server          free the GPU for the next model
                             summarize.py        throughput table
                             score.py            accuracy table
 rsync results back    ◄──
 score.py locally (optional), review disagreements
 stop / terminate pod
```

Estimated GPU time: setup ~30 min + per model (~10 min server start/smoke + 3 runs × 5-15 min)
≈ **2.5-3.5 h total, ~$3-4 at $0.99/h**.

## 3. Outputs

Per run, `results/<model>/<run>/`:

| File | Content |
|---|---|
| `summary.json` | pages/s, pages/h, GPU-h per 1M pages, latency p50/p95, tokens per page, GPU/CPU utilisation, vLLM queue stats, failures |
| `md/<page_id>.md` | the model's markdown for each page (what gets scored) |
| `md/<page_id>.raw.md`, `.blocks.json` | Unlimited-OCR only: raw output and parsed blocks (category, box, text) |
| `pages.jsonl` | per page/request: latency, tokens, errors, crops |
| `gpu.csv`, `server.jsonl` | nvidia-smi and vLLM metric samples during the run |

`<model>` = `paddleocr-vl-1.6`, `glm-ocr`, `unlimited-ocr`; `<run>` = `c64`, `w8`, `c64_k1`, `smoke`, ...
`page_id` = `<doc_id>_p<NNN>` (1-based page of the original filing).

Across runs, in `results/`:

| File | Made by | Content |
|---|---|---|
| `comparison.csv` | `summarize.py` | throughput of every run + cost projection |
| `score_summary.csv` | `score.py` | per model: number recall/precision and word F1 on born-digital control pages, questions supported (easy/medium/hard), agreement on scans/charts |
| `score_pages.csv` | `score.py` | per model per page |
| `score_questions.csv` | `score.py` | per model per question: found / missing strings |
| `disagreements.csv` | `score.py` | scans/charts where models disagree most, with the numbers only one model produced |

---

## 4. Runbook (run in order)

Commands marked **[local]** run on this machine, **[pod]** inside the pod over SSH.

### Step 0 [local] — connection details

Get the pod's public IP and SSH port: RunPod console → pod → Connect → "SSH over exposed TCP"
(or ask Claude: it reads them from the RunPod API). Then:

```bash
export POD_IP=<ip>        # RunPod console -> Connect -> "SSH over exposed TCP"
export POD_PORT=<port>    # changes on every pod (re)start
export SSH="ssh -i $HOME/.ssh/run_pod -p $POD_PORT"
cd /home/nagasirishachava/personal/cap_slice_github/cap-slice
$SSH root@$POD_IP 'nvidia-smi --query-gpu=name,memory.total --format=csv && nvidia-smi | grep -oE "CUDA (UMD )?Version: [0-9.]+"'
```

Expect `NVIDIA GeForce RTX 5090, 32607 MiB` and **CUDA Version ≥ 12.9** (PaddlePaddle's Blackwell build needs it).

### Step 1 [local] — copy code and benchmark set to the pod

```bash
$SSH root@$POD_IP 'apt-get update -qq && apt-get install -y -qq rsync tmux > /dev/null; mkdir -p /workspace/data'
rsync -az --no-owner --no-group --info=progress2 -e "$SSH" vlm_bench/ root@$POD_IP:/workspace/ocr_bench/
rsync -az --no-owner --no-group --info=progress2 -e "$SSH" data/parsing_eval/sets/bench/ root@$POD_IP:/workspace/data/bench_set/
```

`/workspace` is RunPod network storage (MooseFS) where even root cannot `chown`, hence
`--no-owner --no-group`; without them rsync prints `chown ... Operation not permitted`
(harmless, but exits with code 23).

### Step 2 [local → pod] — open a shell inside tmux

Runs take hours; tmux keeps them alive if SSH drops.

```bash
$SSH root@$POD_IP
```
```bash
# [pod]
tmux new -s bench          # later: Ctrl-b d to detach, `tmux attach -t bench` to come back
chmod +x /workspace/ocr_bench/*.sh
```

### Step 3 [pod] — one-time setup (~20-40 min)

```bash
cd /workspace/ocr_bench && bash setup_pod.sh 2>&1 | tee /workspace/logs/setup.log
```

The last lines must show: `paddle ... cuda: True` and `PaddlePaddle works well on 1 GPU`,
`vllm 0.30.x | ... gpu NVIDIA GeForce RTX 5090 (12, 0)`, `glmocr ok`, `tools ok`.
After a pod **restart**, re-run it: the venvs are skipped, only `rsync/tmux` are reinstalled.

### Step 4 [pod] — render pages and make the smoke set

```bash
source /workspace/ocr_bench/env.sh
source $WS/venvs/tools/bin/activate
python prep_pages.py --from-manifest $WS/data/bench_set/manifest.jsonl --out-dir $P --dpi 200
python prep_pages.py --from-manifest $WS/data/bench_set/warmup.jsonl   --out-dir $P --dpi 200
# smoke set: one page of each hard type (scan, old-OCR scan, chart, chart, transcript layout)
grep -E '"page_id": "(719_p002|344_p003|534_p027|220_p020|712_p007)"' $P/manifest.jsonl > $P/smoke.jsonl
wc -l $P/manifest.jsonl $P/warmup.jsonl $P/smoke.jsonl     # expect 780, 16, 5
deactivate
```

### Step 5 [pod] — PaddleOCR-VL-1.6

```bash
source /workspace/ocr_bench/env.sh
./serve.sh paddle                                  # waits until the server answers (1st start downloads the model)

# smoke test: 5 hard pages
source $WS/venvs/paddle_client/bin/activate
python run_paddle.py --manifest $P/smoke.jsonl --warmup 2 --run-name smoke --results "$RESULTS"
ls -la $RESULTS/paddleocr-vl-1.6/smoke/md/
cat $RESULTS/paddleocr-vl-1.6/smoke/md/534_p027.md   # chart page: values should appear as a table
cat $RESULTS/paddleocr-vl-1.6/smoke/md/719_p002.md   # scanned P&L: decimals intact (146.49, 55.43)
deactivate
```

If the markdown looks right, run the mini-sweep (3 full runs), then stop the server:

```bash
LEVELS="32 64 128" ./sweep.sh paddle 2>&1 | tee $WS/logs/sweep_paddle.log
pkill -f "vllm|genai_server"; sleep 15; nvidia-smi --query-gpu=memory.used --format=csv   # should be near 0
```

### Step 6 [pod] — GLM-OCR

```bash
source /workspace/ocr_bench/env.sh
./serve.sh glm

source $WS/venvs/glm_client/bin/activate
python run_glm.py --manifest $P/smoke.jsonl --warmup 2 --workers 2 --run-name smoke --results "$RESULTS"
ls -la $RESULTS/glm-ocr/smoke/md/                    # files must not be empty (0 bytes)
cat $RESULTS/glm-ocr/smoke/md/534_p027.md            # does GLM transcribe the chart or skip it?
cat $RESULTS/glm-ocr/smoke/md/344_p003.md
deactivate

LEVELS="4 8 16" ./sweep.sh glm 2>&1 | tee $WS/logs/sweep_glm.log
pkill -f vllm; sleep 15; nvidia-smi --query-gpu=memory.used --format=csv
```

### Step 7 [pod] — Unlimited-OCR

```bash
source /workspace/ocr_bench/env.sh
./serve.sh unlimited

source $WS/venvs/tools/bin/activate
python run_unlimited.py --manifest $P/smoke.jsonl --warmup 2 --concurrency 4 --run-name smoke --results "$RESULTS"
grep -E '"(crops|empty_outputs|unparsed_outputs|truncated)"' $RESULTS/unlimited-ocr/smoke/summary.json
cat $RESULTS/unlimited-ocr/smoke/md/534_p027.md      # chart text should appear under "<!-- image text -->"
head -c 1500 $RESULTS/unlimited-ocr/smoke/md/534_p027.raw.md
deactivate
```

Expect `empty_outputs: 0`, `unparsed_outputs: 0`, `truncated: 0`, `crops` > 0. If
`unparsed_outputs` > 0, send Claude a `*.raw.md` (the tag format differs; one regex to adjust).

```bash
LEVELS="32 64 128" MULTI=0 ./sweep.sh unlimited 2>&1 | tee $WS/logs/sweep_unlimited.log
pkill -f vllm; sleep 15
```

### Step 8 [pod] — saturation check, then results tables

For each model the three runs should show throughput levelling off. Saturated = <10% gain
from the previous level, `waiting_mean` > 0, or `gpu_util_mean` > ~85%:

```bash
source /workspace/ocr_bench/env.sh && source $WS/venvs/tools/bin/activate
grep -H -E '"(pages_per_s|waiting_mean|gpu_util_mean|failures)"' $RESULTS/*/*/summary.json
```

If a model's top level still gained >10%, run one more level for it (e.g.
`./serve.sh paddle && LEVELS="256" ./sweep.sh paddle`). Then:

```bash
python summarize.py --results $RESULTS --gpu-hourly 0.99 --pages 1700000
python score.py --results $RESULTS --bench $WS/data/bench_set
```

### Step 9 [local] — copy results back

```bash
cd /home/nagasirishachava/personal/cap_slice_github/cap-slice
mkdir -p data/parsing_eval/results/bench
rsync -az --no-owner --no-group --info=progress2 -e "$SSH" root@$POD_IP:/workspace/results/ data/parsing_eval/results/bench/
rsync -az --no-owner --no-group -e "$SSH" root@$POD_IP:/workspace/logs/ data/parsing_eval/results/bench/logs/
# optional: rescore locally (stdlib only)
python3 vlm_bench/score.py --results data/parsing_eval/results/bench --bench data/parsing_eval/sets/bench
```

Then tell Claude the results are in `data/parsing_eval/results/bench/`: it reads `score_summary.csv`,
`comparison.csv`, `disagreements.csv` and the markdown, and checks the 15 pages in
`page_checks.json` by eye.

### Step 10 — stop or terminate the pod

- **Stop** (keep `/workspace` for another session; GPU billing stops, small storage fee continues):
  RunPod console → Stop, or ask Claude. Resume later → Step 0, then Step 3 (only reinstalls rsync/tmux).
- **Terminate** when finished (deletes `/workspace` too, so do Step 9 first).

---

## Full-corpus run (PaddleOCR-VL-1.6, full vision)

Numbers: `notes.md` §5 (Paddle was chosen there; superseded by MinerU in §8). Every page of all 369 selected PDFs (15,683 pages) with PaddleOCR-VL-1.6
served by **vLLM 0.30** (`serve.sh paddle030`, ~2× faster than PaddleOCR's pinned vLLM 0.10.2, same output),
**2 clients × concurrency 64** (~2.85 pages/s on typical pages → ~1.5 h on one RTX 5090).

Build the set locally first (≈40 s):
`python parsing_eval/sets/build_full_set.py`

**F1 [local] — copy code and the full set (1.5 GB)**
```bash
cd /home/nagasirishachava/personal/cap_slice_github/cap-slice
rsync -az --no-owner --no-group --info=progress2 -e "$SSH" vlm_bench/ root@$POD_IP:/workspace/ocr_bench/
rsync -az --no-owner --no-group --info=progress2 -e "$SSH" data/parsing_eval/sets/full/ root@$POD_IP:/workspace/data/full_set/
```

**F2 [pod] — render all pages (~11 GB of PNGs, a few minutes)**
```bash
source /workspace/ocr_bench/env.sh && source $WS/venvs/tools/bin/activate
FP=/workspace/data/full_pages
python prep_pages.py --from-manifest $WS/data/full_set/manifest.jsonl --out-dir $FP --dpi 200 --workers 24
python prep_pages.py --from-manifest $WS/data/full_set/warmup.jsonl   --out-dir $FP --dpi 200 --workers 8
wc -l $FP/manifest.jsonl $FP/warmup.jsonl        # expect 15683, 16
deactivate
```

**F3 [pod] — start the server and run (inside tmux)**
```bash
source /workspace/ocr_bench/env.sh
pkill -f "vllm|genai_server"; sleep 15
./serve.sh paddle030
source $WS/venvs/paddle_client/bin/activate
FP=/workspace/data/full_pages
PYTHONUNBUFFERED=1 python run_paddle.py --manifest $FP/manifest.jsonl --warmup-manifest $FP/warmup.jsonl \
  --clients 2 --concurrency 64 --skip-existing --results /workspace/results_full --run-name full \
  2>&1 | tee -a $WS/logs/full_run.log
```
Progress: `ls /workspace/results_full/paddleocr-vl-1.6/full/md | grep -c json$` (out of 15683).
If anything stops it, **re-run the same command**: `--skip-existing` resumes with the remaining pages.

**F4 [local] — copy outputs back while it runs (pod has no volume)**
```bash
rsync -az --no-owner --no-group -e "$SSH" root@$POD_IP:/workspace/results_full/ data/parsing_eval/results/full/
```

**F5 [pod] — find and re-run repetition loops, then merge clean re-runs**
```bash
source /workspace/ocr_bench/env.sh && FP=/workspace/data/full_pages
RUN=/workspace/results_full/paddleocr-vl-1.6/full
$WS/venvs/tools/bin/python detect_loops.py --run $RUN --manifest $FP/manifest.jsonl
source $WS/venvs/paddle_client/bin/activate
PYTHONUNBUFFERED=1 python run_paddle.py --manifest $RUN/loops.jsonl --warmup 2 --clients 1 \
  --repetition-penalty 1.05 --results /workspace/results_full --run-name full_rerun
deactivate
$WS/venvs/tools/bin/python detect_loops.py --run $RUN --manifest $FP/manifest.jsonl \
  --merge-from /workspace/results_full/paddleocr-vl-1.6/full_rerun
```
~1% of pages get flagged; about half are legitimate repetitive tables (kept: their re-run is still
"repetitive", so the original stays). Regional-language newspaper pages (Kannada) produce garbage in every
model — exclude non-English pages at parsing.

**F6 [pod] — score against the text layer, then copy everything back (F4)**
```bash
$WS/venvs/tools/bin/python score.py --results /workspace/results_full --bench $WS/data/full_set \
  --runs paddleocr-vl-1.6=full
```

## Full-corpus run 2: MinerU 4 (MinerU2.5-Pro), for comparison with Paddle

Same 369 PDFs / 15,683 pages, run after Paddle (one server on the GPU at a time). Settings match our
full-vision decision: `--tier advanced` (the 1.2B VLM does layout and reads every block) and
`--parse-mode ocr` (never take text from the PDF's text layer; MinerU's default `auto` keeps it for
PDFs it judges digital, which brings back the wrong OCR layers of our scans). MinerU parses whole
PDFs; `run_mineru.py` splits the output into the same per-page files as Paddle
(`md/<page_id>.md` + `.json`; whole-document JSON in `docs/<doc_id>.json`), so `score.py` and
`detect_loops.py` work unchanged.

**M1 [pod] — environment (~5 min; pinned set from main's `docker/requirements-mineru-cu130.txt`)**
The `mineru` block of `setup_pod.sh`: venv from `requirements-mineru-cu130.txt` via the PyTorch cu130
index (the image's uv 0.9 has no `--torch-backend cu130`), then
`mineru-kit models download --tier standard --vlm-engine vllm` (small models + MinerU2.5-Pro, 3.1 GB,
into `MINERU_HOME=/workspace/mineru_home`; "standard" is the download set advanced also uses).

**M2 [pod] — server, smoke on the 3 smallest PDFs, full run (inside tmux)**
```bash
source /workspace/ocr_bench/env.sh
pkill -f "vllm serve"; sleep 20
./serve.sh mineru                         # mineru-kit vlm-server on :30000, 0.5 of VRAM
source $WS/venvs/mineru/bin/activate
export MINERU_MALLOC_TRIM=1 MALLOC_ARENA_MAX=2   # give freed RAM back after each page window (62 GB pod limit)
FP=/workspace/data/full_pages
export MINERU_PROCESSING_WINDOW_SIZE=32          # 32-page windows: lower RAM peak per process
PYTHONUNBUFFERED=1 python run_mineru.py --manifest $FP/manifest.jsonl --procs 4 --workers 1 \
  --skip-existing --results /workspace/results_full --run-name full 2>&1 | tee -a $WS/logs/mineru_full.log
```
`run_mineru_full.sh` does all of M2 (waits for Paddle, smoke first). `--procs` = parser processes (each
loads its own MinerU models; PDFs split so each gets ~the same pages); `--workers` = PDFs in
flight (threads sharing one set of layout models); each PDF sends up to 100 VLM requests at once.
Re-run the same command to resume: `--skip-existing` skips PDFs whose pages are all written.
Watch RAM: `cat /sys/fs/cgroup/memory.current` (limit `memory.max`, 62 GB); lower `--procs` if it
nears the limit.

**M3 [pod] — score both runs on the same pages**
```bash
cp $WS/data/bench_set/questions.json $WS/data/full_set/   # the 25 questions' pages are in the full set
$WS/venvs/tools/bin/python score.py --results /workspace/results_full --bench $WS/data/full_set \
  --runs paddleocr-vl-1.6=full mineru2.5-pro=full
$WS/venvs/tools/bin/python detect_loops.py --run /workspace/results_full/mineru2.5-pro/full \
  --manifest $WS/data/full_pages/manifest.jsonl    # loop counts per model (no re-run needed to compare)
```

## 5. Reading the results

Throughput (`comparison.csv`):
- **pages_per_s** is the headline; use each model's saturated run.
- Low **gpu_util_mean** with high **cpu_mean** → CPU-bound (layout stage), not GPU.
- **running_mean** well below the concurrency → the client isn't feeding the server.
- **gen_tokens_per_page** explains speed differences (dense tables = many output tokens).
- **vlm_requests_per_page**: region calls for Paddle/GLM; page + crop calls for Unlimited.
- The best concurrency is machine-specific: re-tune the chosen model on the production GPU.

Accuracy (`score_summary.csv`):
- **num_recall / num_precision / word_f1** on 230 born-digital control pages vs the PDF text
  layer. Low precision = numbers not on the page (invented or mangled).
- **questions_easy/medium/hard**: the evidence pages contain every string the answer needs.
  Necessary, not sufficient: it does not prove the value is in the right row/column; that is
  checked by eye with `page_checks.json`.
- **agreement_noncontrol** and `disagreements.csv`: scans and charts have no ground truth;
  review the top ~30 disagreement pages by eye.

## 6. If something goes wrong

| Symptom | Likely cause / fix |
|---|---|
| `serve.sh` times out | `tail -50 /workspace/logs/<model>_server.log`. Out of memory → `GPU_UTIL=0.5 ./serve.sh <model>` |
| Paddle: `no kernel image is available` / sm_120 errors | wrong PaddlePaddle build; must be `paddlepaddle-gpu==3.2.1` from the `cu129` index and host CUDA ≥ 12.9 |
| `paddleocr install_genai_server_deps vllm` builds flash-attn for a long time | expected on Blackwell if no prebuilt wheel; needs `nvcc` (setup prints it) |
| Paddle models download to `~/.paddlex` | `source env.sh` before running (sets `PADDLE_PDX_CACHE_HOME`) |
| GLM `.md` files empty | SDK result attribute changed: check `run_glm.py::_markdown`, look at `md/_scratch` |
| Unlimited `unparsed_outputs` > 0 | send a `*.raw.md` to Claude; adjust `BLOCK_START` in `run_unlimited.py` |
| Unlimited `crops` = 0 or `n_crops_with_text` = 0 on chart pages | image blocks not detected, or crop prompt; try `document parsing.` as `CROP_PROMPT` |
| SSH dropped mid-run | `ssh` back in, `tmux attach -t bench` |

## 7. Files

| File | Purpose |
|---|---|
| `setup_pod.sh` | one-time setup: 5 venvs, caches on `/workspace`, GPU/import checks |
| `env.sh` | `source` in every new pod shell: cache paths, `$P`, `$RESULTS`, cd |
| `serve.sh` | start one model server (`paddle` / `paddle030` / `glm` / `unlimited` / `mineru`) |
| `prep_pages.py` | render the benchmark manifest (or whole PDFs) to PNG at fixed DPI |
| `run_paddle.py`, `run_glm.py`, `run_unlimited.py` | one benchmark run each: markdown + timings |
| `run_mineru.py`, `requirements-mineru-cu130.txt` | MinerU 4 (MinerU2.5-Pro) over whole PDFs, split into per-page outputs; its pinned environment |
| `sweep.sh` | runs one model at several concurrency levels (`LEVELS=...`, `MULTI=0`) |
| `summarize.py` | throughput table + cost projection |
| `score.py` | accuracy: control-page gold, questions, cross-model agreement |
| `common.py` | GPU/CPU/vLLM samplers, summary writer |
