# PROGRESS.md

Living status for `cap-slice`. Update at the end of every session. Stable rules and facts are in [`AGENTS.md`](AGENTS.md).

**Last updated:** 2026-10-03

## Current status

**Phase:** five-company research prototype — acquisition, indexing pipeline and a parser comparison. Nothing has been embedded yet (no Voyage calls, no `data/qdrant/`).

| Area | State (2026-09-26) |
|---|---|
| Catalogue & downloads | 267 rows, 259 URLs attempted, **228 PDFs** on disk (hash-verified). Coverage and document labels are **not** content-validated (see Open gaps) |
| Indexing pipeline | Committed on main (`b3fe0bd`); dry run and local Qdrant checks pass. Still uses the old flattening chunker (`chunk.py`) — not yet switched to the comparison winner |
| Parser comparison | Done for all four: baseline, Option 1 (PyMuPDF text), Option 2 (PyMuPDF4LLM), **Option 3 (Docling)** on 5 golden docs / 28 facts. **Docling most accurate: 27/28 at L4** (the only option that reads scanned tables with years intact) **but 15.2 s/page (95 min for 375 pages, ~55 h projected for the collection), 6.1 GB peak RAM.** Option 2: 21/28, 3.3 s/page. Verdict and latency: `review/README.md` |
| Other agent's work | Branch `tamil/codex-pilot-verification` (`a6ca47b`, on GitHub) holds an independent pilot verification and catalogue corrections **not yet merged into main** — see "Branches and parallel work" |
| Next decision | Parser strategy: route pages (fast parser for ordinary pages, Docling for low-text/table pages) vs Docling everywhere vs a GPU; then reconcile the branch and wire the choice into `index.py`. **C: drive is full (~210 MB free) — free space first** |

## Done

- **2026-10-03** — Reviewed RunPod deployment compatibility: `tools/gpu/session.sh` assumes a Docker-capable host, while a GPU Pod runs the workload container itself. Recommended Ubuntu 24.04 Pod with separate parser environments, or externally built custom images; CUDA 13 pins require a compatible host driver. No Pod rented, dependencies installed, or GPU tests run. Next step: adapt the session wrapper for direct execution before the paid benchmark.

- **2026-10-02** — Saved the user's question about why a dedicated public-company document chatbot is useful when general assistants can access public data, and the full response, in `docs/public-data-chatbot-value.md`. Conversation record only; no implementation decision. Next steps remain unchanged.

- **2026-09-21** — Tested direct NSE access: homepage loads, `/api/*` blocked by Akamai even with cookies/headers. BSE main site and company IR pages also 403.
- **2026-09-21** — Found the open archive layer (`nsearchives.nseindia.com`, `archives.nseindia.com`, `bseindia.com/xml-data/corpfiling`); confirmed direct PDF fetch across all 5 companies.
- **2026-09-21** — Built `data/document_availability_matrix.csv`: 267 documents (APAR 121, Hero 66, E2E 58, Esconet 14, C2C 8). 17 URLs verified `200`, 224 `untested`, 18 `blocked`, 8 `not found`.
- **2026-09-21** — Wrote `docs/document-sourcing-report.md` (sources, workarounds, ToS/subscription, scaling issues, open questions).
- **2026-09-23** — Added `AGENTS.md` and this file for hand-offs.
- **2026-09-23** — Wrote `src/cap_slice/downloader.py` (`uv run cap-slice-download`) and created `data/<SYMBOL>/<doc_type>s/` folders. Full run: **228 downloaded** (761 MB), **31 failed** — 18 × 403 (Hero company site), 11 × 404, 2 × HTML page instead of PDF. Matrix `fetch_status` updated from real fetches; added `download_status` column (yes 228 / no 39). Per-attempt log in `data/download_manifest.csv`.
- **2026-09-23** — Found that NSE serves annual reports up to FY2022-23 as ZIPs (recorded in `AGENTS.md`). Downloader now unpacks them; the 7 existing ZIPs were converted, so every downloaded document is now a PDF.
- **2026-09-23** — Wrote the indexing pipeline (`extract.py`, `chunk.py`, `embed.py`, `vectorstore.py`, `index.py`; CLIs `cap-slice-index`, `cap-slice-search`). Dry run over all 228 PDFs: 12,980 pages, **13,441 chunks = 11.0M tokens** (exact count with Voyage's tokenizer; annual reports 8.4M), no extraction failures, no document mostly scanned. Qdrant store tested locally with dummy vectors (insert, skip-if-indexed, replace-on-change, filtered search). Fixed: a run interrupted mid-upsert would have left a partial document marked as done — now `has_doc` checks stored count against `n_chunks`.
- **2026-09-26** — Validated the repo end to end. Matrix (267 rows), files on disk (228 PDFs, all start `%PDF`, no orphans), `download_status` and manifest sha256s all agree. Pipeline compiles, dry run and Qdrant checks pass. Fixed: (a) embedding batches were a fixed 64 chunks — worst case ~166K tokens, over Voyage's 120K cap — now sized by token count (≤100K); (b) the 2 URLs that returned HTML were left `untested` — now `not found`, and the downloader records such responses that way. Matrix `fetch_status` is now 228 `200` / 21 `not found` / 18 `blocked`. Committed with the indexing pipeline in `b3fe0bd` — note that commit also included the other agent's "Validation review — 2026-09-26" section below, which was in the working tree at the time and not mentioned in the commit message.
- **2026-09-26** — Parser comparison on 5 golden docs (375 pages) with 28 ground-truth facts read off page images (`data/golden/`). Code: `src/cap_slice/parsing/` (Option 1 `pymupdf_text`, Option 2 `pymupdf4llm` + RapidOCR), shared `structured_chunk.py`, runner `cap-slice-compare`. Facts at L4 (value under the right column): baseline 4/28, Option 1 15/28, **Option 2 21/28**. Option 2 is ~30x slower (21 min for 375 pages; 945 s for the report with scanned pages). Scanned statements still fail in every option (RapidOCR merges year columns, drops spaces). Verdict and file guide: `review/README.md`; scores: `review/COMPARISON.md`; per option/doc `parsed.md` (raw parser output) and `chunks.md` (what would be embedded). Along the way fixed six chunker/parser bugs (letterhead removal, a real table row deleted as boilerplate, fake tables from two-column layouts, tiny chunks, OCR `~~` markup, headings lost) — listed in `review/README.md`. New deps: `pymupdf4llm` (+ `pymupdf-layout`, `onnxruntime`), `rapidocr_onnxruntime` (~340 MB total in `.venv`, no PyTorch). Parser output is cached in `review/*/*/parsed.json` (committed, because re-parsing with Option 2 takes ~21 min).
- **2026-09-26** — Scorer now only matches a fact against chunks covering the fact's page (was: any chunk of the document). Only change: F13 (scanned P&L, p. 124) drops L1 → 0 in every option — its earlier "found" came from the directors' report quoting the same number. Totals now: value found on the page 20 / 20 / 26 (baseline / Option 1 / Option 2); L4 unchanged at 4 / 15 / 21. Scanned statements: Option 2 finds 4 of 6 values, none with the year column.
- **2026-09-28** — **Docling (Option 3) run on the golden set.** Installed with CPU-only PyTorch (`pyproject.toml` `pytorch-cpu` index; no CUDA packages; ~2 GB incl. 0.5 GB models). Defaults kept (8 threads measured slower than 4). Result, re-scored with the fixed chunker: **27/28 facts at L4** (Option 2: 21, Option 1: 15, baseline: 4); scanned statements 5/6 at L4 (Option 2: 0). Latency: 95 min for 375 pages (15.2 s/page) vs 21 min for Option 2 and 6 s for plain PyMuPDF; peak 6.1 GB RAM. Runner now records parse vs chunk time, memory, machine and measurement date, and writes a latency table with a full-collection projection (`review/COMPARISON.md`). Chunker fix S8 (units line carried into table chunks) — Docling first scored 1/8 on digital tables because of it. New `bugs_resolved.md` (27 bugs with root causes and 6 lessons). Side effect found: installing Docling makes PyMuPDF4LLM switch OCR engine on re-parse (P6).
- **2026-10-02** — Wrote `docs/pdf-parsers-pymupdf4llm-vs-docling.md`: what each parser does, the models they run (PyMuPDF4LLM: `BoxRFDGNN` layout GNN + table-grid + OCR-decision models, all ONNX; Docling: RT-DETRv2 "Heron" layout + TableFormer, PyTorch), how each decides what to OCR, why Docling reads scanned tables. Checked against the installed packages and model cards. Correction found while writing it: PyMuPDF4LLM's `~~` is MuPDF's strikethrough flag, not a low-confidence OCR marker (`bugs_resolved.md` S7 corrected).
- **2026-10-02** — Explainer video `docs/media/pymupdf4llm-vs-docling.mp4` (2:52, 1.2 MB, captions only): one scanned page through both parsers, step by step, drawn from their real outputs (`tools/explainer_video/`). Narration not added — ElevenLabs returned HTTP 402; the renderer picks up clips automatically if generated later. **Correction found while extracting the data:** PyMuPDF4LLM's scanned-table failure is in its table-grid step (3 columns found instead of 4), not OCR — RapidOCR read both values correctly as separate boxes. Fixed in the explainer doc, `review/README.md` and Open gaps.
- **2026-10-02** — **Golden set v2: 150 facts** from 61 pages of 45 documents not in v1 (`data/golden/v2_facts.csv`, guide `data/golden/README.md`). Pages drawn by a seeded stratified sample over an inventory of all 12,980 pages (`tools/golden/inventory.py`); every fact read off the rendered image; 137/140 cross-checked against the text layer. Mix: 100 table, 27 prose, 20 Q&A, 3 chart labels; 11 two-level-header facts; 10 facts on image-only pages; 8 decorative image pages kept as hallucination checks. **Finding:** E2E's Q4 FY2025-26 results PDF has a wrong embedded OCR text layer ("rrom operating activitirs", "(1 .26,245.03)") — parsers that trust text layers will get it wrong. Next: wire v2 into the scorer, then plan the GPU run.
- **2026-10-03** — **GPU-run tooling built and tested on CPU** (images not built — no Docker/disk on the laptop): batch runner `cap-slice-parse` (per-document cache + raw JSON, resume, run logs, GPU sampling); MinerU 4 adapter (MinerU2.5-Pro-2605 via a VLM server, tiers standard/advanced, HTML tables → pipe tables); Docling adapter with GPU device, batch size and per-stage timings; golden-v2 scorer `cap-slice-score`; 200-page benchmark builder; two pinned Docker images (Docling: torch 2.14.0+cu130; MinerU: vLLM 0.28.0, torch 2.13.0+cu130); `tools/gpu/session.sh`; runbook `docs/gpu-run.md`. MinerU verified end to end against MinerU's llama.cpp CPU server, including the VLM path on the scanned E2E balance sheet (4 columns, all values right). **First v2 scores (L4 of 150):** baseline 36, PyMuPDF text 76 — two-level headers 2/11, bad-text-layer PDF 1/8, image-only 0/10 (`review/v2/`). GPU: RTX 5090 ($0.99/h), A40 fallback.

## Open gaps

| Gap | Affects | Status |
|---|---|---|
| Official filed shareholding-pattern PDF not discoverable | All 5 companies | Open — only derived % from Screener |
| Periodic-results PDF not isolated | APAR, Hero MotoCorp (and E2E partially) | Open |
| ~~224 of 267 URLs not individually verified~~ | Matrix | Closed 2026-09-23 — every URL now fetched by the downloader |
| **Tables are flattened.** `chunk.py` joins all whitespace, so balance-sheet rows run together, numbers lose their column headers (which year) and units, and chunks straddle pages/sections (e.g. E2E FY2024-25 chunk 139 = auditor sign-off + balance sheet). PyMuPDF `find_tables()` out of the box also failed on that page (whole table merged into one cell) | All financial tables — mostly annual reports and results | **Partly addressed** 2026-09-26 — Options 1 and 2 keep rows, headers and units (Option 2: 8/8 digital facts under the right year column), but `index.py` still uses `chunk.py`; switch after the parser decision |
| Scanned financial statements: PyMuPDF4LLM + RapidOCR recovers the text but not the table (its table-grid step merges both year columns into one cell even though OCR read the values correctly; OCR also drops spaces and reads some `,` as `.`); 300 dpi didn't help | E2E FY2022-23 and any scanned filing | **Largely addressed 2026-09-28 by Docling:** 5/6 scanned facts under the right year column. Remaining miss is a real OCR error (990.99 read as `6960969`). Cost: ~17 s/page |
| 441 of 12,980 pages (3.4%) have no text layer — 273 mostly covered by one image, 118 small images only, 42 blank, 8 text-as-vector-outlines; includes E2E AR FY2022-23 pp. 123–164 (likely financial statements) | Search won't find that content | **Partly addressed** — Option 2's OCR recovers text on all 52 E2E FY2022-23 low-text pages and all 9 image-only slides; text quality is good for prose/slides, poor for scanned tables (row above). Pages under 50 chars are "low-text", not proven scans |
| **Catalogue error:** C2C `periodic_results` "H1 FY2025-26" (filed 2025-10-22) is a preferential-allotment outcome (shares + warrants), not financial results — checked against the page images on 2026-09-26. The URL says `Outcome_of_Board_Meeting..._updated_FS`, which is how it got matched | C2C periodic results | Open — also found independently on branch `a6ca47b` (2026-09-23). Real H1 FY2025-26 results still need finding; matrix row should be relabelled |
| Hero MotoCorp pre-2022 concalls on company site | 18 rows | `blocked` (403) — confirmed again by downloader |
| 13 matrix URLs were wrong (11 × 404, 2 × HTML page) | APAR: AR FY2022-23; presentations Feb 2023 (d), Aug 2022 (b), Aug 2021, Nov 2018 (a)/(b), Jan 2018; concalls Feb 2018, Mar 2017, Jun 2016. Hero: concall Jul 2023; presentations Sep 2018, Aug 2018 | Open — need re-discovery of the correct URLs |
| 198 of 228 downloaded rows have no `filed_date` (verified 2026-09-26) | Matrix, file naming (those files are named by period only) | Open |
| `chunk.py`: `chunk_words` argument only partly honoured — paragraphs are pre-split at the module-level size, so `chunk_words=100` still yields a 250-word chunk (verified) | Baseline chunker | Open — likely moot once `index.py` switches to `structured_chunk.py` |
| Indexing skip logic keys on file hash + chunk count, not parser/chunker version or embedding model | `index.py` / `vectorstore.py` | Open — add a pipeline version to the payload before the first real embedding run |
| Historical corrections on branch `a6ca47b` not on main: C2C listed 3 Dec 2024; E2E mainboard trading from 12 Apr 2022; issuer-hosted APAR results and shareholding reports found | `AGENTS.md` pilot table, matrix | Open — part of reconciling the branch |

## Open questions (for discussion)

1. Keep Screener.in as the discovery dependency, or build a primary-source discovery path (e.g. browser automation against NSE/BSE filing search)?
2. Accept "derived data only" for shareholding pattern, or find a dedicated discovery path?
3. At what volume does NSE Data & Analytics' paid route make more sense than the workaround? (3–4k companies × 10 years ≈ 150k–250k docs.)
4. How to discover periodic results for large mainboard companies, given pattern-matching didn't isolate them?

## Next steps

0. **GPU run on a RunPod pod** — follow `docs/gpu-run.md`: pod `runpod/pytorch:1.0.2-cu1281-torch280-ubuntu2404` + RTX 5090 + ≥ 80 GB volume + exposed SSH → `setup_runpod.sh` → rsync PDFs → `session.sh models → smoke → bench → full-mineru → full-docling` → rsync caches back. Plan: `docs/plan.md`.
1. **Free disk space on C:** (~210 MB left on 2026-09-28): compact/sparse the WSL virtual disk (`ext4.vhdx`, ~100 GB for 51 GB used) — needs `wsl --shutdown`; optionally `uv cache clean` (~1.9 GB).
2. **Parser decision** (review `review/README.md`): route pages by need vs Docling everywhere vs GPU. Before deciding, add golden facts from unseen documents (the current 28 also guided the chunker fixes) and test routing on the golden set.
3. **Reconcile branch `tamil/codex-pilot-verification` (`a6ca47b`)** into main: its verification doc, catalogue/history corrections and APAR issuer sources. Resolve `AGENTS.md`/`PROGRESS.md` conflicts by hand, keeping both agents' findings.
4. Correct the catalogue: relabel the C2C allotment row; fill missing `filed_date`s where possible; re-discover the 13 wrong URLs.
5. Switch `index.py` to the chosen parser + `structured_chunk.py`; add a pipeline/model version to the index payload.
6. Build the retrieval golden set (questions with known source pages) and run a small approved embedding test (`cap-slice-index --symbol C2C`, then `cap-slice-search`).
7. Discuss the open questions above (Screener dependency, shareholding, paid NSE route, results discovery).

## Decision log

| Date | Decision | Why |
|---|---|---|
| 2026-09-21 | Personal research, low volume only | NSE ToS prohibits automated scraping; bulk/commercial needs the paid route |
| 2026-09-21 | No crawler yet — build an availability matrix first | Understand sources and failure modes before investing in infrastructure |
| 2026-09-21 | Don't use Screener as the source of record — record the underlying NSE/BSE archive URL | Goal is to understand primary sources, not depend on an aggregator |
| 2026-09-21 | Periodic results follow the listing tier: quarterly for mainboard, half-yearly for SME | That's what each tier actually files |
| 2026-09-23 | Build a downloader for matrix URLs only (no discovery) | User wants the pilot documents on disk; stays within low-volume, sequential, throttled rules |
| 2026-09-23 | Folders keyed by NSE symbol: `data/<SYMBOL>/<doc_type>s/`; downloads gitignored | Symbol is unique and stable; 761 MB of binaries don't belong in git |
| 2026-09-23 | Unpack single-PDF ZIPs, keep only the PDF | One consistent format for later parsing; the ZIP adds nothing |
| 2026-09-23 | Embeddings: Voyage `voyage-finance-2`; vector DB: Qdrant (local mode first) | User's choice; finance-tuned model, and Qdrant's local mode uses the same client code as a server later |
| 2026-09-23 | Split stable guidance (`AGENTS.md`) from living status (`PROGRESS.md`) | Keeps rules readable; progress can grow without burying them |
| 2026-09-26 | Compare parsers with one shared chunker, scored on facts read off page images | Isolates the parser as the only variable; ground truth independent of any parser |
| 2026-09-26 | Semantic chunking deferred | Tables and Q&A are our main problems and it helps neither; test later on the chosen parser |
| 2026-09-26 | Docling deferred; PyTorch must be CPU-only (superseded 2026-09-28: Docling run with CPU PyTorch) | C: drive has ~8 GB free and the WSL disk never shrinks; default Linux PyTorch pulls several GB of unusable CUDA libraries |
| 2026-09-26 | Commit comparison outputs (`review/`, incl. parse caches) | So the user and other agents can review without re-running (~21 min for Option 2) |
| 2026-10-03 | Run on RunPod pods (user's subscription): no Docker inside pods, so `setup_runpod.sh` builds the two environments as venvs from the same pinned files; CUDA 12.8 pin sets added alongside 13.0 | Pods are containers; the base image is CUDA 12.8, and torch 2.14 only exists for CUDA 13 |
| 2026-10-03 | GPU: RTX 5090 ($0.99/h), A40 ($0.53/h) fallback; two Docker images; MinerU first, then Docling, never in parallel | Memory isn't the constraint (MinerU needs 8 GB); 5090 likely cheapest per page; sequential keeps speed measurements clean |
| 2026-10-02 | Scale up via the modified Option 1 in `docs/plan.md`: expand golden set first, then Docling + MinerU on all pages in one A100 session; drop the 375-page-only comparison; tune chunking only against retrieval | Docling is at 27/28 on v1, so v1 can't separate parsers; retrieval needs the full collection |
| 2026-09-28 | Run Docling with its default settings (4 threads) | Fairest "as shipped" comparison; 8 threads measured slower |
| 2026-09-28 | Keep Option 2's 2026-09-26 cached timings instead of re-parsing | Re-parse would take 21 min and use a different OCR engine version (P6), so results wouldn't be comparable |
| 2026-09-28 | Log every parser/chunker/scorer fix in `bugs_resolved.md` | User request: learning material for other agents |

## Branches and parallel work

| Branch / worktree | Commit | What it is | Status |
|---|---|---|---|
| `main` | `4c37cc3` (2026-10-03) | Everything above + golden set v2 + GPU-run tooling (runner, adapters, Docker images, runbook) | Pushed |
| `tamil/codex-pilot-verification` (on GitHub) | `a6ca47b` (based on `cbe2f7f`) | Another agent's independent pilot verification: `docs/pilot-verification-2026-09-23.md`, corrected `AGENTS.md`/`PROGRESS.md`/report | **Not merged** — see Next steps 3 |
| `pilot-test-2` (local worktree `../cap-slice-1`) | `cbe2f7f` | Local only; no commits beyond main's history | Unknown purpose — ask before removing |

## Validation review — 2026-09-26

This review checks the current working tree, including the other agent's uncommitted indexing pipeline. The earlier reconciled verification report remains on `tamil/codex-pilot-verification` (`a6ca47b`) and has not been integrated into main. Preserve the indexing work when reconciling those documentation changes.

**Verified locally:** all 228 downloaded files exist, begin with PDF signatures, and match the SHA-256 values in `data/download_manifest.csv`. They total 799,182,012 bytes and 12,980 PDF pages. The catalog has 267 rows: 259 URLs and eight gap placeholders. The recorded downloader outcomes are 228 successes, 18 HTTP 403s, 11 HTTP 404s, and two HTTP 200 responses containing HTML. These are historical network results; this review did not re-fetch exchange URLs.

**Coverage is still incomplete:** downloaded labels comprise 43 annual reports, four periodic-results candidates, 86 transcripts and 95 presentations; no shareholding reports are in the current downloaded catalog. 198 downloaded rows have no filing date. These counts describe catalog labels, not content-validated coverage.

**Reconfirmed content corrections:** C2C's four-page H1 FY2025–26 results candidate is an equity/warrant allotment disclosure and should not enter a financial-results index under that label. C2C's FY2024–25 annual report dates listing to December 3, 2024; E2E's FY2022–23 annual report dates mainboard trading to April 12, 2022. Main's guidance still needs those historical corrections. The earlier pilot also found issuer-hosted APAR results and shareholding reports; those sources have not been incorporated into this catalog or re-fetched in this review.

**Fresh full dry run:** all 228 PDFs completed extraction/chunking with zero failures and no whole-document OCR skips: 12,980 pages, 13,441 chunks, and 441 low-text pages omitted (3.4%). This independently reproduces the previously recorded chunk/page totals, but does not establish correct table interpretation or complete page coverage. No embeddings were generated.

**Indexing validation:** local Qdrant tests with temporary dummy vectors passed partial-document detection, complete-document detection, hash-change detection, replacement, and symbol-filtered search. There is no `data/qdrant/` store in this checkout. No live embedding/search API calls were made; actual retrieval quality and paid indexing remain unvalidated. The earlier 11.0M-token count has not been independently recounted in this review.

**Extraction issues reproduced:** E2E FY2022–23 PDF pages 123–164 are all omitted by the current extraction threshold (52 of 164 pages omitted overall), but the document is not rejected by the majority-page OCR rule. E2E FY2024–25 chunk 139 spans PDF pages 106–108 and combines auditor text with flattened balance-sheet content. Pages below 50 characters should be described as low-text/omitted, not automatically classified as scans or proven to lack a text layer.

**Additional code limitations:** document skipping keys on file hash and stored chunk count, not parser/chunker version, metadata or embedding model. A parser or metadata correction therefore requires deliberate reindexing; model compatibility is documented but not enforced against an existing collection. A focused chunking check also showed that `chunk_words=100` still produced one 250-word chunk because paragraph splitting uses the module-level size.

**Recommended order:** (1) reconcile the two agents' documentation and correct catalog labels/history; (2) preserve financial-table headers, units and section boundaries and recover relevant omitted pages with OCR; (3) add regression checks and version-aware indexing; (4) evaluate a small, approved embedding run against representative questions with known source pages; (5) commit the reviewed pipeline, expand validated coverage, and confirm source/access rights before bulk discovery. The existing research-stage restriction on crawler development remains in force.

No implementation changes, commits, paid calls or new research artifacts were made by this validation review; its only repository edit is this progress update.

**Follow-up to this review (later on 2026-09-26, main agent):**
- "The indexing pipeline is uncommitted" — it was committed in `b3fe0bd` (which also carried this review section).
- Item (2), table headers/units/section boundaries and OCR: tested in the parser comparison — Option 2 keeps them for digital tables and recovers low-text pages, but scanned tables remain broken. Not yet in `index.py`.
- Verified independently: 198 downloaded rows lack `filed_date`; the `chunk_words` bug; the C2C misclassification (checked against page images).
- Not yet done: reconciling the two agents' documentation (item 1), version-aware indexing (item 3), approved embedding test (item 4). All are in Next steps.
