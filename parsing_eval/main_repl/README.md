# main_repl — main's parser-decision steps, run on our corpus

Main branch (commit `5e35ee3`, `docs/parser-decision-2026-10-17.md`) chose MinerU advanced over PaddleOCR-VL-1.6
on its own five companies. This folder re-runs the same steps, with main's code unchanged, on our 369 PDFs
and our two full runs (`results/full/{paddleocr-vl-1.6,mineru2.5-pro}/full`). Results: `vlm_bench/notes.md` §8.

Workspace (git-ignored): `data/parsing_eval/main_repl/` — main's `src/` + `tools/` at `5e35ee3`, our PDFs as
`data/<SYMBOL>/<type>/<doc_id>.pdf` (hard links), converted caches `parsed/paddleocr_vl/`, `parsed_ocr/mineru/`,
our golden sets in `data/golden/`, outputs in `review/`.

```bash
WS=data/parsing_eval/main_repl
python3 parsing_eval/main_repl/build_workspace.py --code-only
uv venv -p 3.12 $WS/.venv && uv pip install -p $WS/.venv pymupdf==1.28.2 pillow
uv pip install -p $WS/.venv --no-deps -e $WS
$WS/.venv/bin/python parsing_eval/main_repl/build_workspace.py          # A: PDFs + converted caches
cd $WS
.venv/bin/python tools/golden/inventory.py                                # page inventory + v2 candidates
.venv/bin/python tools/golden/number_check.py parsed_ocr/mineru parsed/paddleocr_vl --out review/number_fidelity   # D
.venv/bin/python tools/golden/number_audit.py review/number_fidelity --parsers parsed_ocr/mineru parsed/paddleocr_vl
.venv/bin/python tools/golden/v3_candidates.py --out golden_work/v3      # v3 thumbnail sheets
for v in v2 v3; do                                                       # C
  .venv/bin/cap-slice-score --parser mineru --cache parsed_ocr --clean --name mineru_ocr \
      --facts data/golden/${v}_facts.csv --skipped data/golden/${v}_skipped.csv --out review/$v
  .venv/bin/cap-slice-score --parser paddleocr_vl --cache parsed --clean --name paddleocr_vl \
      --facts data/golden/${v}_facts.csv --skipped data/golden/${v}_skipped.csv --out review/$v
done
```

`number_check_reliable.py` re-runs D on pages whose text layer is real text (and optionally without whole
documents). Golden facts (`data/golden/v2_facts.csv` 248, `v3_facts.csv` 116, plus `*_skipped.csv` hallucination
checks) were read off page images, never from parser output — the expensive part. Back up after any change:
`./backup_r2.sh parsing_eval/main_repl/data/golden parsing_eval/main_repl/review parsing_eval/main_repl/golden_work`
(R2 `sirisha/data/parsing_eval/main_repl/`; last backup 2026-10-19).
Step E's per-fact diagnosis is `review/disagreements/classification.csv`.

Differences from main's setup: our MinerU run used `parse_mode=ocr` (main's used the default, which took the PDF
text layer for 214 of 228 PDFs); our corpus adds credit-rating letters and Kannada newspaper notices.
