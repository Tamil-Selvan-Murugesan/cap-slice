# PaddleOCR-VL-1.6 on our pipeline

Option 5 in the parser comparison: **PaddleOCR-VL-1.6**, the full pipeline: a PP-DocLayout layout model
(PaddlePaddle, in the client process) plus a 0.9B vision-language model (served by vLLM) for every detected
region. Every page goes through vision. The co-founder's evaluation (branch `main-sirisha`, `vlm_bench/`)
chose it. This brings it into our runner, so it's scored on the same golden sets (v2 150 facts, v1 28) and
appears in the same comparison table as baseline, PyMuPDF4LLM, Docling and MinerU.

**Settings are theirs** (`vlm_bench/run_paddle.py`, `notes.md` §5), so results are comparable:

| | |
|---|---|
| Pipeline | `pipeline_version="v1.6"`, chart recognition on (charts → tables), OCR inside picture blocks on |
| Markdown | footers, footer images and page numbers left out (still in the raw JSON) |
| Input | each page rendered at 200 DPI |
| Server | vLLM ≥ 0.30 (`--api-server-count 4`, `--max-num-batched-tokens 131072`, GPU util 0.6, no prefix/mm cache): ~2× PaddleOCR's own vLLM 0.10.2 server, same output |
| Clients | 2 processes × 64 region requests in flight (3 processes: +2 % speed at 31.9 of 32 GB GPU memory) |

Their measured speed on an RTX 5090: ~2.85 pages/s on typical pages.

## Files

| File | Role |
|---|---|
| `tools/gpu/setup_paddleocr_vl.sh` | adds two envs to a pod already set up with `setup_runpod.sh`: `paddle` (PaddlePaddle 3.2.1 cu129 + `paddleocr[doc-parser]` + cap-slice) and `vllm030` (vLLM ≥ 0.30); downloads the weights with PaddleX's own downloader (HuggingFace `PaddlePaddle/PaddleOCR-VL-1.6`) |
| `src/cap_slice/parsing/paddleocr_vl.py` | the adapter: renders pages, runs the pipeline, writes per-page Markdown (HTML tables → pipe tables, picture placeholders removed) + `paddleocr_vl.json` (every block with label and box) |
| `tools/gpu/session.sh` | `paddle-server`, `smoke-paddle`, `full-paddle`, `tune paddleocr_vl`; `compare` / `tune-report` include it |

## Run (pod, from `/workspace/cap-slice`; nothing else on the GPU)

```bash
git pull
tools/gpu/setup_paddleocr_vl.sh 2>&1 | tee /workspace/setup_paddle.log       # once, ~15-30 min
# checks at the end: "paddle ... cuda: True", "PaddlePaddle works well on 1 GPU",
# "vllm 0.30.x ... RTX 5090 (12, 0)", "cap-slice adapter ok"

tmux new-window -n paddle 'cd /workspace/cap-slice && tools/gpu/session.sh paddle-server; echo SERVER EXITED; exec bash'
until curl -sf http://127.0.0.1:8118/v1/models >/dev/null; do sleep 10; done; echo READY

tools/gpu/session.sh smoke-paddle                    # 4-page PDF: one "ok" line
PADDLE_PROCS=2 tools/gpu/session.sh full-paddle 2>&1 | tee /workspace/full_paddle.log
GPU_PRICE=1.01 tools/gpu/session.sh compare          # scores + the comparison table, all parsers
```

Watch GPU memory (`nvidia-smi`; their 3-client run peaked at 31.9 of 32 GB) and pod RAM
(`/sys/fs/cgroup/memory.current` vs `memory.max`). Resume = run the same command again (finished documents
are skipped); `RETRY_FAILED=1` redoes failed ones.

**Known risks (their notes):**
- **Repetition loops:** no repetition guard in the VLM, ~1 % of pages can loop (e.g. `\quad` repeated). We
  don't detect them yet; their `vlm_bench/detect_loops.py` does, and a re-run with repetition penalty 1.05
  fixes most.
- **Regional-language pages** (e.g. Kannada newspaper ads) come out as garbage in every model.
- **Numbers from pictures:** about 5 % of numbers it outputs on digital pages aren't in the PDF text layer.
  Most (88 %) come from charts and pictures, i.e. real extra information, not invented. Like MinerU's
  image descriptions, decide at chunking time whether to keep picture text.

Untested on this pod until `smoke-paddle`: the setup and the adapter were written against their tested
scripts and checked here only with a stand-in pipeline.
