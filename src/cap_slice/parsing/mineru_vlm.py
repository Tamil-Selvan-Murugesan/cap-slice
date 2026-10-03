"""Option 4: MinerU 4 with the MinerU2.5-Pro VLM -> Markdown per page (plus raw JSON).

MinerU 4 is a hybrid parser; its *tier* decides how much the VLM does:
  basic     small ONNX models only (no VLM)
  standard  small layout model + native PDF text where usable + MinerU2.5-Pro for the rest
  advanced  MinerU2.5-Pro also does the layout — closest to "the VLM parses everything"
The VLM itself (``opendatalab/MinerU2.5-Pro-2605-1.2B`` in MinerU 4.0.10) runs in a
separate server started with ``mineru-kit vlm-server`` (vLLM on a GPU, llama.cpp
on CPU); this adapter talks to it over HTTP, so several documents can be in
flight at once (``cap-slice-parse --workers N``) and vLLM batches them.

Environment:
  CAP_SLICE_MINERU_TIER   standard (default) | advanced | basic
  CAP_SLICE_MINERU_SERVER VLM server URL (default http://127.0.0.1:30000)
  MINERU_HOME             where MinerU keeps its small models and config

Saved raw files: ``mineru_middle.json`` (MinerU's lossless output: every block
with its type, page and box; tables as HTML) and ``mineru.md`` (whole document). Per-page text is rendered page by page with MinerU's
own Markdown renderer; HTML tables are converted to pipe tables
(html_table.py) so the shared chunker treats them like every other parser's tables.
"""

from __future__ import annotations

import copy
import json
import os
import re
from pathlib import Path

from cap_slice.parsing import ParsedPage, ParseOutput
from cap_slice.parsing.html_table import html_table_to_markdown

TABLE = re.compile(r"<table\b.*?</table>", re.S | re.I)
INLINE_TAGS = re.compile(r"</?(strong|em|b|i|u|sup|sub|span)\b[^>]*>", re.I)


def _settings() -> tuple[str, str]:
    return (os.environ.get("CAP_SLICE_MINERU_TIER", "standard"),
            os.environ.get("CAP_SLICE_MINERU_SERVER", "http://127.0.0.1:30000"))


def _page_markdown(middle: dict, page: dict) -> str:
    """Render one page with MinerU's renderer by giving it a one-page document."""
    from mineru.parser.base import ParseResult

    one = copy.deepcopy({k: v for k, v in middle.items() if k != "pages"})
    one["pages"] = [page]
    layout = one.get("extensions", {}).get("docvortex_layout")
    if layout and "pages" in layout:
        layout["pages"] = [p for p in layout["pages"] if p.get("page_idx") == page["page_idx"]]
    return ParseResult.from_dict(one).markdown()


def to_pipe_tables(md: str) -> str:
    """Replace every HTML table with a Markdown pipe table, on its own lines."""
    md = TABLE.sub(lambda m: "\n\n" + html_table_to_markdown(m.group(0)) + "\n\n", md)
    md = INLINE_TAGS.sub("", md)
    return re.sub(r"\n{3,}", "\n\n", md).strip()


def pages_from_middle(middle: dict) -> list[ParsedPage]:
    return [ParsedPage(p["page_idx"] + 1, to_pipe_tables(_page_markdown(middle, p)))
            for p in sorted(middle["pages"], key=lambda p: p["page_idx"])]


def parse_full(path: Path) -> ParseOutput:
    from mineru.config import VlmConfig
    from mineru.parser.mineru_parser import MinerUParser

    tier, server = _settings()
    parser = MinerUParser(tier=tier, vlm_config=VlmConfig(server_url=server))
    result = parser.parse(path)
    middle = result.to_dict()
    # middle JSON is MinerU's lossless output. structured_content() is not saved:
    # it embeds page images as base64 (~1 MB per 4 pages, ~3 GB for the collection).
    raw = {"mineru_middle.json": json.dumps(middle), "mineru.md": result.markdown()}
    return ParseOutput(pages_from_middle(middle), raw=raw,
                       info={"tier": tier, "server": server,
                             "mineru_tier_used": middle.get("extensions", {}).get("mineru", {})})
