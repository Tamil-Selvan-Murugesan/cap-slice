# Benchmark run notes

Exact numbers and observations from each run, in the order they happened. Times are UTC.

**Local copies (copied 2026-10-04, file counts verified against the pod):**
- `data/parsing_eval/results/bench/` — 780-page bench runs of all three models (+ invalid GLM w8/w16), score and
  comparison CSVs (all three models), `logs/` (server, sweep, CPU-throttle logs), `early_smoke_runs/`.
- `data/parsing_eval/results/repr/` — 600-page representative-sample Paddle runs (vLLM 0.10.2 n1–n4,
  vLLM 0.30 v030_n1–n3), markdown + per-page JSON.
- Full-corpus runs (Paddle + MinerU, 15,683 pages each): `data/parsing_eval/results/full/` (sections 6–7); pod logs in `data/parsing_eval/results/pod_logs/`. Backed up to R2 `sirisha/data/parsing_eval/`.

## Machine

| | |
|---|---|
| Pod | `5090-local120-verified-20261004` (`0hgcwa3psucznl`), EU-CZ-1, Secure Cloud, $0.99/h |
| SSH | `ssh -i ~/.ssh/run_pod -p <port> root@<pod-ip>` |
| GPU | 1× RTX 5090 32 GB (Blackwell, sm_120), driver 610.57.04, host CUDA 13.3 |
| CPU / RAM | 32 vCPU / 62 GB |
| Disk | 120 GB container disk, **no volume**: everything is lost if the pod stops. Copy results back first |
| Image | `runpod/pytorch:1.0.2-cu1281-torch280-ubuntu2404` |
| Bench set | 780 pages from 223 filings at 200 DPI + 16 separate warm-up pages (see README §1) |

## Setup log

- 2026-10-03: first pod `dh3dps2bgin07q` (EU-CZ-1, 80 GB pod volume). Network from the pod measured:
  HuggingFace with `hf download` (xet, parallel) ~260 MB/s (11.2 GB of models in 43 s); single-stream
  HF 12 MB/s; PyPI 116 MB/s; PaddlePaddle wheel from Baidu CDN 9.6 MB/s.
- `paddleocr install_genai_server_deps vllm` failed building flash-attn: its `setup.py` imports torch,
  which pip's isolated build env lacks (`No module named 'torch'`). Fix: `flash-attn==2.8.3
  --no-build-isolation` (prebuilt cu12/torch2.8/cp312 wheel from GitHub), then re-run the helper.
- Installing PaddlePaddle with `--index-url <paddle index>` pulled every dependency through Paddle's
  slow index (>20 min). Fix: install the wheel by direct CDN URL; deps come from PyPI.
- 2026-10-04: the original pod could not restart (its host had no free GPU). A RunPod "migrate" pod
  never got a direct SSH port. Work continued on pod `0hgcwa3psucznl` above (container disk only).
- rsync to `/workspace` on the network-volume pod needed `--no-owner --no-group` (MooseFS refuses chown).
- 2026-10-04 08:32: first `./serve.sh glm` crashed after ~2.5 min of startup: `Failed to get device
  capability: SM 12.x requires CUDA >= 12.9` → `FlashInfer requires GPUs with sm75 or higher`. vLLM 0.30
  (torch 2.13+cu130) uses FlashInfer, which locates nvcc via CUDA_HOME / PATH / `/usr/local/cuda` and found
  the image's CUDA **12.8** toolkit (sm_120 needs ≥ 12.9). serve.sh kept polling for 15 min, which looked
  like slow loading. Fix: `serve.sh` points CUDA_HOME at the pip-installed nvcc 13.4 inside the vllm_server
  venv (`site-packages/nvidia/cu13`) for GLM and Unlimited. vLLM 0.30 startup also captures ~150 CUDA graphs (~2 min).
- 08:46: second attempt got further: FlashInfer JIT-compiled its **sampling** kernel with nvcc 13.4 and failed
  (`CUDA compiler and CUDA toolkit headers are incompatible`). Traceback: `sampler.py` → `flashinfer_sample`
  → `top_k_top_p_sampling_from_logits` → JIT build. Fix: `VLLM_USE_FLASHINFER_SAMPLER=0` in `serve.sh` (vLLM's
  PyTorch sampler; identical output at temperature 0, no compilation).
- A sync of `serve.sh` overwrote the pod's `chmod +x` (rsync -a copies local permissions) → "Permission denied".
  Fixed by `chmod +x` locally too.
- 09:40: `./serve.sh unlimited` crashed in the startup memory profile, in Unlimited-OCR's vision encoder
  (`deepseek_ocr.py` → `deepencoder.py:deepencoder_rel_pos_attention`): Triton kernel compile error
  `NameError: Cannot access global variable LOG2E from within @jit'ed function`. **vLLM 0.30 bug:** the kernel
  multiplies by the plain global `LOG2E` from `vllm.triton_utils`; vLLM 0.30 needs torch 2.13 → **Triton 3.7.1**,
  which only allows constexpr globals. Fix: inline `1.4426950408889634` at the two uses (lines 93, 124);
  backup `deepencoder.py.orig`; added as an idempotent step in `setup_pod.sh`.

## Versions

| Env | Packages |
|---|---|
| paddle_server | vllm 0.10.2 (pinned by PaddleOCR), torch 2.8.0, flash-attn 2.8.3 |
| paddle_client | paddleocr 3.7.0, paddlex 3.7.2, paddlepaddle-gpu 3.2.1 (cu129) |
| vllm_server (GLM, Unlimited) | vllm 0.30.0, torch 2.13.0+cu130, triton 3.7.1, flashinfer-python 0.6.18.post1, nvcc (pip) 13.4; glmocr 0.1.5 (glm_client) |

---

## 1. PaddleOCR-VL-1.6

Settings: `pipeline_version="v1.6"`, `use_chart_recognition=True`, `use_ocr_for_image_block=True`,
`use_queues=True`; server `gpu-memory-utilization 0.6`, `max-num-seqs 256`; layout model on the same GPU.

### Smoke test (5 hard pages)

`719_p002`, `344_p003`, `534_p027`, `220_p020`, `712_p007`: 5 pages in 12.09 s (0.413 pages/s),
0 failures, 43 server requests (8.6 per page), 8,729 generated tokens, GPU 44.8%, `running_mean` 3.2.
Throughput here is meaningless: 5 pages cannot fill the server.

| Page | What it tests | Result |
|---|---|---|
| `719_p002` | scanned P&L, no text layer | ✅ every value correct in all 4 columns (146.49, 55.43, 327.14, −2902.18, empty Purchase cell). Two-level header kept (Half Year Ended / Year Ended). Notes correct (1,95,352). Silently "fixed" the filing's typo "Dirctors". Date/place/signatory not seen in the pasted output |
| `344_p003` | scan with wrong embedded OCR layer | ✅ every value correct (5,81,695; (12,917); 5,06,070; OCI row). Ignored the bad text layer. 3-level header kept. Signatory (Atul.B.Lall) kept. Note 5 lost its number; stray "## Notes: ___" |
| `534_p027` | 3 charts, values only in images | ✅ all 20 values correct, each chart → its own table with the right fiscal year. ⚠️ unit read as "£ Crore" instead of ₹ Crore |
| `220_p020` | 2 bar charts | ✅ all 10 values correct and on the right quarter. ⚠️ EBITDA table's value column mislabelled "EBITDA Margin"; margin bubbles (56.0%, 57.3%) missing from the table |
| `712_p007` | transcript, speaker/text layout | ✅ speaker attribution perfect (Ashutosh Shukla asks, Mukesh Vasani answers) |

**Smoke verdict:** no wrong numbers found. Errors are labels/units only (£ for ₹, one header label, one
note number). Strongest on exactly the pages where pymupdf4llm and Docling failed (scans, bad OCR layer, charts).

### Sweep (780 pages, separate 16-page warm-up)

| Run | Pages | Failures | Wall s | pages/s | pages/h | GPU-h per 1M pages | gen tok/s | gen tok/page | req/page | running mean / max | waiting mean | GPU util mean / p90 | GPU mem max | CPU mean / max | KV cache mean / max |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| c32 | 780 | 0 | 512.99 | **1.520** | 5,474 | 182.7 | 1,455.1 | 957.0 | 13.33 | 22.5 / 32 | 0.0 | 34.3% / 59% | 21.7 GB | 14.1% / 37.6% | 0.074 / 0.145 |
| c64 | 780 | 0 | 474.74 | **1.643** (+8%) | 5,915 | 169.1 | 1,585.7 | 965.1 | 13.33 | 47.1 / 64 | 0.0 | 34.2% / 62% | 22.2 GB | 14.5% / 37.1% | 0.135 / 0.228 |
| c128 | 780 | 0 | 470.25 | **1.659** (+1%) | 5,971 | 167.5 | 1,583.3 | 954.5 | 13.33 | 92.6 / 127 | 0.0 | 32.6% / 62% | 21.7 GB | 14.8% / 29.5% | 0.232 / 0.412 |

Totals per run: 10,399 server requests, ~750k generated tokens, 2.67M prompt tokens.
Sweep finished 08:27 UTC; no errors in `sweep_paddle.log`. Best run: **c128 (1.659 pages/s)**, but c64 is
within 1%, so c64 is the knee.

**Observations:**
- c32 → c64: 2× requests at the server (`running_mean` 22 → 47) but only +8% pages/s, and GPU
  utilisation unchanged at 34%. `waiting_mean` 0 throughout: the server never queues.
- c64 → c128: `running_mean` doubled again (47 → 93) for +1% pages/s; GPU 32.6%. Confirmed plateau.
- So the GPU is not the bottleneck. The limit is the **client pipeline** (single process: layout
  detection → region requests → page assembly). By the <10% rule, Paddle is saturated at ~1.65 pages/s
  in this setup; more concurrency only fills the KV cache (max 41% at c128) without more output.
- GPU has large headroom (66% idle, KV cache ≤ 23%). Running 2–3 client processes on split manifests
  would likely raise throughput 2–3× on the same GPU; a production-tuning step, not needed for the model choice.
- Cost at 1.6 pages/s: ~5,900 pages/h → ~290 GPU-h (~$290 at $0.99/h) for a ~1.7M-page backfill, as configured.

### Accuracy (score.py, run c128)

| Control pages | Unreliable gold excluded | num_recall | num_recall tables / text | num_precision | word_f1 | Questions easy / medium / hard | Total |
|---|---|---|---|---|---|---|---|
| 208 | 21 | **0.852** | 0.916 / 0.734 | **0.990** | 0.938 | 6/6 · 10/10 · 9/9 | **25/25** |

Before excluding unreliable gold: num_recall 0.795, num_precision 0.909, word_f1 0.859 (penalised for reading
*better* than the text layer). Agreement with other models: pending (needs GLM / Unlimited).

**Finding: some born-digital text layers are not usable as ground truth (21 of 229 control pages).**
- Shifted-glyph fonts: Reliance AR 2018 (`9_p243`–`p246`, `9_p440`) stores "ANNEXURE IV A" as `$11(;85(,9$`,
  "Policy for selection" as `3ROLF\IRUVHOHFWLRQ`. The page renders fine; only the text layer is wrong.
- Symbol soup: `483_p002`–`p004` (Kaynes credit rating), `353_p003`; mojibake fonts: `514_p001` (Adisoft).
- Kannada newspaper result notices (Vijay Karnataka: `470_p002`, `479_p003`, `484_p003`), legacy-font text layer.
- Paddle read these pages correctly from the image.
- score.py now excludes them (`gold_reliable()`: vowel share of letters < 24% or letters < 30% of characters).
- **Pipeline impact:** pymupdf4llm (text layer) would output garbage for such pages → the router must also send
  pages whose text layer fails this check to the VLM, not only scans.

**Error pattern:** every remaining low-recall control page has precision 1.0 — numbers are omitted, not wrong.
Omitted numbers are mostly page furniture Paddle drops by design (running headers/footers, "Page 6 of 26",
page numbers), e.g. `712_p007` recall 0.33 with all dialogue present. Precision 0.99 = it almost never invents numbers.

---

## 2. GLM-OCR

Settings: official SDK `glmocr` 0.1.5 (PP-DocLayoutV3 layout + GLM-OCR via vLLM 0.30), MTP speculative
decoding with 1 token, `gpu-memory-utilization 0.6`, `VLLM_USE_FLASHINFER_SAMPLER=0` (see setup log).
**Chart/image fix (run_glm.py, default on):** the SDK's default config *skips* `chart` and `image` regions
(`label_task_mapping.skip`) and its formatter renders them as picture links, dropping any text
(`result_formatter.label_visualization_mapping.image`). Both changed: chart → table task ("Table
Recognition:"), image → text task. `--no-charts` restores SDK defaults. Needed for parity with Paddle
(`use_chart_recognition`) and Unlimited (crop pass).

### Smoke test (5 hard pages)

| Run | Wall s | pages/s | req/page | gen tok/page | Failures / empty |
|---|---|---|---|---|---|
| smoke (SDK default: charts skipped) | 6.84 | 0.731 | 6.2 | 1,278 | 0 / 0 |
| smoke_charts (charts → table) | 7.68 | 0.663 | 7.2 | 1,420 | 0 / 0 |

Per-page latency (smoke_charts): 220_p020 0.46 s, 534_p027 0.69 s, 712_p007 0.50 s, 344_p003 4.47 s, 719_p002 6.02 s.

| Page | Result |
|---|---|
| `719_p002` | ✅ all checked values correct; two-level header kept (`<thead>` with Half Year / Year Ended) |
| `344_p003` | ✅ all checked values correct (5,81,695; (12,917)); 3-level header kept; ignores the bad OCR layer |
| `712_p007` | ✅ speaker attribution perfect; minor lost spaces ("$70 to$ 80", "business.So") |
| `534_p027` | SDK default: ❌ only image links. With fix: ✅ all 20 values present, but **layout copy**, not value→year pairs: values row + years row; margins crammed into one cell ("16.1% 17.3% 19.4%"). ⚠️ unit "है Crore" (Hindi char) instead of ₹ |
| `220_p020` | SDK default: ❌ only image links. With fix: values present, but EBITDA row mixes margin bubbles into the values (56.0%, 17,301, …, 57.3%, 19,590 over 5 years) → positional year mapping is **wrong** |

**Smoke verdict:** scans/tables/transcripts as good as Paddle. Charts: values are extracted but not reliably
attached to their period, unlike Paddle's chart-to-table output.

Smoke outputs: the first smoke run landed in `/workspace/ocr_bench/results/` (no `--results` flag);
`smoke_charts` is in `/workspace/results/glm-ocr/`.

### Sweep (780 pages, `--workers` = parallel SDK pipelines, each with its own layout model on the GPU)

| Run | Valid | Empty pages | Wall s | pages/s | pages/h | GPU-h per 1M | gen tok/s | gen tok/page | req/page | lat p50 / p95 s | running mean / max | waiting mean / max | GPU util mean / p90 | GPU mem max | CPU mean / max | KV cache mean / max |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| w4 | ✅ | 1 | 672.32 | **1.160** | 4,177 | 239.4 | 3,026.4 | 2,608.6 | 11.48 | 1.26 / 9.01 | 16.1 / 77 | 1.15 / 38 | **92.4%** / 100% | 27.9 GB | 6.5% / 23% | 0.261 / **1.0** |
| w8 | ❌ OOM | **752** | 107.62 | (7.248) | | | 278.4 | 38.4 | 0.33 | | 4.3 / 25 | | 28.0% | 32.1 GB | 16.9% / 29% | 0.039 / 0.095 |
| w16 | ❌ OOM | **687** | 230.36 | (3.386) | | | 2,096.0 | 619.0 | 1.58 | | 19.9 / 71 | | 55.3% | 32.1 GB | 17.3% / 30.9% | 0.276 / 0.994 |

Totals w4: 8,955 server requests, 2.03M generated tokens, 2.09M prompt tokens.

**Observations:**
- **w8 / w16 are invalid.** GPU memory hit 32 GB: the vLLM server holds ~20.2 GB and every worker loads its own
  PP-DocLayoutV3 on the GPU. From 8 workers the layout step fails (`CUDA error: out of memory`,
  `Layout detection failed for pages [0], skipping batch`, 178 OOM tracebacks in `sweep_glm.log`). The SDK
  swallows the error and returns an **empty page** (failures stayed 0), which made the runs look fast.
  `run_glm.py` now prints an INVALID warning and `score.py` skips runs with >1% empty pages.
- **GLM is GPU-bound at w4:** GPU 92% busy, requests queueing (waiting max 38), KV cache briefly 100% full.
  So ~1.16 pages/s is its ceiling on one RTX 5090 at this memory split; more workers would not help.
  (Layout on CPU, `--layout-device cpu`, would free GPU memory but not GPU compute.)
- **Why GPU-bound when Paddle is not:** GLM writes 2.7× more tokens per page (2,609 vs 957: verbose
  `<table border="1">` HTML, keeps more text). It drives the GPU harder (3,026 vs ~1,585 gen tok/s) but needs
  more tokens per page. No repetition loops: the longest outputs are the dense Kannada newspaper pages
  (`470_p002` 45 KB, ~90% unique lines).
- Cost at 1.16 pages/s: ~4,200 pages/h → ~410 GPU-h (~$400) for ~1.7M pages.

### Accuracy (score.py, run w4) vs Paddle (c128)

| Model | Control pages | num_recall | num_precision | word_f1 | Questions | Agreement (scans/charts) |
|---|---|---|---|---|---|---|
| PaddleOCR-VL-1.6 | 208 | 0.852 | **0.990** | 0.938 | 25/25 | 0.860 |
| GLM-OCR | 208 | 0.843 | **0.972** | 0.935 | 25/25 | 0.860 |

- Both answer-support all 25 questions.
- **GLM's number precision is lower: 2.8% of its numbers on born-digital pages are not on the page, vs 1.0% for
  Paddle.** Mis-read / invented digits are the most damaging error type for financial data.
- Chart structure (smoke): Paddle builds value→period tables; GLM copies the chart layout, and margin labels
  can shift the period alignment (`220_p020`).
- To review: top of `disagreements.csv` (pages where Paddle and GLM numbers differ most).

## 3. Unlimited-OCR

Settings: `baidu/Unlimited-OCR` 3B via vLLM 0.30 (official recipe flags), `gpu-memory-utilization 0.9`,
`--moe-backend triton`, `VLLM_USE_FLASHINFER_SAMPLER=0`, deepencoder `LOG2E` patch (see setup log).
Pass 1 `<image>document parsing.` (window 128); pass 2 re-reads `image`/`chart` blocks with `<image>Free OCR.`.

**Caveat on speed:** `--moe-backend triton` replaces FlashInfer's Blackwell-tuned CUTLASS MoE kernels (which
fail to JIT-compile on this image). Same math in BF16, so accuracy is unaffected (only rounding-order noise),
but Unlimited's throughput here may be somewhat below its best possible on an RTX 5090.

### Smoke test (5 hard pages)

5 pages in 5.59 s (0.894 pages/s), 0 failures, 0 empty, **0 unparsed** (tag parser handles the real format:
`<|det|>category [x0, y0, x1, y1]<|/det|>text`), 0 truncated, 9 crops sent, 2.8 requests/page, 1,167 gen
tokens/page, latency p50 2.64 s / p95 5.11 s. Per page: 534_p027 3 crops (1 with text), 220_p020 2 (0),
344_p003 2 (0), 719_p002 2 (1).

| Page | Result |
|---|---|
| `344_p003` | ✅ all checked values correct (2,08,951; 5,81,695; (12,917); 5,06,070; (11); 69,061; 5.89); 3-level header kept |
| `719_p002` | ✅ all checked values correct (146.49, 55.43, 327.14, −2902.18, 25713.41, 11.58, 18.49). ⚠️ **header structure wrong**: "Half Year Ended" colspan 3 (should be 2) + a spurious duplicated "31st March, 2025 (Audited)" column → the FY26 full-year column falls under "Half Year" (the Q19 trap). Also auto-corrected "Dirctors" |
| `712_p007` | ✅ perfect speaker attribution; "$70 to $80" correct (GLM garbled it) |
| `220_p020` | ❌ chart detected (`chart [30, 244, 964, 688]`) but **no values** |
| `534_p027` | ❌ 3 charts detected, **no values**; one crop returned only the x-axis labels (FY23…FY26) |

**Charts are a model limitation, not a prompt issue.** Tested directly on the `220_p020` chart crop
(2494×667): `<image>Free OCR.`, `<image>document parsing.`, `<image>Parse the figure.` all return only
`<|det|>chart [0, 0, 999, 999]<|/det|>`; `<image>\nFree OCR.` / `<image>\nParse the figure.` return nothing.
The model labels charts and does not transcribe them (its model card's post-processing also drops them). The
crop pass still recovers ordinary text inside images (e.g. 719_p002).

Other formatting: slide titles are emitted as `header` blocks (→ `<!-- header: … -->` comments, text kept but
not `#` headings); logos give `[Non-Text]` blocks.

Sweep ran 10:08–~10:24 UTC (`LEVELS="32 64 128" MULTI=0`); 5 prompt-test requests overlapped its first seconds.
A harmless `RuntimeError: Event loop is closed` traceback (warm-up client closed after its event loop) was
fixed in `run_unlimited.py` mid-sweep (c64/c128 used the fix; no effect on requests).

### Sweep (780 pages, single-page mode, crop pass on)

| Run | Pages | Fail / empty / unparsed | **Truncated** | Crops | Wall s | pages/s | pages/h | GPU-h per 1M | gen tok/s | gen tok/page | req/page | lat p50 / p95 s | running mean / max | waiting mean / max | GPU util mean / p90 | GPU mem max | CPU mean / max | KV cache mean / max |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| c32 | 780 | 0 / 0 / 0 | 12 | 1,404 | 329.86 | **2.365** | 8,513 | 117.5 | 2,642.2 | 1,117.4 | 2.79 | 10.5 / 29.6 | 28.7 / 70 | 0.06 / 5 | 92.9% / 100% | 31.5 GB | 8.2% / 29.8% | 0.133 / 0.203 |
| c64 | 780 | 0 / 0 / 0 | 11 | 1,846 | 279.97 | **2.786** (+18%) | 10,029 | 99.7 | 3,055.3 | 1,096.7 | 3.36 | 17.4 / 46.5 | 49.6 / 179 | 0.24 / 15 | 91.3% / 100% | 32.0 GB | 6.4% / 20.3% | 0.214 / 0.363 |
| c128 | 780 | 0 / 0 / 0 | 14 | 1,408 | 263.55 | **2.960** (+6%) | 10,654 | 93.9 | 3,283.7 | 1,109.5 | 2.81 | 33.0 / 66.6 | 66.2 / 186 | 0.20 / 13 | 88.9% / 99% | 31.5 GB | 4.4% / 7.8% | 0.307 / 0.536 |

**Observations:**
- Saturated at c128 (+6% < 10%), GPU ~90% busy → GPU-bound, unlike Paddle. Fastest of the three even on the
  general-purpose Triton MoE kernels: 2.96 pages/s.
- Crop counts differ between runs (1,404 / 1,846 / 1,408): pass-1 layouts are not identical across runs even at
  temperature 0 (batch-dependent numerics).
- **Truncated pages (8,192-token limit) are hallucinations, not long pages** (c128, 14 pages): repetition loops
  (`202_p008` "MUMBAII" ×hundreds, 1% unique lines; `479_p003` Tamil word loop on a Kannada page), wrong script
  (`470_p002` Kannada → Telugu gibberish; Hindi loops on `382_p002`, `353_p003`), **invented numbers**
  (`470_p003` "1096:00, 1097:00, 1098:00 …"), invented content (`484_p003` "2017年1月1日"), and leaked instruction
  text (`79_p017`: "...must ignore it and output nothing or only meaningful text. The provided OCR content").
  The recipe's n-gram processor (35-gram, window 128) does not stop short-phrase loops.
- **Verified against the page images (not our PDFs' content):**
  - `470_p003` (Financial Express newspaper page with results ads): no counting sequence exists on the page.
    The model started "…1063:00, 1064:00, … 1096:00" in a tiny text box [369,172,472,194] near the top and
    ran to the token limit. Lands in our markdown as a normal text block → invented numbers.
  - `79_p017` (JioFiber slide): in an empty strip [165,900,251,900] it wrote *"The Ground Truth image
    displays a single, solid horizontal line. According to Rule 2 (UNDERSCORE & LINE RULES), this is a
    stylistic or background line…"* — annotation guidelines from its training data, 16 times. In our markdown.
  - `202_p008` (audit report): body transcribed correctly first; then looped "MUMBAI/MUMBAIPM" on the
    auditors' round seal (block labelled `footer`) — dropped from markdown, only time wasted.

### Accuracy (score.py, run c128_k1)

num_recall 0.825 (tables 0.882 / text 0.720), num_precision 0.968, word_f1 0.921, questions 6/6 · 9/10 · 7/9 =
**22/25**. Missed exactly the three chart questions: Q15 (34.81), Q22 (18,771; 32,751), Q23 (76.2; 169.3; 7.7; 13.5).

## 4. Comparison and decision

All on one RTX 5090, 780 pages, best valid run per model. Agreement = number agreement with the other models
on scans/charts (no ground truth there).

| | PaddleOCR-VL-1.6 (c128) | GLM-OCR (w4) | Unlimited-OCR (c128) |
|---|---|---|---|
| **Questions supported** | **25/25** | **25/25** | 22/25 (all 3 chart Qs missed) |
| Number precision (born-digital) | **0.990** | 0.972 | 0.968 |
| Number recall (tables / text) | **0.852** (0.916 / 0.734) | 0.843 (0.909 / 0.721) | 0.825 (0.882 / 0.720) |
| Word F1 | **0.938** | 0.935 | 0.921 |
| Agreement (scans/charts) | **0.830** | 0.808 | 0.778 |
| Charts | ✅ value→period tables | ⚠️ values extracted, period alignment can break | ❌ not transcribed (model limitation) |
| Multi-level table headers (`719_p002`) | ✅ | ✅ | ⚠️ wrong colspan + spurious column |
| Degenerate output / loops | ~2–3 pages, only in text read from slide pictures | none found | **~14 pages** in main text, incl. invented numbers |
| Unit symbol ₹ | ⚠️ "£" on a chart slide | ⚠️ "है" | ✅ "₹" |
| pages/s | 1.66 | 1.16 | **2.96** |
| Bottleneck | single client process (GPU ~33% busy) | GPU (92%) | GPU (~90%) |
| GPU-h / cost for ~1.7M pages @ $0.99/h | ~285 h / ~$282 | ~407 h / ~$403 | ~160 h / ~$158 |

**Recommendation: PaddleOCR-VL-1.6** for the routed (scanned / bad-text-layer / chart) pages.
- Most accurate on every measure, the only model that turns charts into correctly labelled tables, and the
  lowest rate of numbers that are not on the page (1%). For financial filings a wrong digit costs far more
  than GPU time.
- Its speed figure is a lower bound: the single client process is the bottleneck while the GPU is two-thirds
  idle. Running 2–3 client processes on split manifests should raise throughput substantially on the same GPU
  (not yet measured). Even as measured, the cost gap to Unlimited is ~$125 for the whole backfill.
- Mitigations to build in: normalise the currency symbol from the document's unit line; drop/flag repetitive
  text from picture regions (or turn off `use_ocr_for_image_block` and compare); keep page headers if recall
  of header numbers matters.

GLM-OCR is a close second on accuracy (fine as a fallback) but the slowest and needs SDK config changes for
charts. Unlimited-OCR is fastest but chart-blind and produced invented numbers and wrong-script text on ~2% of
pages — not suitable for financial data without a strong repetition/garbage filter.

### Header / footnote policy (found after the runs above)

The three pipelines treated non-body regions differently, which also affects recall:

| | header | footnote, aside_text | footer, page number |
|---|---|---|---|
| Paddle (runs above) | recognised, **hidden** from markdown (`markdown_ignore_labels` default) | recognised, **hidden** | recognised, hidden |
| GLM (runs above) | **never recognised** (`label_task_mapping.abandon`) | **never recognised** | never recognised |
| Unlimited (runs above) | kept as `<!-- header: … -->` | kept | dropped by `run_unlimited.py` |

Paddle's `markdown_ignore_labels` (number, footnote, header, header_image, footer, footer_image, aside_text)
is applied only in `result.py` when formatting markdown — the VLM still reads those regions. Headers carry
company, standalone/consolidated, period and units; footnotes can qualify numbers. Decision: **extract
everything with its label; decide what to drop at parsing/chunking.** Changes (synced, not yet re-run):
- `run_paddle.py`: markdown hides only `footer,footer_image,number` (`--md-ignore`), and saves Paddle's full
  per-page JSON (`md/<page_id>.json`, every block with label + box).
- `run_glm.py`: `header`, `footnote`, `aside_text` moved from `abandon` to the text task (`--drop-headers`
  restores the SDK default).
Re-run Paddle (one level) and GLM w4 to score all three under the same policy.

## 5. Full-vision decision: PaddleOCR-VL on a representative sample

Decision under test (2026-10-04): run PaddleOCR-VL on **all pages** (full vision) instead of hybrid. New
**representative set** (`parsing_eval/sets/build_repr_sample.py` → `repr_set.zip`, 107 MB): 600 pages
drawn uniformly at random from all 15,683 pages (185 filings; mix matches the corpus: text 69.7% vs 68.6%,
table_dense 14.2% vs 13.4%, charts 8.3% vs 7.8%, old-OCR scans 6.3% vs 7.9%, no-text scans 1.5% vs 2.3%;
annual reports 332 pages), 503 born-digital pages with text-layer gold, 16 separate warm-up pages.
Runs use the new header policy (headers/footnotes kept) and save Paddle's per-page JSON.
`run_paddle.py --clients N`: N worker processes (own pipeline + layout model each), round-robin split,
common start signal after warm-up; `--skip-existing` for resume.

### Parallel clients on PaddleOCR's pinned vLLM 0.10.2 — CPU-bound

| Clients | pages/s | gen tok/s | GPU util mean / p90 | running mean | GPU mem max |
|---|---|---|---|---|---|
| 1 | 1.323 | 1,144 | 30.3% / 57% | 45.6 | 22.3 GB |
| 2 | 1.386 (+5%) | 1,199 | 30.0% / 57% | 96.2 | 26.2 GB |
| 3 | 1.420 (+2%) | 1,228 | 30.2% / 58% | 159.3 | 31.2 GB |
| 4 | **GPU OOM** (each client ~4–5 GB; leftover client process had to be killed) | | | | |

Root cause: **pod CPU quota (31 cores) exhausted.** The vLLM 0.10.2 server process alone averaged **20.6 cores**
(image preprocessing of ~17 region crops per page); cgroup `cpu.stat`: 23,569 of 135,195 periods throttled,
145,094 CPU-s throttled. `cpu_mean` in our summaries (psutil) measures the whole 256-core host, so it hid this.

### Same model on vLLM 0.30 (`./serve.sh paddle030`) — 2× faster, same accuracy

Same weights (`/workspace/paddlex_cache/official_models/PaddleOCR-VL-1.6`), chat template, served name
(`PaddleOCR-VL-1.6-0.9B`), 4 API servers, max-num-batched-tokens 131072, max-model-len 16384, GPU util 0.6,
no prefix/mm cache; Paddle client unchanged.

| Clients | pages/s | gen tok/s | GPU util mean / p90 | running mean | GPU mem max | CPU used (cgroup) | throttled periods |
|---|---|---|---|---|---|---|---|
| 1 | **2.627** | 2,342 | 59.8% / 89% | 39.6 | 21.5 GB | 3.1 cores | 2 |
| 2 | **2.850** (+8%) | 2,485 | 60.8% / 88% | 93.5 | 26.5 GB | 3.3 cores | 2 |
| 3 | 2.912 (+2%) | 2,539 | 61.5% / 83% | 158.5 | **31.9 GB** | 3.6 cores | 4 |

Accuracy, vLLM 0.10.2 vs 0.30 (1 client, 503 control pages): num_recall 0.8363 vs 0.8356, num_precision 0.9596
vs 0.9572, word_f1 0.9395 vs 0.9374. Page by page: 486/600 identical, 88 near-identical (>98% text and numbers),
26 differ — mostly single characters (`–` vs `-`, `0` vs `0.`). One page (`220_p004`, a table-of-contents slide
both versions misread as a formula) **looped `\quad`** on 0.30 (12 KB output).

**Choice for the full run: vLLM 0.30, 2 clients, concurrency 64 → ~2.85 pages/s on typical pages**
(3 clients: +2% for 31.9/32 GB GPU memory — OOM risk). Full corpus 15,683 pages ≈ **1.5 h ≈ $1.5** on this pod;
~9.4M pages for 3,000 companies ≈ 920 GPU-h ≈ $910 on RTX 5090s.

### Why precision is 0.96 on typical pages (vs 0.99 on the hard-page bench)

On reliable control pages, 1,194 of 22,837 numbers Paddle output (5.2%) are not in the text layer:
- **1,047 (88%) come from `image` (863), `chart` (169), `header_image` (15) blocks** — numbers printed inside
  pictures/charts, which the text layer never contains. Not errors; extra information full vision captures.
- ~130 (≈0.6% of all numbers) from body text/tables. Sampled six: `8_p078` (text layer does have 0.26 — a
  counting artefact), and five where the text layer has no trace of the digits (`2_p146` 1,31,20,000; `9_p110`
  ₹4,281 crore; `2_p091` 63,000,000; `9_p026` 27,000; `7_p185` "261" page number merged into a heading).
  **Verified `2_p146` against the page image: the table prints 1,31,20,000 in the "As at 31st March, 2024"
  column and Paddle placed it correctly** — the text layer is what's missing it. No Paddle misread found in
  the sample.
- Conclusion: the precision gap is mostly the text layer's incompleteness, which supports full vision.

### Risks to handle in the full run
- **Repetition loops** (Paddle has no repetition guard): 1/600 here (`220_p004`), 2–3/780 in picture text on
  the bench set. Add a post-extraction loop detector (repeated token/phrase share, unique-line ratio) to flag
  and re-run such pages, optionally with a repetition penalty via `vlm_extra_args`.
- The pod has **no volume**: copy results back during/after the run.

**Still to do:** hand-check the 15 pages in `page_checks.json` across the three models (row attribution, chart
values) and the top of `disagreements.csv`; optionally measure Paddle with 2–3 parallel clients.

## 6. Full-corpus run: PaddleOCR-VL-1.6 (2026-10-04)

All 369 PDFs / 15,683 pages, vLLM 0.30 (`serve.sh paddle030`), concurrency 64.
- **First attempt, 2 clients: one client OOM-killed after 14 min** (pod cgroup limit 62 GB; `memory.events`
  oom_kill 1). Each Paddle client holds 16–22 GB RSS and grows ~0.25 GB/min; two clients + server reached the
  limit. Client 0 finished its half (7,842 pages); client 1 had written 550.
- With both clients the pair managed only ~1.3 pages/s (memory pressure); **client 0 alone did 2.89 pages/s**.
- **Resumed with 1 client** (`--skip-existing`, hardened `run_paddle.py`: atomic writes, JSON-validated resume):
  remaining 7,291 pages, memory peaked at ~41 GB real (anon 32 GB), finished 14:21. 15,683/15,683 pages.
- **Lesson: on this 62 GB pod use 1 Paddle client**; it is as fast as 2.

## 7. Full-corpus run: MinerU 4 (MinerU2.5-Pro), for comparison (2026-10-04)

`run_mineru.py`, tier **advanced**, **parse_mode=ocr** (default `auto` keeps text-layer text on PDFs it judges
digital — would bring back wrong OCR layers), **4 processes × 1 PDF**, `MINERU_PROCESSING_WINDOW_SIZE=32`,
`MINERU_MALLOC_TRIM=1 MALLOC_ARENA_MAX=2`. Env pinned from main (`requirements-mineru-cu130.txt`, vLLM 0.28).
- 15,683/15,683 pages, 0 failed PDFs, no OOM (anon RAM ~26–30 GB). **2.73 pages/s** (96 min), GPU 86% busy,
  21.5 VLM requests and 1,323 generated tokens per page (Paddle: ~20 and ~1,040).

Accuracy, both full runs (`score.py --runs paddleocr-vl-1.6=full mineru2.5-pro=full`, 12,498 control pages):

| | Paddle | MinerU |
|---|---|---|
| questions (25, must_contain) | **25/25** | 23/25 (missed Q15 ROE chart, Q23 income/PAT-margin chart) |
| num_recall / precision / word_f1 (markdown) | 0.828 / 0.955 / 0.940 | 0.755 / 0.974 / 0.929 |
| empty pages | 16 | 42 |

The markdown recall gap is **not** misreading: MinerU's markdown drops `header`, `footer`, `page_number` blocks
(its JSON keeps them; Paddle's markdown keeps headers). Counting **all blocks** on both sides (sample of 1,500
text + 800 table-dense control pages):

| all blocks | Paddle recall / precision | MinerU recall / precision |
|---|---|---|
| text pages | 0.966 / 0.949 | **0.975 / 0.969** |
| table-dense pages | 0.978 / 0.981 | **0.984 / 0.988** |

Non-control pages (numbers output, all blocks): scans with old OCR 75,667 vs 75,767; scans without text
6,011 vs 6,139 — equal. **Charts: MinerU outputs 32% fewer numbers** (19,575 vs 28,796 on 1,219 chart pages).
- MinerU does read charts (`image_analysis` is on by default and used by the advanced tier only): 2,431 chart
  blocks → tables (bar 1,485, donut 192, line 126, pie 124, …). But some charts are never read (e.g. 534_p027,
  534_p031). Of image blocks with no sub-type (= never analysed), **810 are large regions** (708 pages); in 326
  of them (306 pages, ~12,300 numbers) Paddle read numbers, and Paddle labels 173 of those `chart` — i.e. MinerU
  misses roughly 7% of charts (173 vs 2,429 read). Per-region list: `results/full/mineru2.5-pro/full/image_regions.jsonl`.
  - Likely cause (code, `mineru-vl-utils` 2.0.5 `mineru_client.py` `prepare_for_extract`): an image/chart ≥90%
    inside an `image_block` container is skipped, and `image_block` itself is in `skip_list`, so nothing is
    read. Hardcoded, no setting — but patchable in the venv (like the vLLM `deepencoder.py` fix).
  - **To test on the next pod:** log the layout blocks/skip reason for ~20 affected PDFs (incl. 534), patch so
    contained images/charts are analysed, re-run those PDFs and count recovered charts. If the cause is instead
    an empty model answer, retry the empty crop with MinerU's own `Image Analysis:` prompt.
  - Leave the small-region size threshold (8,090 skipped blocks, mostly logos/icons) and "natural_image"
    calls (24 regions) alone: changing them would mostly add icon noise.
- Many chart tables are **estimates off the axes** (`~61300`, `~2,380`) or meaningless (`| Blue | ~35% |`,
  marker/colour legends). Dangerous as facts for the analysis agent unless filtered (drop `~` values).

**Verdict:** MinerU is slightly better on born-digital text and tables and equal on scans; Paddle is clearly
better on charts (labelled values, 25/25 questions). Keep **PaddleOCR-VL-1.6** as the parser (superseded 2026-10-19: MinerU, see §8). If chunking needs
both, MinerU's per-page JSON (block types, boxes, HTML tables) is in `results/full/mineru2.5-pro/full/md/`.

**Repetition loops** (`detect_loops.py`, both runs): 92 pages flagged each (0.6%), but **Paddle has 34 runaway
loops** (a phrase ≥150×: `177_p031` "Month" ×2017, `104_p034` "I was" ×508, `166_p032` Korean ×679, …) vs
**MinerU 1** (`433_p003`). MinerU's server adds its own logits processor with a repetition stop (vLLM counter
`finished_reason="repetition"`); its other flags are genuinely repetitive tables (rating lists). Re-run lists:
`results/full/<model>/full/loops.jsonl`.

**Still to do:** re-run Paddle's flagged pages with `--repetition-penalty 1.05` on a future pod (F5) and merge;
hand-check top of `disagreements.csv`.

## 8. Main's parser-decision steps re-run on our corpus (2026-10-17 – 2026-10-19)

Main (`5e35ee3`, `docs/parser-decision-2026-10-17.md`) chose **MinerU advanced** on its own five companies. Same
steps, main's code unchanged, on our 369 PDFs and our two full runs: `parsing_eval/main_repl/` (how to re-run),
outputs in `data/parsing_eval/main_repl/review/`. Our MinerU run is `parse_mode=ocr` (pure vision); main's MinerU
took the PDF text layer for 214/228 PDFs, which its own doc lists as unresolved.

**D. Number fidelity** (`number_check.py`: numbers ≥3 digits vs the PDF text layer on digital pages; "changed" = one
digit off a printed number), per 10,000 output numbers:

| | pages | MinerU | Paddle |
|---|---|---|---|
| as main runs it | 9,369 | 39.0 | 73.0 |
| pages with a real text layer (`gold_reliable`) | 9,298 | 29.7 | 64.4 |
| same, without doc 9 (Reliance AR 2017-18: shifted-glyph table fonts, ~525 false flags each) | 9,106 | **16.6** | **52.9** |
| (main, its corpus) | 7,318 | 22 | 46 |

Printed numbers missed: MinerU 9.6%, Paddle 7.7%. Manual audit of main's seeded 15 flags per parser: MinerU 11
text-layer gaps (doc 9), 3 chart estimates, 1 invented text (Kannada page); Paddle 5 text-layer gaps, 5 loops /
invented sequences, 3 misreads (`1,23,594`→`124594`, `100,00,00,000`→`100,000,000,000`, `0.00`→`0000`), 2 chart
estimates. `review/number_fidelity/audit_sample.csv`.

**B. Golden facts** read off page images (never parser output), main's samplers and seeds: v2 248 facts / 64 pages /
51 docs (+7 decorative hallucination-check pages), v3 116 facts / 25 hand-picked hard pages / 20 docs (+3).
`data/parsing_eval/main_repl/data/golden/`.

**C. Score** (`cap-slice-score --clean`, L4 = label, value, column header and unit in one chunk):

| | MinerU | Paddle |
|---|---|---|
| v2 (random strata) | **211**/248 | 209/248 |
| v3 (hard pages) | **88**/116 | 85/116 |
| pooled | **299**/364 | 294/364 |
| v3 chart points | **14**/22 | 9/22 |
| v2+v3 image-only pages | 35/52 | 35/52 |
| v2 rotated scan (4 facts) | 0/4 | 3/4 (units-line chunking, both read the values identically) |

Hallucination pages: both output little more than the slide title; Paddle adds stray glyphs (`▶`, `三`, `★`).

**E. Every disagreement** (55 facts; `review/disagreements/classification.csv`): 23 unit/header line not in the chunk
(same row in both), 5 chunker drops (text in the page output, in no chunk), 5 formatting (`&amp;`, LaTeX, spacing),
17 content dropped by the parser — MinerU 13 (mostly whole charts: Reliance crack-spread and Kaynes charts, a donut,
merged "Joint Ventures/Associates" cells), Paddle 4 (a bullet, a chart, and on one slide a price series estimated off a
line chart instead of the printed table) — and 5 wrong row/column: **Paddle 4** (income block shifted one row:
revenue values under "Income"; chart titles shifted one chart; 2019-20 EPS column dropped so 2018-19 values sit
under 2019-20, scored L4; expense labels collapsed into one cell), **MinerU 1** (grouped-bar series shifted one year,
scored L4; a second shift with an omission on the same slide).

**Verdict:** main's direction holds on our data and without the text layer: MinerU has 2–3× fewer changed numbers,
slightly more L4 facts, and fewer silent row/column errors; Paddle keeps more printed numbers and more charts.
MinerU's chart drops are the image-block skip in §7 (patch to test). Main's cost argument does not carry over: on
our pod the two ran at the same speed (MinerU 2.73, Paddle 2.85 pages/s; main measured 3.91 vs 2.57).

**Decision (2026-10-19): MinerU 4.0.10 advanced tier (MinerU2.5-Pro, vLLM 0.28), `parse_mode=ocr`, is the PDF parser.**
PaddleOCR-VL-1.6 is the runner-up. Open items: test the image-block patch (§7) for MinerU's unread charts; MinerU's chart
tables can be axis estimates (`~` values) — keep them out of factual chunks unless verified.
