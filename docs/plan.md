# Plan: scaling to all 12,980 pages

Agreed 2026-10-02. Status of each step is tracked in [`PROGRESS.md`](../PROGRESS.md); this page records the plan and the reasoning behind it.

## The decision: a modified Option 1

Four options were on the table:

| Option | What it meant | Verdict |
|---|---|---|
| 1 | Run Docling and MinerU on all 12,980 pages on a rented A100, with a broader golden set | **Chosen, modified:** expand the golden set *first*, then run both parsers on everything in one GPU session; decide chunking only once retrieval can be measured |
| 2 | Compare MinerU and Docling on the current 375 golden pages only | **Dropped.** Docling already scores 27/28 there, so MinerU can't show a meaningful difference. The 28 facts also helped tune the chunker, so they're partly "seen" data. GPU time spent, nothing learned |
| 3 | Skip the VLM; go straight to local embeddings and retrieval, then GPU for Docling only | **Not chosen.** Retrieval measured on 375 pages flatters every method (few competing documents); real difficulty comes from thousands of similar pages across companies and years, which needs the full collection parsed. And once the GPU is rented, adding MinerU is a second run in the same session — dropping it saves little and leaves "is the VLM better?" unanswered |
| 4 | Question: is structure-aware chunking enough, or experiment with chunking before retrieval? | **Keep the current chunker; don't tune it until retrieval can be measured** (see "Chunking" below) |

## Steps

| # | Step | Where | What | Why |
|---|---|---|---|---|
| 1 | **Expand the golden set** | Laptop, no GPU | ~120–150 new facts read off page images, from documents *not* in v1, weighted to hard cases: scanned statements, tables across pages, nested/merged headers, slide charts, footnotes, continued sections, concall Q&A | Removes the ceiling and the "seen data" problem *before* the GPU decision rests on it. **Done 2026-10-02: 150 facts (`data/golden/v2_facts.csv`)** |
| 2 | **One GPU session** | RTX 5090 32 GB (A40 fallback) — runbook: [`gpu-run.md`](gpu-run.md) | Run **Docling and MinerU on all 12,980 pages**, with per-document caching and resume; record latency and failures. Benchmark on a few hundred pages in the first hour before committing to the full run | Parse the whole collection once; then compare both on the expanded golden set |
| 3 | **Choose the parser** | Laptop | Score both from the caches (no re-parsing). Also try routing: fast parser for ordinary pages, Docling/MinerU for scanned and table-heavy pages | Accuracy, speed and failure types measured on data neither parser was tuned on |
| 4 | **Retrieval golden set** | Laptop | **200 hard questions** with every answering page listed, across companies, years, document types and evidence kinds (tables, charts, prose, concall Q&A, scanned pages) — see [Retrieval experiments](#retrieval-experiments-agreed-2026-10-17) | Needs the full-collection parse in place |
| 5 | **Retrieval experiments** | Laptop | Embedding model, chunking, image handling, hybrid search + reranker — one variable per round, in the order below | Chunking only matters through retrieval, so it's judged there |
| 6 | **Full indexing** | Laptop or GPU | Index everything with the winning setup | Last, because it depends on all the choices above |

## Chunking

The current structure-aware chunker (`structured_chunk.py`) is good at what we've measured: it keeps table rows, headers and units together, so information *survives*. Whether it gets *found* is a separate question — chunk size, overlap and what goes into each chunk all affect that — and tuning it against 28 facts would overfit.

- **Before the GPU run:** only parser-side fixes that are certain to help. Fix the S9 caption noise (stop a table's caption at a page boundary) — it adds unrelated text to table chunks regardless of what else we choose.
- **In step 5, compare:**
  1. Current structure-aware chunker (baseline)
  2. Tables as their own chunks, plus a one-line summary that's embedded, with the full table kept for the answer
  3. Document-type-specific splits: Q&A pairs for concalls, one slide per chunk for presentations
  4. Small-to-big: search small chunks, return the surrounding section
  5. Possibly semantic chunking, for long prose sections only

Semantic chunking is deferred, not rejected: it can help inside long prose sections with no headings, but not with tables or Q&A, which are our main problems.

## Retrieval experiments (agreed 2026-10-17)

Parsing is measured by "did the fact survive" (golden v1–v3). From here on every choice is measured by
**"does search find the page that answers the question"**, on one fixed question set, changing one
thing at a time.

### Held fixed in every round

| Fixed | Value |
|---|---|
| Parser and its cache | the parser chosen in step 3, full collection (12,980 pages), never re-parsed during the experiments |
| Clean-up | `page_clean.py`, same version throughout |
| Corpus | all 228 documents of the five pilot companies — every question competes against every page, including the same table in other years and the other companies' versions of it |
| Question set | `data/golden/retrieval_questions.csv` (200 questions), frozen before the first experiment; never edited to suit a result |
| Scoring | page-level hit: a retrieved chunk counts if it covers any of the question's answer pages; Recall@5/@10/@20, MRR@10, reported overall and per stratum |
| Retrieval settings | top-k, distance (cosine), vector store (Qdrant server, HNSW m 16 / ef_construct 128, search hnsw_ef 128) unchanged within a round; every round reports the same filter setups (see [Filters](#filters-agreed-2026-10-19)) |
| Stored metadata | the payload schema in [Vector store and metadata](#vector-store-and-metadata-agreed-2026-10-19) |

### Varied, one per round, in this order

| Round | Variable | Options | Held at |
|---|---|---|---|
| 0 | — | baseline: current structure-aware chunker (after the known-bug fixes below, tagged), dense search only | — |
| 1 | **Embedding model** | closed: **Voyage 4 Large** (API); open: **Nemotron 3 Embed 8B**, BF16 checkpoint (open weights) — compared at 2048 dimensions (decided 2026-10-19, see below) | baseline chunker |
| 2 | **Chunking** | (a) baseline; (b) a context header on every chunk — company, doc type, period, section, page; (c) tables as their own chunks with an embedded one-line summary, full table returned; (d) per-type splits — one Q&A pair per concall chunk, one slide per chunk; (e) small-to-big | round-1 winner |
| 3 | **Images** | A text only (what the parser reads from pictures); B generated per-image summaries embedded as text, flagged `generated`; C page-image embeddings (ColPali/ColQwen-style or a multimodal embedding model) for image-heavy pages; D = A + C routed by page type | round-2 winner |
| 4 | **Search** | dense only vs hybrid (BM25 + dense, fused); then + a reranker on the top 50–100 | round-3 winner |
| 5 | **Re-check** | both embedding models again on the final setup (the best model can change with chunking) | final setup |

**Before round 0 (bug fixes, not experiments):** chunks carrying a stale heading from an earlier
section, lost units/subsection labels, and labels split from their values (found in the 2026-10-06
visual review). Fix, then tag the chunker version as the baseline. **Done 2026-10-18:** fixes S13–S21
(`bugs_resolved.md`), golden v2+v3 L4 up for both finalists with no fact worse, keyword baseline unchanged
within noise; baseline tagged `chunker-baseline-2026-10-18`.

**Decision rule.** A variant wins only if it improves Recall@10 overall **and** no stratum with ≥ 15
questions drops by more than one question in ten. With 200 questions, overall differences under ~4
points are within noise: compare per-question hits of the two variants (paired; count questions
won and lost) rather than headline percentages.

### Embedding models (agreed 2026-10-19)

| | Voyage 4 Large (closed) | Nemotron 3 Embed 8B, BF16 (open) — `nvidia/Nemotron-3-Embed-8B-BF16` |
|---|---|---|
| Access | Voyage API | open weights (OpenMDW-1.1, commercial use allowed; built on Ministral-3-8B-Instruct-2512, Apache 2.0) |
| Context | 32K tokens | 32K tokens (NVIDIA evaluated at 4096) |
| Dimensions | 1024 default; 256/512/2048 | 4096 native; can be cut to the first 2048 or 1024 and L2-renormalised |
| Compared at | **2048** (its largest) | **2048** (first 2048 dims, renormalised) — same size, so dimension doesn't decide the result; native 4096 scored once as a side check |
| Query vs document | `input_type="query"` / `"document"` | Sentence Transformers `encode_query` / `encode_document` apply the saved prompts; with plain Transformers or vLLM the `query: ` / `passage: ` prefixes must be added by hand (quality drops silently without them) |
| Cost / compute | ~34M tokens for the corpus, ~$4 at ~$0.12/M (third-party price — confirm on Voyage's pricing page before running) | ~16 GB of BF16 weights: **needs a GPU** (Ampere or newer; NVIDIA tested A100/H100 80 GB; a 32 GB RTX 5090 fits). Not feasible on this laptop's CPU. Options: a short RunPod session (Sentence Transformers ≥ 5.4.1 / Transformers ≥ 5.2.0, or vLLM 0.25) or a hosted endpoint (DeepInfra, Fireworks) |

### Vector store and metadata (agreed 2026-10-19)

A **Qdrant server** running locally (official v1.19.1 binary, `tools/qdrant/serve.sh`, storage in
`data/qdrant/`, bound to 127.0.0.1) — the same engine and API as a production deployment, not the client's
embedded mode. **One collection per setup** — vectors from different models or chunkers can't share one —
named `<round>__<model>-<dim>__<chunker>`, e.g. `r1__voyage-4-large-2048__baseline`. Cosine distance, HNSW
index (m 16, ef_construct 128), payload indexes on the filter fields (`symbol`, `doc_type`, `doc_id`,
`period_kind`, `chunk_kind` as keyword; `fiscal_year` as integer). Searches use HNSW with hnsw_ef 128;
each round also runs one exact (exhaustive) search to measure what the approximate index loses.
Runner: `cap-slice-retrieval-dense count | embed | load | search` (`src/cap_slice/retrieval_dense.py`);
embeddings are saved per request batch before the next is sent, so an interrupted run resumes without
re-embedding.

**What gets embedded vs what is stored.** Changing the embedded text means re-embedding (cost, hours);
changing the payload doesn't (Qdrant `set_payload`). So in round 1 the embedded text is the bare chunk and
all metadata is payload only. Writing metadata *into* the embedded text (a context header) is round 2(b).

| Group | Fields | Source |
|---|---|---|
| Provenance (citations, debugging) | `doc_id`, `path`, `company`, `symbol`, `listing_tier`, `doc_type`, `period_label`, `filed_date`, `source_url`, `chunk_index`, `page_start`, `page_end`, `text` | matrix + chunker |
| Filters (values a question can supply) | `symbol`, `doc_type`, **`fiscal_year`** (int, year the FY ends: FY2018-19 → 2019, Q3 FY24 → 2024), **`period_kind`** (`annual` / `quarter` / `half_year` / `event`), `chunk_kind` (`table` / `text`), `section` | `periods.py` normaliser (below); chunker |
| Bookkeeping | `period`, `period_source`, `parser`, `chunker_version` (git tag), `embedding_model`, `image_only_page` (page inventory), `generated` (round 3 summaries) | run settings |

**Period normaliser** (`src/cap_slice/periods.py`, built 2026-10-19). Adds `fiscal_year`, `period_kind`,
`period` ("Q3 FY24") and `period_source` to every document:
- `label` — annual reports and results: read from the catalogue label (`FY2018-19` → 2019, `Q4/FY2025-26` →
  Q4 FY26, `H1 FY26` → H1 FY26).
- `event_rule` — concalls and decks are labelled by the month of the event, not the period discussed, so
  they get the latest quarter that ended before that month (Aug 2026 → Q1 FY27 → 2027); for NSE SME
  companies, which file half-yearly, the latest half-year (C2C Aug 2026 → H2 FY26 → 2026).
- `override` — `data/period_overrides.csv`, where the document itself states a different period.

Checked against the documents (`uv run cap-slice-periods` → `review/periods/`): the first 10 pages of all
228 documents were searched for the period they state ("Q1 FY27", "quarter ended June 30, 2026", "H1 FY26",
"Annual Report 2018-19"). 173 state exactly the normalised period, 5 the same fiscal year, 48 state none
(38 general corporate decks, 8 investor-day / broker-conference calls — the event rule stays), 3 disagree:
APAR's Jul-2020 call is on Q4 FY20 (COVID-delayed results) and Esconet's Aug-2026 call on Q1 FY27 (an SME
company now holding quarterly calls) — both overridden; E2E's FY2021-22 report was flagged only because the
parser misread its image-only cover ("ANNUAL REPORT 2022" as "2022-23"; the body says year ended March 2022
132 times) — no override.

Left out for now: standalone vs consolidated and units — users ask about them, but there is no reliable
source yet, and a wrong label used as a filter makes the right page unreachable. Revisit after round 2.
At the full 11–14M pages (~40M chunks, ~160 GB of float vectors) this needs a Qdrant server, payload
indexes and quantised vectors; the field names carry over.

### Filters (agreed 2026-10-19)

A filter narrows the pool before ranking (R002: 40,593 chunks → APAR 16,975 → APAR FY2018-19 report 921).
Fewer look-alike pages compete, but a wrong filter makes the answer unreachable. Every filter production
will use is tested — what matters is **where the filter's value comes from**:

| Setup | Filter values come from | Role |
|---|---|---|
| No filter | — | the retriever on its own |
| **Question-based** | a query reader that sees **only the question text** and outputs `symbol`, `fiscal_year`, `doc_type` (or nothing when the question doesn't say — 13 questions name no period) | **the production number; decisions use this** |
| Answer-key | the gold page's metadata | upper bound only, never quoted as a result; the gap to question-based is what the query reader costs |

Each filtered setup in two variants:
- **Hard** — search only inside the filtered pool. Best when the query reader is right; a wrong filter means no chance.
- **Soft** — search everything, rank chunks matching the filter higher. Safer when the reader is wrong; smaller gain when it's right.

Reported every round: no filter; company only (hard, soft); company + year + doc type, question-based
(hard, soft); the same from the answer key (hard, soft). The existing BM25 company filter reads `symbol`
from the answer key, which equals what a query reader gets because all 200 questions name the company.
Hard cases the query reader must handle: fiscal vs calendar periods ("quarter ended December 2023" = Q3
FY24), event-dated decks (R015 "six months to September 2023" → `Oct-2023` deck), and answers repeated in
the next year's comparative column (R002).

**Images: how the choice is made.** Each question records its evidence kind, so the chart, KPI-tile and
scanned-page questions form their own strata. B or C is adopted only if it lifts those strata without
lowering the text and table strata (generated text adds noise that can push wrong chunks up). Generated
summaries and chart-estimated values are stored with a `generated` flag so the answering step never
quotes them as printed figures — the number-fidelity check showed MinerU invents chart values.

**After retrieval:** answer accuracy (does the final answer quote the right value) on the same
questions, once an answering step exists.

### The question set (step 4)

`data/golden/retrieval_questions.csv` — 200 questions, built 2026-10-17 by the same rule as the golden
facts: **every answer is read off a rendered page image, never from parser output.** The same number is
often printed in several places (next year's comparative column, the results PDF, repeated slides), so
each question has a **strict** answer-page list (checked on the image) and a **lenient** one that adds
pages found by searching the text layers for the answer's distinctive numbers
(`retrieval_answer_pages_auto.csv`, not individually checked; 6 of 8 in a spot check answered). Report
retrieval at both levels.

Targets were: statement tables 45, other tables 25, charts 25, slide KPI tiles 15, annual-report prose 30,
concall Q&A 35, scanned pages 10, multi-page 15. **Built:** statement 25 + other tables 63, prose 33,
concall 33, charts 15, KPI tiles 6, scanned 10, multi-page 15 — tables over and charts/KPIs under, because
pages were taken in seeded random order rather than hand-picked. Wording: 140 paraphrased, 25 in the
document's own terms, 20 vague, 15 analytical. Built to be hard: periods in a different form than printed
(quarter ended December 2023 vs Q3 FY24), standalone vs consolidated, units (crore vs lakh vs million vs
full rupees), footnote-dependent answers, guidance that changes between calls, and metrics that recur
across years so near-duplicate pages compete. All five companies, FY2011-12 to Q1 FY27. Details in
`data/golden/README.md`.

## Before renting the GPU

- **Model confirmed (2026-10-03):** [`opendatalab/MinerU2.5-Pro-2604-1.2B`](https://huggingface.co/opendatalab/MinerU2.5-Pro-2604-1.2B) — 1.2B parameters, same Qwen2-VL-based architecture as MinerU2.5, retrained on 65.5M pages (arXiv 2604.04771, April 2026). OmniDocBench v1.6 overall 95.69 (MinerU2.5: 92.98). Published speed: **2.12 pages/s on one A100** with vLLM. MinerU needs ≥ 8 GB VRAM, Volta or newer.
- **Licence (checked 2026-10-03):** weights Apache 2.0; code under the [MinerU Open Source License](https://github.com/opendatalab/MinerU/blob/master/LICENSE.md) = Apache 2.0 plus: a separate commercial licence above 100M monthly active users or USD 20M monthly revenue, and visible attribution if offered as an online service to third parties.
- **Scale arithmetic:** 200k–250k documents × ~57 pages (pilot average) ≈ **11–14M pages**. At MinerU's published 2.12 pages/s that is ~1,500–1,900 A100-hours if every page goes through the VLM — so GPU cost per page, and routing only hard pages to the VLM, decide the budget.
- **Cost and time:** both parsers should be much faster on an A100 than on this laptop, but that's unmeasured. Benchmark a few hundred pages in the first hour, then decide whether to run everything.
- **Done 2026-10-03:** v2 scorer (`cap-slice-score`), batch runner, MinerU + Docling adapters, two Docker images, session scripts, runbook.
- **GPU choice (2026-10-03):** RTX 5090 at $0.99/h; A40 ($0.53/h) if the 5090 fails the smoke test. The benchmark's measured $ per 1,000 pages decides the GPU for the 11–14M-page run.
- **MinerU version:** MinerU 4.0.10 ships `MinerU2.5-Pro-2605-1.2B` (May 2026), a newer checkpoint than the `2604` above; that is what runs. MinerU 4 is a hybrid: tier `standard` uses small models + native PDF text and calls the VLM where needed; `advanced` lets the VLM do layout too.
