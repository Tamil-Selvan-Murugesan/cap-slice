"""Option 5: PaddleOCR-VL-1.6 (full pipeline: PP-DocLayout layout model + 0.9B VLM) -> Markdown per page.

Every page goes through vision ("full vision", the co-founder's choice; branch main-sirisha,
vlm_bench/notes.md section 5). The layout model runs in this process on the GPU (PaddlePaddle); each
detected region is sent to the VLM on a vLLM server (``tools/gpu/session.sh paddle-server``). Settings
are the ones that run used (vlm_bench/run_paddle.py), so results are comparable:

  pipeline_version="v1.6", use_chart_recognition=True (charts -> tables), use_ocr_for_image_block=True
  (text inside pictures), footers / footer images / page numbers left out of the Markdown, pages
  rendered at 200 DPI, up to CAP_SLICE_PADDLE_CONCURRENCY (64) region requests in flight per process.

Environment:
  CAP_SLICE_PADDLE_SERVER       vLLM server (default http://127.0.0.1:8118/v1)
  CAP_SLICE_PADDLE_CONCURRENCY  region requests in flight per process (default 64)
  CAP_SLICE_PADDLE_DPI          page render resolution (default 200)

Saved raw file: ``paddleocr_vl.json`` — Paddle's per-page result (every block with its label and box,
including the footers left out of the Markdown). HTML tables are converted to pipe tables like MinerU's.
Known risk (their notes): no repetition guard in the VLM — ~1 % of pages can loop; detect afterwards.
Runs only in the ``paddle`` env (tools/gpu/setup_paddleocr_vl.sh).
"""

from __future__ import annotations

import json
import os
import re
import tempfile
from functools import cache
from pathlib import Path

from cap_slice.parsing import ParsedPage, ParseOutput

MD_IGNORE = ["footer", "footer_image", "number"]
# picture placeholders in Paddle's Markdown (<div ...><img src="imgs/..."></div>): no text, chunker noise
IMG = re.compile(r'<div[^>]*>\s*<img\b[^>]*>\s*</div>|<img\b[^>]*>', re.I)


def _settings() -> tuple[str, int, int]:
    return (os.environ.get("CAP_SLICE_PADDLE_SERVER", "http://127.0.0.1:8118/v1"),
            int(os.environ.get("CAP_SLICE_PADDLE_CONCURRENCY", "64")),
            int(os.environ.get("CAP_SLICE_PADDLE_DPI", "200")))


@cache
def _pipeline(server: str, concurrency: int):
    from paddleocr import PaddleOCRVL
    return PaddleOCRVL(pipeline_version="v1.6", vl_rec_backend="vllm-server", vl_rec_server_url=server,
                       vl_rec_max_concurrency=concurrency, use_chart_recognition=True,
                       use_ocr_for_image_block=True, markdown_ignore_labels=MD_IGNORE, use_queues=True)


def _markdown(res) -> str:
    md = res.markdown or {}
    text = md.get("markdown_texts", "")
    return "\n\n".join(text) if isinstance(text, list) else (text or "")


def _input_path(res) -> str:
    j = res.json or {}
    return (j.get("res", j) or {}).get("input_path", "")


def parse_full(path: Path) -> ParseOutput:
    import pymupdf
    from cap_slice.parsing.mineru_vlm import to_pipe_tables
    server, concurrency, dpi = _settings()
    with tempfile.TemporaryDirectory(prefix="paddle_") as td:
        images: dict[str, int] = {}
        with pymupdf.open(path) as doc:
            for i, page in enumerate(doc, 1):
                img = os.path.join(td, f"p{i:04d}.png")
                page.get_pixmap(dpi=dpi).save(img)
                images[img] = i
        by_page: dict[int, tuple[str, dict]] = {}
        for res in _pipeline(server, concurrency).predict_iter(list(images)):
            ip = _input_path(res)
            n = images.get(ip) or images[os.path.join(td, os.path.basename(ip))]
            by_page[n] = (_markdown(res), res.json)
    missing = sorted(set(images.values()) - set(by_page))
    if missing:
        raise RuntimeError(f"PaddleOCR-VL returned no result for pages {missing[:10]}")
    pages = [ParsedPage(n, to_pipe_tables(IMG.sub('', by_page[n][0])).strip()) for n in sorted(by_page)]
    raw = json.dumps([{"page": n, "result": by_page[n][1]} for n in sorted(by_page)],
                     ensure_ascii=False, default=str)
    return ParseOutput(pages, raw={"paddleocr_vl.json": raw},
                       info={"model": "PaddleOCR-VL-1.6-0.9B", "pipeline_version": "v1.6",
                             "server": server, "concurrency": concurrency, "dpi": dpi,
                             "chart_recognition": True, "ocr_for_image_block": True,
                             "md_ignore": MD_IGNORE})


def parse(path: Path) -> list[ParsedPage]:
    return parse_full(path).pages
