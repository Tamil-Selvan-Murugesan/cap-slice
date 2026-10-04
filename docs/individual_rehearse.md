# Rehearsal — one parser at a time, or all four

The rehearsal runs a parser on 5 golden documents (240 pages, including the 164-page E2E FY2022-23 annual report whose statements are scanned), scores it on golden v2 and v1, and rebuilds the full comparison table — the same table the full run produces. Use it to see each parser working before the multi-hour runs.

Settings are the full run's: Docling batch 4 × `DOCLING_PROCS` processes, PyMuPDF4LLM `P4L_PROCS` processes on GPU, baseline one process per CPU, MinerU 4 documents in flight (full run: 8). Batch-size, process-count and worker comparisons: see "Trying higher …" below (`tune`).

Output: `parsed_rehearsal/` (caches), `parsed_rehearsal/review/{v2,v1}/` (scores), `parsed_rehearsal/review/gpu/COMPARISON.md` (table). Each run adds its parser; the table covers every parser rehearsed so far.

## 0. Before you start
```bash
cd /workspace/cap-slice && git pull
curl -s http://127.0.0.1:30000/v1/models | head -c 100; echo     # MinerU server up (only needed for MinerU)
```
Keep `watch -n 2 nvidia-smi` in a second pane.

## Option A — all four in one go (~20–30 min)
```bash
GPU_PRICE=0.99 tools/gpu/session.sh rehearse 2>&1 | tee /workspace/rehearse.log
cat parsed_rehearsal/review/gpu/COMPARISON.md
```
Order: MinerU → Docling → PyMuPDF4LLM → baseline.

## Option B — one parser at a time

### MinerU (server must be up)
```bash
GPU_PRICE=0.99 tools/gpu/session.sh rehearse mineru 2>&1 | tee /workspace/reh_mineru.log
cat parsed_rehearsal/review/gpu/COMPARISON.md
```

### Docling (batch 4, `DOCLING_PROCS` processes — the first line shows how many)
```bash
GPU_PRICE=0.99 tools/gpu/session.sh rehearse docling 2>&1 | tee /workspace/reh_docling.log
cat parsed_rehearsal/review/gpu/COMPARISON.md
```

### PyMuPDF4LLM (GPU)
```bash
GPU_PRICE=0.99 tools/gpu/session.sh rehearse pymupdf4llm 2>&1 | tee /workspace/reh_p4l.log
cat parsed_rehearsal/review/gpu/COMPARISON.md
```

### Baseline (CPU, seconds)
```bash
GPU_PRICE=0.99 tools/gpu/session.sh rehearse baseline 2>&1 | tee /workspace/reh_baseline.log
cat parsed_rehearsal/review/gpu/COMPARISON.md
```

Several at once also works: `tools/gpu/session.sh rehearse docling pymupdf4llm`.

## After each run — checks
```bash
grep -E "Error|Traceback|failed" /workspace/reh_*.log /workspace/rehearse.log 2>/dev/null | head    # should print nothing
p=docling   # the parser you just ran
python3 -c "
import json; d=json.load(open('parsed_rehearsal/$p/E2E/annual_reports/2023-09-21_FY2022-23/pages.json'))
print(next((t for n,t in d['pages'] if n==130), '<no page 130>')[:600])"
```
In `COMPARISON.md`, for the parser just run:
- Documents ok / failed `5 / 0`, Pages `240`
- GPU rows filled (all but baseline)
- Low-text pages recovered above 0 (all but baseline, which recovers none by design)
- Accuracy rows filled; v1 L4 for baseline is 0/6 (those pages are scanned)
- Page 130: `<no page 130>` for baseline; financial-statement numbers with years for the others

## Changing settings / redoing
- Other Docling settings: prefix the command, e.g. `DOCLING_PROCS=1 DOCLING_BATCH=16 tools/gpu/session.sh rehearse docling`.
- PyMuPDF4LLM process count: `P4L_PROCS=1 tools/gpu/session.sh rehearse pymupdf4llm`.
- To redo a parser, delete its cache first — otherwise finished documents are skipped:
  `rm -rf parsed_rehearsal/docling`
- To start the whole rehearsal over: `rm -rf parsed_rehearsal`.

## Trying higher processes / workers / batch sizes — use `tune`, not `rehearse`
The rehearsal has only 5 documents and one of them is 164 pages, so its wall time is just "how long the
biggest document took" — more processes or workers can't show up there. `tune` runs one parser on
**20 whole documents (560 pages, every doc type)**, puts each setting in its own folder
(`parsed_tune/<parser>_<settings>/`) and prints a speed table of every setting tried so far
(pages/s, $ per 1,000 pages, collection time, GPU utilisation and peak memory).

```bash
cd /workspace/cap-slice && git pull
# MinerU (server up): documents in flight
MINERU_WORKERS=8  GPU_PRICE=0.99 tools/gpu/session.sh tune mineru
MINERU_WORKERS=16 GPU_PRICE=0.99 tools/gpu/session.sh tune mineru
# several MinerU runner processes sharing the one server (server must be up); P x W = documents in flight
MINERU_PROCS=2 MINERU_WORKERS=8 GPU_PRICE=0.99 tools/gpu/session.sh tune mineru
MINERU_PROCS=4 MINERU_WORKERS=4 GPU_PRICE=0.99 tools/gpu/session.sh tune mineru
MINERU_PROCS=6 MINERU_WORKERS=3 GPU_PRICE=0.99 tools/gpu/session.sh tune mineru

# stop the MinerU server now (Ctrl+C in its window): frees ~6 GB of GPU memory for the rest

# Docling: processes x batch
DOCLING_PROCS=4 DOCLING_BATCH=4  GPU_PRICE=0.99 tools/gpu/session.sh tune docling
DOCLING_PROCS=6 DOCLING_BATCH=4  GPU_PRICE=0.99 tools/gpu/session.sh tune docling
DOCLING_PROCS=6 DOCLING_BATCH=16 GPU_PRICE=0.99 tools/gpu/session.sh tune docling

# PyMuPDF4LLM: processes
P4L_PROCS=4 GPU_PRICE=0.99 tools/gpu/session.sh tune pymupdf4llm
P4L_PROCS=8 GPU_PRICE=0.99 tools/gpu/session.sh tune pymupdf4llm
```
- Run one at a time; watch `nvidia-smi` (GPU memory must stay under 32 GB) and `top` (CPU pinned at the pod's limit = more processes won't help).
- Rough times: MinerU ~5 min, Docling ~10 min, PyMuPDF4LLM ~8 min per setting.
- Re-running the same setting resumes (skips finished documents); to measure it again, delete its folder: `rm -rf parsed_tune/docling_p6_b16`.
- Print the table again any time: `python3 tools/gpu/bench_report.py --price 0.99 --root parsed_tune`.
- **Evaluate every setting** (accuracy on the 27 v2 + 4 v1 golden facts that sit on 6 of the 20 docs, % of pages identical to a reference setting, coverage, speed, resources, cost) as one table with a column per setting:
  `TUNE_REF="mineru=mineru_w8 docling=docling_p6_b8" GPU_PRICE=0.99 tools/gpu/session.sh tune-report` → `parsed_tune/review/COMPARISON.md`
- Use the fastest setting per parser for the full run, e.g. `MINERU_WORKERS=16 tools/gpu/session.sh full-mineru`.

## Next
`GPU_PRICE=0.99 tools/gpu/session.sh bench` (nothing else running), then the full runs — `docs/gpu-run.md` step 5.
