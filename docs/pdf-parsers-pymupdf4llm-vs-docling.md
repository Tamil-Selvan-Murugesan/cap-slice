# PyMuPDF4LLM vs Docling — what they do, which models they run, how they OCR

A plain-language guide to the two "layout-aware" PDF parsers we tested (Options 2 and 3 in `review/README.md`). Written 2026-10-02.

**Video walkthrough:** [`docs/media/pymupdf4llm-vs-docling.mp4`](media/pymupdf4llm-vs-docling.mp4) (3 min, captions) follows one scanned balance-sheet page through both parsers step by step, using their real outputs. How it's made: `tools/explainer_video/README.md`.

**Sources.** Unless marked otherwise, facts below were checked in the installed packages (`pymupdf4llm` 1.28.2, `pymupdf-layout` 1.28.2, `docling` 2.130.0, `docling-core` 2.99.0, `docling-ibm-models` 4.0.3, `rapidocr` 3.9.2, `rapidocr_onnxruntime` 1.4.4) and in the model files and model cards downloaded to this machine. Performance numbers are **our own measurements** on the golden set (5 documents, 375 pages, 28 facts) on this laptop (Core Ultra 5 135U, CPU only). Anything not verified is labelled *(unverified)*.

---

## 1. TL;DR

| | **PyMuPDF4LLM** (Option 2) | **Docling** (Option 3) |
|---|---|---|
| Who makes it | Artifex (the makers of MuPDF/PyMuPDF) | IBM Research, now the `docling-project` open-source project |
| Core idea | Start from the PDF's own text and boxes, then use **small models** to label them and find tables | Render each page as an **image** and run **large vision models** over it, then merge with the PDF's text |
| Layout model | `BoxRFDGNN` — a graph neural network over text boxes, ONNX, a few MB | `docling-layout-heron` — an **RT-DETRv2** object detector, PyTorch, 164 MB |
| Table structure | `table_grid_model_v4` (ONNX, ~4 MB) + rules | **TableFormer** — a transformer, PyTorch, 203 MB (accurate) / 139 MB (fast) |
| OCR engine | RapidOCR (PaddleOCR models via ONNX) | RapidOCR too (picked automatically on Linux) |
| When it OCRs | A small ONNX **"does this page need OCR?"** model, page by page | On layout regions **not already covered by PDF text** (e.g. text inside images) |
| Runtime | ONNX Runtime only — no PyTorch | PyTorch (+ ONNX Runtime for OCR) |
| Install size here | ~120 MB + ~220 MB for OCR | ~2 GB (CPU PyTorch + libs) + ~0.5 GB models |
| **Our accuracy** (28 facts fully intact) | 21 | **27** |
| **Our speed** (375 pages) | **21 min (3.3 s/page)** | 95 min (15.2 s/page) |
| Scanned financial tables | Reads text, loses columns (0/6 intact) | Rebuilds the table (5/6 intact) |

**In one line:** PyMuPDF4LLM is a fast "text first" parser that does well on digital PDFs; Docling is a slow "vision first" parser that understands page structure — especially tables and scanned pages — much better.

---

## 2. Background: why PDFs are hard

A PDF is a set of **drawing instructions**, not a document: "draw these characters at these coordinates", "draw this image here", "draw a line from A to B". It has no notion of *paragraph*, *heading*, *table* or *column*. Every parser has to rebuild that structure.

Two very different kinds of PDF page:

| Page type | What's inside | How you get text |
|---|---|---|
| **Digital** (born from Word, LaTeX, accounting software) | A **text layer**: real characters with positions | Read it directly — fast and exact |
| **Scanned / image-only** (printed and scanned, or exported as pictures, or designed slides) | Just a **picture** of the page; no characters | **OCR**: detect and recognise text in the image — slow and error-prone |

Many filings mix both: E2E's FY2022-23 annual report is digital except its financial statements (pages 123–164), which are scanned images. Our golden set has 17% such pages; the whole collection has 3.4%.

The hard parts, roughly in order: (1) **tables** — rows, columns, merged header cells; (2) **reading order** — multi-column pages, sidebars; (3) **scanned pages** — OCR, then the tables inside them; (4) **noise** — page headers, footers, letterheads, watermarks.

---

## 3. PyMuPDF (the base both of our fast options use)

**PyMuPDF** is the Python binding for **MuPDF**, a fast C library for rendering and reading PDFs. It can give you:
- the text layer, as characters/words/lines/blocks with exact positions and font information (`page.get_text(...)`);
- images of pages (`page.get_pixmap()`);
- drawings (lines, rectangles) — which is how ruled tables can be found.

It has **no machine learning**. It reads what the PDF contains, and that's all. Our baseline and Option 1 use it directly (0.02 s/page).

---

## 4. PyMuPDF4LLM (Option 2)

**What it is:** an add-on to PyMuPDF that turns a PDF into **Markdown** (headings, lists, tables, bold/italic) intended for LLMs and RAG. Call: `pymupdf4llm.to_markdown(path, page_chunks=True, ...)`.

### 4.1 Pipeline, page by page

```
PDF page
  │
  ├─► 1. Read the text layer with MuPDF (characters + boxes + fonts)
  │
  ├─► 2. OCR decision: does this page need OCR?  ── yes ─► 3. OCR with RapidOCR
  │        (rules + a tiny ONNX classifier)                (adds text boxes to the page)
  │
  ├─► 4. Layout analysis with pymupdf-layout:
  │        label every text box (title, text, table, page-header, ...)
  │        and find table grids
  │
  └─► 5. Write Markdown: headings (#), paragraphs, lists, tables (| a | b |)
         (page headers/footers dropped when header=False/footer=False)
```

When `pymupdf-layout` is installed, PyMuPDF4LLM uses it automatically ("layout mode"); without it, it falls back to older rule-based logic based on font sizes.

### 4.2 The models

All of them run on **ONNX Runtime** (a lightweight engine for running exported neural networks on CPU). No PyTorch.

| Model | File (installed) | Size | What it does |
|---|---|---|---|
| **Layout model `BoxRFDGNN`** | `pymupdf/layout/resources/onnx/layout_rf2.4.1+imf1.onnx` | 8.2 MB | Classifies each text box into one of 11 classes: text, title, picture, table, list-item, page-header, page-footer, section-header, footnote, caption, formula |
| Image feature extractor | `feature_imf1.onnx` / `feature_imf2.onnx` | 1.3 MB each | Small CNN over the rendered page image; its features are pooled per box and fed to the layout model |
| **Table grid model** | `table_grid_model_v4.onnx` (default `V4`) | 3.7 MB | Finds the row/column grid inside a detected table |
| **OCR decision model** | `pymupdf4llm/ocr/ocr_decision_model.onnx` | 0.5 MB | Predicts the probability that a page needs OCR |

**How `BoxRFDGNN` works** (from its code and parameter names; the internals aren't documented, so this is our reading): every text box on the page becomes a **node in a graph**; nearby boxes are connected by **edges**. Each node gets features from the PDF itself (position, size, font, text) — the "RF" features — plus image features cropped from the page picture ("IMF", via ROI pooling). A **graph neural network** passes information between neighbouring boxes and then labels each box. The "D" likely stands for *dynamic* (graph rebuilt from the boxes on each page) *(unverified)*.

The key consequence: **it starts from text boxes the PDF already has.** If a page has no text layer, there is nothing to label until OCR has produced boxes.

### 4.3 OCR in PyMuPDF4LLM

**Step 1 — decide.** `pymupdf4llm/ocr/analyze_page.py` decides per page:
- if the page already has an OCR text layer (from an earlier OCR), keep it;
- if ≥ 10% of the characters are "bad" (unrecognisable glyphs), recommend OCR;
- otherwise compute features — including **Sobel edge statistics** of the rendered page (edges suggest text drawn as pixels) — and ask the **OCR decision model**; OCR if its probability ≥ **0.93**.

**Step 2 — OCR.** The page is rendered at `ocr_dpi` (default **150 dpi**) and passed to **RapidOCR**. Which RapidOCR package it uses depends on what is installed: it prefers `rapidocr` (v3.x) and falls back to `rapidocr_onnxruntime` (v1.4). Our measured Option 2 run used `rapidocr_onnxruntime` with PP-OCRv4 models; installing Docling later added `rapidocr` 3.9, which would silently switch a re-run to PP-OCRv6 models (`bugs_resolved.md` P6).

**Step 3 — merge.** Recognised text lines become text boxes on the page, and the normal layout/table/Markdown steps run over them.

### 4.4 Output quirks we saw
- Tables as `|`-pipe Markdown with a `|---|` header separator. Multi-line cells joined with `<br>`.
- **`~~text~~` strikethrough** where MuPDF flags characters as struck out. On our scanned statements, table rules crossing OCR'd numbers appear to trigger this (`2,294~~.~~41`) — our chunker strips it (`bugs_resolved.md` S7).
- `<mark>`, `<u>`, `<sup>` tags for highlights, underlines, superscripts.

### 4.5 What we observed
| Document type | Result |
|---|---|
| Digital financial tables | **8/8** facts with the correct year column |
| Scanned financial statements | Text recovered on all 52 pages, but **0/6** facts intact: spaces dropped (`BalanceSheetasatMarch31,2023`), some `,` read as `.`, and **both year columns merged into one cell** (`1,631.31 384.34`) by the table-grid step |
| Image-only slides | Read correctly (2/2) |
| Speed | 1.2 s/page on a digital report; 5.8 s/page on the report with scanned pages; 3.3 s/page overall |

Why scanned tables fail: **not because of OCR.** On the cash row, RapidOCR read both values correctly as separate boxes (`1,631.31` at x 439–475 pt and `384.34` at x 547–576 pt, confidence 0.999 and 1.0). The failure is in the **table-grid step**: it decided this table has 3 columns (label | notes | values) and stacked both years' values into the last one, joined with `<br>`. So the problem is *finding the columns* from scattered OCR boxes, not reading the text. *(Checked 2026-10-02 by extracting the OCR boxes and layout boxes for page 123 — `tools/explainer_video/extract.py`.)*

---

## 5. Docling (Option 3)

**What it is:** an open-source document conversion toolkit started by IBM Research (Zurich), now under the `docling-project` organisation. It converts PDF, DOCX, PPTX, HTML, images and more into a structured **`DoclingDocument`**, which can be exported to Markdown, JSON or HTML. Call: `DocumentConverter().convert(path).document.export_to_markdown()`.

### 5.1 Pipeline, page by page (the standard PDF pipeline)

```
PDF page
  │
  ├─► 1. PDF backend (docling-parse): read text "cells" with positions,
  │      plus bitmap and vector-graphics regions
  │
  ├─► 2. Render the page to an image
  │
  ├─► 3. Layout model (Heron, RT-DETRv2): draw boxes around regions
  │      and label them (17 classes: table, text, section-header, picture, ...)
  │
  ├─► 4. OCR (RapidOCR) — only on layout regions NOT already covered by PDF text
  │
  ├─► 5. TableFormer on every "table" region: predict rows, columns,
  │      header cells, merged cells; fill cells with PDF text or OCR text
  │
  ├─► 6. Assemble: reading order, captions, headers/footers marked as "furniture"
  │
  └─► 7. DoclingDocument  ──►  Markdown export (we export one page at a time)
```

Defaults we used (checked on the installed version): backend `ThreadedDoclingParseDocumentBackend`; OCR **on**, engine **auto**, mode **DEFAULT**; table structure **on**, mode **ACCURATE**, cell matching **on**; 4 CPU threads.

### 5.2 The models

All run on **PyTorch** except OCR (ONNX Runtime). Downloaded from Hugging Face on first use into `~/.cache/huggingface` (~0.5 GB here).

| Model | Where | Size | What it does |
|---|---|---|---|
| **Layout: `docling-layout-heron`** | `docling-project/docling-layout-heron` | 164 MB | **RT-DETRv2** object detector (a transformer-based detector, `RTDetrV2ForObjectDetection`). Draws boxes and labels 17 classes: caption, footnote, formula, list-item, page-footer, page-header, picture, section-header, table, text, title, document-index, code, checkbox-selected/unselected, form, key-value region. Described in the paper "Advanced Layout Analysis Models for Docling" (Livathinos et al., arXiv 2509.11720) |
| **TableFormer (accurate)** | `docling-project/docling-models` → `tableformer/accurate` | 203 MB | Transformer that looks at the **image of a table** and predicts its structure as a sequence of tags (rows, cells, spans) plus a box per cell (Nassar et al., "TableFormer: Table Structure Understanding With Transformers", CVPR 2022). The model card reports a TEDS score of 93.6 vs 73.0 for Camelot *(their benchmark, not ours)* |
| TableFormer (fast) | `tableformer/fast` | 139 MB | Smaller variant, quicker, somewhat less accurate *(trade-off not measured by us)* |
| **OCR** | RapidOCR, bundled in the `rapidocr` package | ~32 MB | See 5.3 |

### 5.3 OCR in Docling

**Engine selection ("auto").** On Linux, Docling tries engines in order and uses the first that works; here it picked **RapidOCR with ONNX Runtime** (our run's logs show RapidOCR starting with `engine_name: onnxruntime` and loading the PP-OCRv6 detection/recognition models). Other supported engines: EasyOCR, Tesseract, macOS Vision (on Macs), and remote/NVIDIA options.

**What gets OCR'd (mode DEFAULT = "PDF-aware layout regions").** Docling does *not* OCR the whole page by default. It takes the layout model's regions and OCRs a region only if it isn't already fully covered by real PDF text — e.g. text inside a picture, a scanned page, or a region overlapping a bitmap. Other modes: `LAYOUT_REGIONS` (OCR every detected region) and `FULL_PAGE` (OCR the whole page, ignoring the PDF text).

**A likely cause of slowness on some documents** *(our inference, not proven)*: the C2C letterhead pages have a large watermark **image** behind the text. Regions overlapping a bitmap qualify for OCR, so Docling probably OCRs most of each page even though the text layer is fine. That matches what we measured: OCR was about **two-thirds** of Docling's time on the 4-page C2C notice (53 s with OCR, 19 s without).

### 5.4 Why Docling reads scanned tables where PyMuPDF4LLM doesn't

Both use the **same OCR engine family** (RapidOCR). The difference is the **order of operations**:

| | PyMuPDF4LLM | Docling |
|---|---|---|
| Step 1 | OCR the page into **text boxes** (reads the numbers correctly) | Detect the **table region** in the image (layout model) |
| Step 2 | Guess the table grid from where those boxes fall — here it found 3 columns instead of 4 | Predict the **grid** from the table image (TableFormer) — 45 rows × 4 columns |
| Step 3 | — | Read text **per cell** (OCR / PDF text matched to each cell box) |
| Failure mode | Column guessing merges the two year columns into one cell, even though OCR read both numbers correctly | Grid is predicted first, so each year's number lands in its own cell |

On E2E's scanned balance sheet, Docling produced `| (ii) Cash and cash equivalents | 10 | 1,631.31 | 384.34 |` under `| | Notes | As at March 31, 2023 | As at March 31, 2022 |` — exactly the structure on the page. PyMuPDF4LLM produced `1,631.31<br>384.34` in a single cell.

Docling isn't perfect: it misread the double-underlined profit **990.99 as `6960969`** (F13) — the underline lines likely confused recognition.

### 5.5 What we observed
| Document type | Result |
|---|---|
| Digital financial tables | **8/8** with the correct year column (after fixing our chunker's caption bug, S8) — cleanest tables of all options, merged header cells handled |
| Scanned financial statements | **5/6** intact; 1 genuine OCR misread |
| Image-only slides | 2/2 |
| Table split across pages, wrapped names | 4/4 — the only option that kept "Pravan Holdings / LLP" as one row |
| Speed | 11.8 s/page digital report; 17.2 s/page with scans; **24.2 s/page on the presentation**; 15.2 s/page overall |
| Memory | Peak **6.1 GB**; +4.7 GB while parsing the first document (models loaded) |
| Quirk | Element order can differ from the page — it put the signature line between the "INR lakhs" line and the balance sheet, which broke our chunker's caption logic until S8 was fixed |

---

## 6. Head to head

| Question | PyMuPDF4LLM | Docling |
|---|---|---|
| Uses the PDF's real text when it exists? | Yes (its starting point) | Yes (matched into layout regions and table cells) |
| Needs the page image? | Only for small image features and OCR | Always (layout model runs on every page) |
| Finds tables by | Labelling text boxes + grid model + ruling lines | Detecting table regions in the image |
| Rebuilds table structure by | Grid model over text positions | TableFormer over the table image |
| Handles merged/multi-line header cells | Partly (`<br>` joins) | Yes (spans predicted) |
| OCR engine | RapidOCR | RapidOCR (auto) — EasyOCR/Tesseract optional |
| OCR trigger | Per-page classifier (≥ 0.93) | Per region, where PDF text is missing |
| Heavy dependency | No (ONNX Runtime) | Yes (PyTorch) |
| GPU support | Layout model has a `use_gpu` flag; OCR via ONNX Runtime GPU *(not tested)* | Yes — `device="cuda"` / Apple `mps` *(not tested)* |
| Output | Markdown string (per page) | `DoclingDocument` → Markdown / JSON / HTML |
| Best for | Digital filings, prose, speed | Tables, scanned pages, complex layouts |

---

## 7. Why they're slow on this laptop, and what helps

Almost all of the time in both is **neural-network inference**: layout detection, table structure and OCR (text detection + recognition). This laptop runs them on a 15 W mobile CPU, which also slows down when hot (the same Docling test measured 66 s and 104 s in two runs).

| Lever | Effect | Status |
|---|---|---|
| **Route pages** — fast parser for ordinary pages, Docling only for pages without text or with tables | Biggest win; only 3.4% of pages lack text | Proposed, not tested |
| **GPU** | Large speed-up expected — all three model types are GPU-friendly; Docling's own benchmarks report sub-second pages on GPU *(unverified here)* | Not tested |
| TableFormer `FAST` mode | Faster tables, some accuracy loss | Not tested |
| OCR off or narrower OCR mode | OCR was ~2/3 of Docling's time on the watermarked C2C pages | Not tested beyond that one document |
| More threads | **Slower** here (8 threads: 66 s vs 4 threads: 53 s) | Measured — keep defaults |
| Parse once, cache | Parsing happens once per document | Already done in our comparison runner |

---

## 8. Glossary

- **Text layer** — the real characters stored in a PDF. Digital PDFs have one; scans don't.
- **OCR (optical character recognition)** — turning pictures of text into characters. Modern OCR is usually three neural networks: **detection** (find text lines in the image), **direction classification** (is the line rotated/upside down?), **recognition** (read the characters in each line).
- **RapidOCR** — a packaging of Baidu's **PaddleOCR** models (PP-OCR) for ONNX Runtime. Models on this machine: `PP-OCRv6_det_small` (9.9 MB, detection), `ch_ppocr_mobile_v2.0_cls` (0.6 MB, direction), `PP-OCRv6_rec_small` (21 MB, recognition) in `rapidocr` 3.9; PP-OCRv4 equivalents in `rapidocr_onnxruntime` 1.4.
- **ONNX / ONNX Runtime** — a portable file format for trained neural networks and a lightweight engine to run them; no training framework needed.
- **PyTorch** — a full deep-learning framework; heavier to install, needed by Docling's layout and table models.
- **Layout analysis** — finding and labelling page regions (heading, paragraph, table, figure, header/footer).
- **RT-DETR** — "Real-Time DEtection TRansformer", an object-detection model family; Docling's Heron layout model is RT-DETRv2.
- **Graph neural network (GNN)** — a network that works on nodes connected by edges; PyMuPDF4LLM's layout model treats text boxes as nodes.
- **TableFormer** — IBM's transformer model that predicts a table's rows, columns and cell spans from an image of the table.
- **TEDS** — Tree-Edit-Distance-based Similarity, a standard score for how close a predicted table structure is to the true one.
- **DPI** — dots per inch; the resolution a page is rendered at before OCR (PyMuPDF4LLM default 150).

## 9. Where to look in this repo

- Our wrappers: `src/cap_slice/parsing/pymupdf4llm_md.py`, `src/cap_slice/parsing/docling_md.py`
- Raw output of each parser, page by page: `review/pymupdf4llm/<doc>/parsed.md`, `review/docling/<doc>/parsed.md` — compare page 123 of `e2e_ar_fy23` in both to see section 5.4 for yourself
- Scores and timings: `review/README.md`, `review/COMPARISON.md`
- Problems we hit with each: `bugs_resolved.md` (P5, P6, S7, S8)
