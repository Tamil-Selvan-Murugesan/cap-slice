"""Unlimited-OCR throughput + accuracy run (end-to-end model, no separate layout model).

Follows the official vLLM recipe (recipes.vllm.ai/baidu/Unlimited-OCR): literal <image>
prompt prefix, skip_special_tokens=False, n-gram logits processor args per request
(window 128 single page, 1024 multi-page), temperature 0.

Per page (single-page mode) it runs the same two passes as the reference notebook:
  1. "<image>document parsing."  -> typed blocks with boxes (title, text, table, image, ...)
  2. every 'image' block is cropped from the page and re-read with "<image>Free OCR.",
     because pass 1 does not transcribe text inside figures/charts. The recovered text
     is put back in place of the image block.
Both passes count towards the page's latency and the throughput numbers.

Outputs per page in <run>/md/:
  <page_id>.raw.md       pass-1 output exactly as returned
  <page_id>.blocks.json  parsed blocks: category, box (0-999), text, source
  <page_id>.md           markdown: headings as '#', page headers kept as
                         '<!-- header: ... -->', footers/page numbers dropped, tables as
                         returned (HTML), image text inline. Heading LEVELS are not
                         assigned here (that needs the whole document; done later).

Multi-page mode (--pages-per-request > 1) is for throughput only: no crop pass, output
saved per request as <first_page_id>.raw.md / .md.

  python run_unlimited.py --manifest pages/manifest.jsonl --warmup-manifest pages/warmup.jsonl --concurrency 64
  python run_unlimited.py --manifest pages/manifest.jsonl --concurrency 16 --pages-per-request 8
"""
import argparse
import asyncio
import base64
import io
import json
import re
import time
from collections import defaultdict
from pathlib import Path

from openai import AsyncOpenAI
from PIL import Image

from common import (GpuMonitor, Sampler, load_manifest, run_dir, scrape_counters,
                    write_summary)

PAGE_PROMPT = "<image>document parsing."
MULTI_PROMPT = "<image>Multi page parsing."
CROP_PROMPT = "<image>Free OCR."
COORD_SCALE = 999.0

# --------------------------------------------------------------------------- parsing
# Region tags seen in this model family's outputs:
#   <|det|>title [x0, y0, x1, y1]<|/det|>content          (model card)
#   <|ref|>title<|/ref|><|det|>[[x0, y0, x1, y1]]<|/det|>  (DeepSeek-OCR style)
#   title [x0, y0, x1, y1] content                        (reference notebook, tags stripped)
# Removing the tag tokens reduces all three to "category [box] content".
TAG = re.compile(r"<\|/?(?:ref|det)\|>")
SPECIAL = re.compile(r"<\|[^|>]*\|>")
BLOCK_START = re.compile(r"^\s*([A-Za-z_][A-Za-z_ ]*?)\s*(\[\[?[\d.,\s\[\]]+\]\]?)\s*(.*)$")
NUM = re.compile(r"[\d.]+")

DROP = {"footer", "page_number", "pagenumber", "page number", "page_footer", "page-footer"}
HEADER = {"header", "page_header", "page-header"}
IMAGE = {"image", "figure", "chart", "picture"}


def is_heading(cat: str) -> bool:
    return "title" in cat or "heading" in cat


def parse_blocks(raw: str) -> list[dict]:
    """Split model output into blocks. Lines that do not start a new block continue the
    previous one (multi-line text, HTML tables)."""
    text = SPECIAL.sub("", TAG.sub("", raw))
    blocks, cur = [], None
    for line in text.splitlines():
        m = BLOCK_START.match(line)
        if m:
            nums = [float(x) for x in NUM.findall(m.group(2))][:4]
            if len(nums) == 4:
                cur = {"category": m.group(1).strip().lower(), "box": nums,
                       "text": m.group(3).strip()}
                blocks.append(cur)
                continue
        if cur is None:
            if line.strip():
                cur = {"category": "text", "box": None, "text": line.strip()}
                blocks.append(cur)
            continue
        cur["text"] = (cur["text"] + "\n" + line.rstrip()).strip("\n")
    for b in blocks:
        b["text"] = b["text"].strip()
    return blocks


def blocks_to_markdown(blocks: list[dict]) -> str:
    out = []
    for b in blocks:
        cat, txt = b["category"], b["text"]
        if cat in DROP:
            continue
        if cat in HEADER:
            if txt:
                out.append(f"<!-- header: {' '.join(txt.split())} -->")
            continue
        if cat in IMAGE:
            rec = b.get("image_text", "")
            out.append(f"<!-- image text -->\n{rec}" if rec else "<!-- image -->")
            continue
        if not txt:
            continue
        out.append(f"# {' '.join(txt.split())}" if is_heading(cat) else txt)
    return "\n\n".join(out)


def crop_text(raw: str) -> str:
    """Text from a 'Free OCR.' crop response, whether it came back tagged or plain."""
    blocks = parse_blocks(raw)
    if blocks and any(b["box"] for b in blocks):
        return "\n".join(b["text"] for b in blocks if b["category"] not in DROP and b["text"])
    return SPECIAL.sub("", TAG.sub("", raw)).strip()


# --------------------------------------------------------------------------- requests
def image_part_path(path: str, transport: str) -> dict:
    if transport == "file":  # needs --allowed-local-media-path on the server; no base64 overhead
        url = f"file://{path}"
    else:
        url = "data:image/png;base64," + base64.b64encode(Path(path).read_bytes()).decode()
    return {"type": "image_url", "image_url": {"url": url}}


def image_part_pil(img: Image.Image) -> dict:
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return {"type": "image_url",
            "image_url": {"url": "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()}}


async def ask(client, a, prompt: str, images: list[dict], max_tokens: int, window: int):
    resp = await client.chat.completions.create(
        model=a.model_name,
        messages=[{"role": "user", "content": [{"type": "text", "text": prompt}] + images}],
        max_tokens=max_tokens, temperature=0.0,
        extra_body={"skip_special_tokens": False,
                    "vllm_xargs": {"ngram_size": 35, "window_size": window}})
    choice = resp.choices[0]
    return (choice.message.content or ""), choice.finish_reason, \
        (resp.usage.completion_tokens if resp.usage else 0)


def crops_for(page_path: str, blocks: list[dict], a) -> list[tuple[int, Image.Image]]:
    """Crop every image block from the exact page image that was sent (boxes are 0-999)."""
    todo = [(i, b) for i, b in enumerate(blocks) if b["category"] in IMAGE and b["box"]]
    if not todo:
        return []
    page = Image.open(page_path).convert("RGB")
    W, H = page.size
    out = []
    for i, b in todo:
        x0, y0, x1, y1 = b["box"]
        box = (max(0, round(x0 / COORD_SCALE * W)), max(0, round(y0 / COORD_SCALE * H)),
               min(W, round(x1 / COORD_SCALE * W)), min(H, round(y1 / COORD_SCALE * H)))
        if box[2] - box[0] < a.min_crop_px or box[3] - box[1] < a.min_crop_px:
            continue
        crop = page.crop(box)
        side = max(crop.size)
        if side < a.crop_pad_below:  # pad small crops to a square, as the notebook does
            sq = Image.new("RGB", (side, side), (255, 255, 255))
            sq.paste(crop, ((side - crop.width) // 2, (side - crop.height) // 2))
            crop = sq
        out.append((i, crop))
    return out


async def run_unit(client, sem, unit, a, md_dir, records):
    multi = len(unit) > 1
    async with sem:
        t0 = time.perf_counter()
        rec = {"unit_id": unit[0]["page_id"], "n_pages": len(unit),
               "page_ids": [r["page_id"] for r in unit]}
        try:
            images = [image_part_path(r["path"], a.image_transport) for r in unit]
            max_tokens = min(a.max_tokens_per_page * len(unit), a.max_tokens_cap)
            raw, finish, out_tok = await ask(client, a, MULTI_PROMPT if multi else PAGE_PROMPT,
                                             images, max_tokens, 1024 if multi else 128)
            rec.update(finish=finish, out_tokens=out_tok, empty=not raw.strip())
            blocks = parse_blocks(raw)
            rec["n_blocks"] = len(blocks)

            if not multi and a.crop_pass:
                crops = crops_for(unit[0]["path"], blocks, a)
                if crops:
                    results = await asyncio.gather(*(
                        ask(client, a, CROP_PROMPT, [image_part_pil(img)],
                            a.crop_max_tokens, 128) for _, img in crops),
                        return_exceptions=True)
                    n_ok = 0
                    for (i, _), res in zip(crops, results):
                        if isinstance(res, Exception):
                            blocks[i]["crop_error"] = repr(res)[:200]
                            continue
                        txt = crop_text(res[0])
                        rec["out_tokens"] += res[2]
                        if txt:
                            blocks[i]["image_text"] = txt
                            n_ok += 1
                    rec.update(n_crops=len(crops), n_crops_with_text=n_ok)
            rec["latency_s"] = time.perf_counter() - t0

            if md_dir:
                (md_dir / f"{rec['unit_id']}.raw.md").write_text(raw)
                (md_dir / f"{rec['unit_id']}.blocks.json").write_text(json.dumps(blocks, indent=1))
                (md_dir / f"{rec['unit_id']}.md").write_text(blocks_to_markdown(blocks))
                if not blocks and raw.strip():
                    rec["unparsed"] = True  # raw saved; check the output format
        except Exception as e:
            rec.update(latency_s=time.perf_counter() - t0, error=repr(e)[:300])
        records.append(rec)


def build_units(rows: list[dict], k: int) -> list[list[dict]]:
    """k=1: one page per request. k>1: consecutive pages of the same run (or PDF), chunked."""
    if k == 1:
        return [[r] for r in rows]
    groups = defaultdict(list)
    for r in rows:
        groups[r.get("run_id") or r["pdf"]].append(r)
    units = []
    for pages in groups.values():
        pages.sort(key=lambda r: r["page_no"])
        units += [pages[i:i + k] for i in range(0, len(pages), k)]
    return units


async def run_all(units, a, md_dir):
    # Close the client inside this event loop; otherwise it is garbage-collected after asyncio.run()
    # has closed the loop and prints a harmless "RuntimeError: Event loop is closed" traceback.
    async with AsyncOpenAI(base_url=a.server_url, api_key="EMPTY", timeout=3600,
                           max_retries=0) as client:
        sem = asyncio.Semaphore(a.concurrency)
        records: list[dict] = []
        await asyncio.gather(*(run_unit(client, sem, u, a, md_dir, records) for u in units))
    return records


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", required=True)
    ap.add_argument("--warmup-manifest", help="pages used only for warm-up (not measured)")
    ap.add_argument("--limit", type=int)
    ap.add_argument("--server-url", default="http://localhost:8000/v1")
    ap.add_argument("--model-name", default="unlimited-ocr")
    ap.add_argument("--concurrency", type=int, default=64, help="requests (units) in flight")
    ap.add_argument("--pages-per-request", type=int, default=1)
    ap.add_argument("--max-tokens-per-page", type=int, default=8192)
    ap.add_argument("--max-tokens-cap", type=int, default=24576,
                    help="cap for multi-page requests (model context is 32k incl. image tokens)")
    ap.add_argument("--no-crop-pass", dest="crop_pass", action="store_false",
                    help="skip re-reading image regions with 'Free OCR.'")
    ap.add_argument("--crop-max-tokens", type=int, default=2048)
    ap.add_argument("--min-crop-px", type=int, default=40)
    ap.add_argument("--crop-pad-below", type=int, default=1024)
    ap.add_argument("--image-transport", choices=["file", "base64"], default="file")
    ap.add_argument("--warmup", type=int, default=16)
    ap.add_argument("--results", default="results")
    ap.add_argument("--run-name")
    a = ap.parse_args()

    rows = load_manifest(a.manifest, a.limit)
    units = build_units(rows, a.pages_per_request)
    run_name = a.run_name or f"c{a.concurrency}_k{a.pages_per_request}"
    d = run_dir(a.results, "unlimited-ocr", run_name)
    metrics_url = a.server_url.rsplit("/v1", 1)[0] + "/metrics"

    warm_rows = load_manifest(a.warmup_manifest) if a.warmup_manifest else rows[:a.warmup]
    warm_units = build_units(warm_rows, a.pages_per_request)
    print(f"warmup: {len(warm_units)} units ({'separate pages' if a.warmup_manifest else 'first pages of the set'})")
    asyncio.run(run_all(warm_units, a, None))

    before = scrape_counters(metrics_url)
    with GpuMonitor(d / "gpu.csv"), Sampler(d / "server.jsonl", metrics_url) as smp:
        t0 = time.perf_counter()
        records = asyncio.run(run_all(units, a, d / "md"))
        wall = time.perf_counter() - t0
    after = scrape_counters(metrics_url)

    with open(d / "pages.jsonl", "w") as f:
        for r in records:
            f.write(json.dumps(r) + "\n")
    ok = [r for r in records if "error" not in r]
    empties = sum(1 for r in ok if r.get("empty"))
    unparsed = sum(1 for r in ok if r.get("unparsed"))
    truncated = sum(1 for r in ok if r.get("finish") == "length")
    if empties:
        print(f"WARNING: {empties} empty outputs - check prompt prefix / skip_special_tokens")
    if unparsed:
        print(f"WARNING: {unparsed} outputs had no recognisable blocks - inspect *.raw.md and "
              f"adjust BLOCK_START in run_unlimited.py")
    write_summary(d, model="unlimited-ocr", run_name=run_name,
                  config={"concurrency": a.concurrency, "pages_per_request": a.pages_per_request,
                          "crop_pass": a.crop_pass and a.pages_per_request == 1,
                          "crops": sum(r.get("n_crops", 0) for r in ok),
                          "empty_outputs": empties, "unparsed_outputs": unparsed,
                          "truncated": truncated},
                  n_pages=sum(r["n_pages"] for r in ok), wall_s=wall,
                  latencies=[r["latency_s"] / r["n_pages"] for r in ok],
                  failures=sum(r["n_pages"] for r in records if "error" in r),
                  counters_before=before, counters_after=after, sampler=smp)


if __name__ == "__main__":
    main()
