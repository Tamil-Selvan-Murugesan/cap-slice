# Rehearsal — one parser at a time, or all four

The rehearsal runs a parser on 5 golden documents (240 pages, including the 164-page E2E FY2022-23 annual report whose statements are scanned), scores it on golden v2 and v1, and rebuilds the full comparison table — the same table the full run produces. Use it to see each parser working before the multi-hour runs.

Settings are the full run's: Docling batch 4 × `DOCLING_PROCS` processes, PyMuPDF4LLM `P4L_PROCS` processes on GPU, baseline one process per CPU, MinerU 4 documents in flight (full run: 8). Batch-size and process-count comparisons are `bench`'s job, not this one's.

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

## Next
`GPU_PRICE=0.99 tools/gpu/session.sh bench` (nothing else running), then the full runs — `docs/gpu-run.md` step 5.
