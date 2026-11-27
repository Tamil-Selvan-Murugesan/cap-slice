"""
Side-by-side viewer of PaddleOCR-VL vs MinerU output on the 15 hand-checked hard pages (vlm_test_pack).

Reads the full-corpus run outputs (results/full/<model>/full/md/<page_id>.{md,json}) and the pack's
page_checks, writes one HTML page that shows, per page: the page image | Paddle | MinerU, with the
manifest check on top. Each model column toggles between rendered markdown, raw markdown and all JSON
blocks (MinerU's markdown drops header/footer/page_number blocks; its JSON keeps them).

Output: <data>/compare/hard_pages.html (images referenced relatively, so open it in place).

Run:
  python parsing_eval/compare_hard_pages.py
"""
import json
import os
import re
from pathlib import Path

from paths import DATA, PACK, RESULTS

RUNS = {"PaddleOCR-VL-1.6": "paddleocr-vl-1.6", "MinerU2.5-Pro": "mineru2.5-pro"}
CHECKS = DATA / "sets" / "bench" / "page_checks.json"
OUT = DATA / "compare" / "hard_pages.html"


def paddle_blocks(d):
    return [(b["block_label"], b.get("block_content") or "") for b in d["res"]["parsing_res_list"]]


def mineru_blocks(d):
    def text(c):
        if isinstance(c, str):
            return c
        if isinstance(c, list):
            return "\n".join(t for t in (text(x) for x in c) if t)
        if isinstance(c, dict):
            sub = c.get("type", "")
            t = text(c.get("content", ""))
            return f"[{sub}] {t}" if sub and sub != "text" and t else t
        return ""
    return [(b["type"], text(b.get("content", ""))) for b in d["blocks"]]


def load(run, page_id):
    md_dir = RESULTS / "full" / run / "full" / "md"
    md_path, js_path = md_dir / f"{page_id}.md", md_dir / f"{page_id}.json"
    md = md_path.read_text() if md_path.exists() else None
    blocks = []
    if js_path.exists():
        d = json.loads(js_path.read_text())
        blocks = paddle_blocks(d) if "res" in d else mineru_blocks(d)
    # Paddle markdown links cropped images that were not kept; show a placeholder instead.
    if md:
        md = re.sub(r"<img[^>]*>", "<span class='img'>[image]</span>", md)
    return {"md": md, "blocks": blocks}


def main():
    checks = json.loads(CHECKS.read_text())
    pages = []
    for c in checks:
        pid = c["page_id"]
        img = PACK / "images" / f"{pid}.png"
        pages.append({
            **c,
            "img": os.path.relpath(img, OUT.parent),
            "models": {name: load(run, pid) for name, run in RUNS.items()},
        })
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(TEMPLATE.replace("__DATA__", json.dumps(pages).replace("</", "<\\/")))
    print(f"wrote {OUT} ({len(pages)} pages)")


TEMPLATE = r"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Hard Pages Compare</title>
<script src="https://cdnjs.cloudflare.com/ajax/libs/marked/12.0.2/marked.min.js"></script>
<style>
:root{--bg:#fafaf9;--panel:#fff;--fg:#1c1917;--muted:#78716c;--line:#e7e5e4;--accent:#2563eb;--chip:#f5f5f4}
@media (prefers-color-scheme:dark){:root{--bg:#1c1917;--panel:#262321;--fg:#f5f5f4;--muted:#a8a29e;--line:#44403c;--accent:#60a5fa;--chip:#33302d}}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--fg);font:14px/1.45 system-ui,sans-serif;display:flex;height:100vh}
nav{width:200px;flex:none;border-right:1px solid var(--line);overflow:auto;padding:8px}
nav button{display:block;width:100%;text-align:left;border:0;background:none;color:var(--fg);padding:6px 8px;border-radius:6px;cursor:pointer;font:inherit}
nav button small{display:block;color:var(--muted);font-size:11px}
nav button.on{background:var(--chip);font-weight:600}
main{flex:1;display:flex;flex-direction:column;min-width:0}
header{padding:10px 14px;border-bottom:1px solid var(--line)}
header h1{font-size:16px;margin:0 0 4px}
header p{margin:2px 0;color:var(--muted)}
header b{color:var(--fg)}
.cols{flex:1;display:grid;grid-template-columns:1fr 1fr 1fr;min-height:0}
.col{display:flex;flex-direction:column;min-height:0;border-right:1px solid var(--line)}
.col h2{font-size:13px;margin:0;padding:6px 10px;border-bottom:1px solid var(--line);display:flex;gap:6px;align-items:center;background:var(--panel)}
.col h2 span{flex:1}
.col h2 button{font:12px system-ui;border:1px solid var(--line);background:var(--bg);color:var(--fg);border-radius:4px;padding:2px 6px;cursor:pointer}
.col h2 button.on{border-color:var(--accent);color:var(--accent)}
.body{flex:1;overflow:auto;padding:10px;background:var(--panel)}
.body img.page{width:100%;cursor:zoom-in}
.body img.page.zoom{width:auto;max-width:none;cursor:zoom-out}
.body table{border-collapse:collapse;margin:6px 0;font-size:12px}
.body td,.body th{border:1px solid var(--line);padding:2px 5px}
.body pre{white-space:pre-wrap;font:12px/1.4 ui-monospace,monospace;margin:0}
.blk{border-bottom:1px dashed var(--line);padding:4px 0}
.blk i{color:var(--accent);font-style:normal;font-size:11px;font-family:ui-monospace,monospace}
.img{color:var(--muted);font-size:11px}
.missing{color:var(--muted);font-style:italic}
@media (max-width:900px){body{flex-direction:column;height:auto}nav{width:auto;display:flex;overflow-x:auto;border-right:0;border-bottom:1px solid var(--line)}nav button{white-space:nowrap}.cols{grid-template-columns:1fr}.body{max-height:70vh}}
</style></head><body>
<nav id="nav"></nav>
<main><header id="hdr"></header><div class="cols" id="cols"></div></main>
<script>
const PAGES = __DATA__;
const esc = s => s.replace(/[&<>]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;'}[c]));
let cur = 0, mode = {};
try { mode = JSON.parse(localStorage.getItem('mode') || '{}'); } catch (e) {}
function render(i){
  cur = i; const p = PAGES[i];
  document.querySelectorAll('nav button').forEach((b,j)=>b.classList.toggle('on', j===i));
  document.getElementById('hdr').innerHTML =
    `<h1>${p.page_id} <small style="color:var(--muted);font-weight:400">${p.category}</small></h1>
     <p><b>Why hard:</b> ${esc(p.why_hard)}</p><p><b>Check:</b> ${esc(p.check)}</p>`;
  let html = `<div class="col"><h2><span>Page image</span></h2><div class="body"><img class="page" src="${p.img}" onclick="this.classList.toggle('zoom')"></div></div>`;
  for (const [name, m] of Object.entries(p.models)) {
    const md = mode[name] || 'rendered';
    let body;
    if (md === 'blocks') body = m.blocks.length ? m.blocks.map(([t,c])=>`<div class="blk"><i>${esc(t)}</i><pre>${esc(c)||'<span class="missing">(empty)</span>'}</pre></div>`).join('') : '<p class="missing">no JSON</p>';
    else if (m.md == null) body = '<p class="missing">no markdown</p>';
    else if (md === 'raw' || !window.marked) body = `<pre>${esc(m.md)}</pre>`;
    else body = marked.parse(m.md);
    const btn = k => `<button class="${md===k?'on':''}" onclick="setMode('${name}','${k}')">${k}</button>`;
    html += `<div class="col"><h2><span>${name}</span>${btn('rendered')}${btn('raw')}${btn('blocks')}</h2><div class="body">${body}</div></div>`;
  }
  document.getElementById('cols').innerHTML = html;
  try { localStorage.setItem('page', i); } catch (e) {}
}
function setMode(name, k){ mode[name] = k; try { localStorage.setItem('mode', JSON.stringify(mode)); } catch (e) {} render(cur); }
document.getElementById('nav').innerHTML = PAGES.map((p,i)=>`<button onclick="render(${i})">${p.page_id}<small>${p.category}</small></button>`).join('');
document.addEventListener('keydown', e => {
  if (e.key==='ArrowDown'||e.key==='j') render(Math.min(cur+1, PAGES.length-1));
  if (e.key==='ArrowUp'||e.key==='k') render(Math.max(cur-1, 0));
});
let start = 0; try { start = +localStorage.getItem('page') || 0; } catch (e) {}
render(Math.min(start, PAGES.length-1));
</script></body></html>
"""

if __name__ == "__main__":
    main()
