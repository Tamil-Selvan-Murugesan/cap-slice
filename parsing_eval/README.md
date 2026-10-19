# parsing_eval — choosing how to parse the filings' PDFs

Code for comparing PDF parsers on our BSE/NSE filings and for building the evaluation sets used by the
GPU benchmark in [`../vlm_bench/`](../vlm_bench/). Results and decisions: [`../vlm_bench/notes.md`](../vlm_bench/notes.md).

**Decision (2026-10-19): MinerU 4.0.10 advanced, `parse_mode=ocr`** — see `../vlm_bench/notes.md` §8
(main's decision steps re-run on our data). Earlier outcome, now superseded: PaddleOCR-VL-1.6 (served by vLLM 0.30) on *every* page ("full vision") — most accurate of
the three vision models tested (25/25 questions, number precision 0.99 on the hard-page set), reads charts into
labelled tables, ~2.85 pages/s on one RTX 5090. The CPU baselines (pymupdf4llm, Docling) are exact on
born-digital pages but fail on scans, scans with wrong embedded OCR layers, garbled-font text layers and charts.

## Where things live

| | |
|---|---|
| Code | this folder (in git) |
| Generated data | `data/parsing_eval/` (git-ignored; ~4.3 GB). Override with `PARSING_EVAL_DATA=/mnt/...` |
| Input | `data/pipeline.sqlite3` → `ingestion_documents` (read-only) and the downloaded PDFs it points to |

All locations are defined once in [`paths.py`](paths.py).

```
parsing_eval/
├── paths.py                    shared locations (repo, SQLite, data root)
├── profile_pages.py            cheap per-page profile of every selected PDF -> page_class per page
├── baselines/
│   ├── pymupdf4llm_parse.py    CPU baseline 1 (layout mode + RapidOCR) on the 10-document sample
│   └── docling_parse.py        CPU baseline 2 (TableFormer + RapidOCR); --force-ocr variant
├── sets/
│   ├── build_pack.py           15 hand-checked hard pages (+ vlm_test_pack_README.md)
│   ├── build_sample.py         780-page stratified bench set (hard pages over-represented) + text-layer gold
│   ├── build_repr_sample.py    600 random pages: the corpus's real page mix
│   └── build_full_set.py       every page of every selected PDF (15,683 pages) for the full run
└── eval_set/questions.json     25 hand-verified questions (easy/medium/hard) with must_contain strings
```

## Order to (re)build

Run from the repo root (`cap-slice/`), with a Python that has `pymupdf` (see `requirements.txt`):

```bash
python parsing_eval/profile_pages.py              # -> data/parsing_eval/page_profile/pages.csv   (~2 min)
python parsing_eval/sets/build_pack.py            # -> data/parsing_eval/sets/vlm_test_pack/
python parsing_eval/sets/build_sample.py          # -> data/parsing_eval/sets/bench/ + bench_set.zip
python parsing_eval/sets/build_repr_sample.py     # -> data/parsing_eval/sets/repr/  + repr_set.zip
python parsing_eval/sets/build_full_set.py        # -> data/parsing_eval/sets/full/  (1.5 GB)
```

All builders are deterministic (fixed seeds): re-running produces identical manifests.

Page classes (`profile_pages.py`): `scanned_old_ocr` (scan with an invisible, often wrong OCR text layer),
`scanned_no_text`, `chart_or_graphic`, `table_dense`, `text`. Born-digital pages (`table_dense`, `text`) get
their PDF text layer saved as `gold/<page_id>.txt`; `vlm_bench/score.py` skips gold whose text layer is itself
garbage (`gold_reliable()`: shifted-glyph fonts, symbol soup, legacy-font Kannada newspaper pages).

Page ids are `<document id>_p<NNN>` with NNN the 1-based page of the original filing.

## Baselines (CPU)

```bash
python parsing_eval/baselines/pymupdf4llm_parse.py [doc_id ...]   # -> data/parsing_eval/baselines/pymupdf4llm_output/
python parsing_eval/baselines/docling_parse.py [doc_id ...]       # -> .../docling_output/  (--force-ocr: docling_force_ocr_output/)
```

Docling needs its own venv (CPU torch + docling + rapidocr); pymupdf4llm needs `pymupdf-layout` and
`rapidocr` for its layout model and OCR. Both only read SQLite and the PDFs.
