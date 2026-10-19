# Progress

Last updated: 2026-10-19.

## Goal and scope

Build a fundamental-analysis agent grounded in company filings: collection → curation → parsing → chunking → embeddings/vector database → retrieval → analysis with source citations. BSE and NSE are the primary sources. The target scope is approximately 3,000 companies; the current sample covers five.

## Implemented download pipeline

- Runtime package: `filings/`; offline regression tests: `tests/`.
- BSE sample: 543664 (Kaynes), 540699 (Dixon), 500325 (Reliance). The user reviewed these companies and was satisfied with collection scope.
- NSE sample: AIMTRON and ADISOFT. The adapter currently supports Emerge/SME; mainboard support is not implemented.
- Both collectors default to ten years of discovery. Availability may be shorter.
- Six categories: annual reports, shareholding, investor presentations, call transcripts, credit ratings and financial results.
- NSE filters announcement metadata before downloading. Full responses, including rejected announcement metadata, are retained in SQLite.
- SQLite stores run history, company outcomes, document metadata, attempt history, full API responses, curation decisions and HTML chunks.
- Downloads use temporary files and atomic renames. Each completed task is checkpointed. Valid existing files are reused after interruption.
- Explicit failed-file and run-based retries; configurable default failure threshold is 5%. Discovery failures and unfinished work also flag retries.
- A process lock allows one writer; interrupted runs are recovered on the next writer startup.
- Curation selects required categories, handles revisions and alternate formats, and removes identical-content duplicates. Both collectors invoke it automatically.
- Optional hash-matched content-review overrides remain in `config/nse_verified_announcements.json`; automatic selection for new companies requires no review entry.

## Current local data

`data/pipeline.sqlite3` is the only metadata index. Downloaded documents and NSE detail JSON remain on disk; back them up together with SQLite.

| Metric | Count |
| --- | ---: |
| Document records | 775 |
| Downloaded records | 736 |
| Failed records | 32 |
| Permanently inactive records, excluded from ingestion | 7 |
| Selected documents | 476 |
| PDF documents awaiting extraction | 369 |
| Structured JSON documents | 84 |
| HTML/iXBRL documents | 23 |
| HTML chunks | 306 |

Selected documents by company: Reliance 197, Dixon 146, Kaynes 91, AIMTRON 33, ADISOFT 9.

Existing sample files were imported offline. Original download timestamps were unavailable and remain null; the recorded initial run describes the import rather than claiming new downloads. Original API fields never saved during initial collection cannot be reconstructed. Future runs retain full responses.

## Latest cleanup and verification

Removed unused configuration and utilities, duplicate file indexes, and disk copies of listing responses after verifying all original metadata fields and saved responses exist in SQLite. Collectors now store listing responses only in SQLite. Active NSE detail JSON remains document content required by curation and retry processing.

- All 15 offline tests passed, covering filtering, full-response retention, metadata preservation, retries, interruptions, writer locking, discovery failures, thresholds and curation.
- Offline curation: 476 selected documents, 292 ordinary exclusions, 306 HTML chunks. Seven inactive records remain excluded separately.
- Compared every ingestion-view row, chunk row and run-history row before and after cleanup: unchanged.
- SQLite integrity and foreign-key checks passed.
- No live exchange downloads were run. The 32 existing failures remain unresolved.
- No Git commit or push was performed.

## Commands

Run from the repository root:

```bash
venv/bin/python -m filings.status
venv/bin/python -m filings.status --failures
venv/bin/python -m filings.bse 543664 540699 500325 --years 10 --download
venv/bin/python -m filings.nse AIMTRON ADISOFT --years 10 --download
venv/bin/python -m filings.nse --retry-failed
venv/bin/python -m filings.bse --retry-run RUN_UUID
venv/bin/python -m filings.curate
venv/bin/python -m unittest discover -s tests -v
```

See `README.md` for schema fields and command options; `docs/pipeline.md` explains each runtime module.

## PDF parsing evaluation (2026-10-02 – 2026-10-04)

Code: `parsing_eval/` (page profiling, CPU baselines, evaluation-set builders, 25 hand-verified questions) and `vlm_bench/` (RunPod GPU benchmark: setup, servers, runners, scoring). Generated data: `data/parsing_eval/` (git-ignored, ~4.3 GB). Full numbers and observations: `vlm_bench/notes.md`.

- Profiled all 15,683 pages of the 369 selected PDFs: 69% born-digital text, 13% dense tables, 8% charts, 8% scans with an old (often wrong) OCR text layer, 2% scans without text. ~9% of born-digital control pages have unusable text layers (shifted-glyph fonts, symbol soup, Kannada newspaper notices).
- CPU baselines (10-document sample): pymupdf4llm and Docling are exact on born-digital pages but fail on scans, wrong OCR layers, broken fonts and charts.
- GPU comparison (780-page stratified set, one RTX 5090): **PaddleOCR-VL-1.6** 25/25 questions, number precision 0.990, charts → labelled tables; GLM-OCR 25/25, 0.972, chart periods can misalign, slowest; Unlimited-OCR 22/25 (cannot read charts), 0.968, fastest but hallucination loops incl. invented numbers.
- *(Superseded 2026-10-19 — see below.)* Earlier choice: PaddleOCR-VL-1.6 on every page (full vision), served by vLLM 0.30 (2× faster than PaddleOCR's pinned vLLM 0.10.2, same output; 0.10.2 was CPU-bound), 2 client processes → ~2.85 pages/s on a representative 600-page sample (≈1.5 h for the corpus). Precision vs the text layer on typical pages is 0.96 because 88% of the "extra" numbers are printed inside pictures/charts and the text layer lacks them; sampled body-text mismatches were text-layer gaps, not misreads.
- Full-corpus runs (15,683 pages each, RunPod, 2026-10-04) completed for **PaddleOCR-VL-1.6** and, for comparison, **MinerU 4 (MinerU2.5-Pro)** (`vlm_bench/run_mineru.py`). Outputs per page: markdown + JSON (all blocks with labels and boxes) in `data/parsing_eval/results/full/<model>/full/md/`; backed up to R2 (`backup_r2.sh`, `sirisha/data/parsing_eval/`).
- Full-corpus comparison (notes §7): Paddle 25/25 questions vs MinerU 23/25 (missed two chart questions). Counting all blocks, MinerU is slightly better on born-digital text and dense tables (recall/precision 0.975/0.969 vs 0.966/0.949 on text pages); equal on scans. Paddle is clearly better on charts: MinerU outputs 32% fewer chart numbers, never reads some large chart regions, and many of its chart values are axis estimates (`~61300`). MinerU's unread large image regions (~7% of charts) look like a hardcoded skip that can be patched; test on the next pod (notes §7).
- Repetition loops (`detect_loops.py`): 92 pages flagged in each run (0.6%); Paddle has 34 runaway loops, MinerU 1 (its server stops on repetition). Re-run lists: `results/full/<model>/full/loops.jsonl`.

## Main's parser decision re-run on our data (2026-10-17 – 2026-10-19)

Main (`5e35ee3`) recommends MinerU advanced. Re-ran its steps with its code unchanged on our 369 PDFs and both full runs (`parsing_eval/main_repl/`, outputs in `data/parsing_eval/main_repl/`, details in `vlm_bench/notes.md` §8). Our MinerU run is pure vision (`parse_mode=ocr`); main's mostly used the PDF text layer.

- **Number fidelity** (main's `number_check.py`, changed numbers per 10,000): MinerU 39.0 vs Paddle 73.0; 16.6 vs 52.9 after dropping unreliable text layers and doc 9. Manual audit of 30 flags: Paddle has misreads and counting loops, MinerU mostly text-layer false alarms and chart estimates.
- **Golden facts built** (read off page images, main's samplers/seeds): v2 248 facts, v3 116 facts, plus 10 hallucination-check pages. Kept in `data/parsing_eval/main_repl/data/golden/` (git-ignored); backed up and verified 2026-10-19 with `./backup_r2.sh parsing_eval/main_repl/data/golden parsing_eval/main_repl/review parsing_eval/main_repl/golden_work` to R2 `sirisha/data/parsing_eval/main_repl/`. Re-run that command after editing the facts.
- **Scores (L4)**: MinerU 211 vs 209 (v2), 88 vs 85 (v3), pooled 299 vs 294 of 364; MinerU better on chart points (14 vs 9 of 22).
- **All 55 disagreements diagnosed**: most are chunking/formatting; real errors are MinerU dropping whole charts (13) and Paddle silent row/column shifts (4, two of them scored as correct).
- **Conclusion:** main's choice holds on our data, without the text layer. Main's cost advantage does not: both ran at ~2.8 pages/s on our pod.
- **Decision (2026-10-19): MinerU 4.0.10 advanced tier (MinerU2.5-Pro on vLLM 0.28), `parse_mode=ocr`, is the PDF parser.** PaddleOCR-VL-1.6 is the runner-up. Its full-corpus output is `data/parsing_eval/results/full/mineru2.5-pro/full/` (per-page markdown + block JSON, whole-document middle JSON in `docs/`).
- Not committed: `parsing_eval/main_repl/` scripts and README; the notes/progress edits.

## Next stage and limitations

Use SQLite `ingestion_documents` as the parsing/ingestion allowlist. Never scan all downloaded files for ingestion. Existing HTML chunks are in `document_chunks`. PDF parser: MinerU advanced (`parse_mode=ocr`, decided above); design chunking on its block JSON. On the next pod, test the image-block patch (notes §7) so MinerU reads the large chart regions it skips (~7% of charts), and keep its estimated chart values (`~`) out of factual chunks. Structured results/shareholding JSON needs an explicit structured-data path.

Before chunking: set aside non-English (regional-language newspaper) pages, where every model produced garbage; normalise the currency symbol from the unit line (models misread ₹ as £/है); cross-check numbers on born-digital pages against reliable text layers. No embedding model, vector database or analysis-agent implementation has been selected. Preserve filing dates, reporting periods, accounting basis, units, source URLs, hashes and page/table references through parsing. Metadata classification is not PDF content verification and does not guarantee complete exchange coverage.

Before large-scale collection, a small live smoke run can verify current exchange responses. Partial attachments restart from byte zero; successful files are reused. The next useful work is designing PDF extraction and chunking using the selected documents.
