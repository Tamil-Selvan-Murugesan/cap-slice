# Explainer video: PyMuPDF4LLM vs Docling

Output: [`docs/media/pymupdf4llm-vs-docling.mp4`](../../docs/media/pymupdf4llm-vs-docling.mp4) — 2 min 52 s, 1280×720, 12 fps, ~1.2 MB. Companion to [`docs/pdf-parsers-pymupdf4llm-vs-docling.md`](../../docs/pdf-parsers-pymupdf4llm-vs-docling.md).

It follows one page — E2E FY2022-23 annual report, PDF page 123, a scanned balance sheet — through each parser step by step. **Every box and Markdown line on screen is real parser output** extracted from that page, not a mock-up.

## Rebuild

```bash
W=/tmp/explainer-video            # any scratch folder
uv run python tools/explainer_video/extract.py $W          # ~1 min: runs both parsers on the page
ELEVENLABS_API_KEY=... python3 tools/explainer_video/tts.py $W/audio   # optional narration
uv run python tools/explainer_video/render.py $W docs/media/pymupdf4llm-vs-docling.mp4   # ~30 s
```

| File | What it does |
|---|---|
| `extract.py` | Renders the page and records: text-layer size, PyMuPDF4LLM's OCR decision, RapidOCR line boxes, PyMuPDF4LLM layout boxes and Markdown, Docling layout regions, OCR'd cells, TableFormer grid and Markdown → `data.json` + `page.png` |
| `script.json` | Narration, one entry per scene (also used as on-screen captions) |
| `tts.py` | Optional: one ElevenLabs clip per scene. Key read from the environment only; never stored |
| `render.py` | Draws each frame with Pillow and pipes it straight into ffmpeg (H.264, CRF 30). With narration clips present, scenes are timed to the audio and it's muxed in; otherwise scenes are timed to reading speed and the video is captions-only |

Notes:
- `extract.py` forces PyMuPDF4LLM onto `rapidocr_onnxruntime` (the OCR package our measured Option 2 run used), then restores `rapidocr` for Docling, which needs it (`bugs_resolved.md` P6).
- Current video has **no narration**: the ElevenLabs request returned HTTP 402 (Payment Required) on 2026-10-02. Generate the clips into `$W/audio/` and re-run `render.py` to add it — no other change needed.
