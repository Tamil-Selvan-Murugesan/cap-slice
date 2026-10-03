"""Option 2: PyMuPDF4LLM in layout mode -> Markdown per page.

Layout mode (pymupdf-layout, an ONNX model) classifies page regions; tables
come out as Markdown tables. Pages without a text layer are OCR'd with
RapidOCR. No PyTorch needed.

GPU (``CAP_SLICE_DEVICE=cuda``): both ONNX parts run on CUDA through
onnxruntime-gpu — the layout model is rebuilt with ``use_gpu=True`` (pymupdf's
default activation uses the CPU), and the RapidOCR engine PyMuPDF4LLM uses is
pre-created with CUDA enabled and cuDNN algorithm search ``DEFAULT`` (RapidOCR's
EXHAUSTIVE default re-tunes for every image shape; see bugs_resolved.md I12).
Which RapidOCR package runs depends on what's installed: PyMuPDF4LLM prefers
``rapidocr`` (3.x, PP-OCRv6) over ``rapidocr_onnxruntime`` (bugs_resolved.md P6).
"""

from __future__ import annotations

import os
import sys
from functools import cache
from pathlib import Path

import pymupdf4llm

from cap_slice.parsing import ParsedPage, ParseOutput


@cache
def _configure(device: str) -> dict:
    """Point PyMuPDF4LLM's ONNX models at the GPU once per process."""
    info = {"device": device, "layout_gpu": False, "ocr_gpu": False}
    if device == "cpu":
        return info
    # onnxruntime-gpu (CUDA 13 build) can't find libcublasLt.so.13 & co on its own; they ship
    # with torch's nvidia-* wheels, and importing torch loads them into the process first
    # (Docling imports torch anyway, PyMuPDF4LLM doesn't). bugs_resolved.md I14.
    try:
        import torch  # noqa: F401
    except ImportError:
        pass
    if not _ort_cuda_works():
        print("WARNING: onnxruntime can't use CUDA here; PyMuPDF4LLM stays on CPU", file=sys.stderr)
        return info
    import pymupdf
    from pymupdf.layout import DocumentLayoutAnalyzer

    model = DocumentLayoutAnalyzer.get_model(use_gpu=True)
    pymupdf._get_layout = lambda *a, **k: model.predict(*a, **k)
    info["layout_gpu"] = True
    try:
        from rapidocr import RapidOCR
        import pymupdf4llm.ocr.rapidocr_391_backend as backend

        backend.ENGINE = RapidOCR(params={
            "EngineConfig.onnxruntime.use_cuda": True,
            "EngineConfig.onnxruntime.cuda_ep_cfg.cudnn_conv_algo_search":
                os.environ.get("CAP_SLICE_OCR_ALGO_SEARCH", "DEFAULT"),
        })
        info["ocr_gpu"] = True
    except ImportError:  # only rapidocr_onnxruntime installed: OCR stays on CPU
        pass
    return info


def _ort_cuda_works() -> bool:
    """Open a real ONNX session on CUDA: the provider list alone says nothing (I12)."""
    import onnxruntime as ort
    try:
        import rapidocr
        model = Path(rapidocr.__file__).parent / "models" / "PP-OCRv6_det_small.onnx"
    except ImportError:
        return False
    if not model.exists():
        return False
    s = ort.InferenceSession(str(model), providers=["CUDAExecutionProvider", "CPUExecutionProvider"])
    return s.get_providers()[0] == "CUDAExecutionProvider"


def parse_full(path: Path) -> ParseOutput:
    info = _configure(os.environ.get("CAP_SLICE_DEVICE", "cpu"))
    chunks = pymupdf4llm.to_markdown(
        str(path), page_chunks=True, header=False, footer=False,
        use_ocr=True, show_progress=False,
    )
    pages = [ParsedPage(c["metadata"]["page_number"], c["text"].strip()) for c in chunks]
    return ParseOutput(pages, info=dict(info))


def parse(path: Path) -> list[ParsedPage]:
    return parse_full(path).pages
