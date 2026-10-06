import sys,csv,json,pathlib,html,base64
sys.path.insert(0,'src')
import pymupdf
from cap_slice.page_clean import clean_pages
from cap_slice.score import chunks_for
out=pathlib.Path('review/visual-2026-10-06')
out.mkdir(parents=True,exist_ok=True)
gold=list(csv.DictReader(open('data/golden/v3_pages.csv')))
ids=['dense02','dense03','dense05','dense07','dense11','dense19','conti02','conti12','slide05','slide07','slide11','slide14','slide18','sdoc06','sdoc14','sdoc07','sdoc19']
# 17 golden pages, plus 8 pages not in the earlier visual spot checks.
chosen=[dict(path=r['doc'],page=int(r['page']),reason=r['pool'],selection=r['cand_id']) for r in gold if r['cand_id'] in ids]
new=[('data/ESCONET/annual_reports/2026-08-25_FY2025-26.pdf',144,'seeded dense-table sample'),('data/C2C/annual_reports/2025-09-08_FY2024-25.pdf',104,'seeded dense-table sample'),('data/E2E/annual_reports/2020-08-19_FY2019-20.pdf',57,'seeded dense-table sample'),('data/HEROMOTOCO/annual_reports/FY2023-24.pdf',176,'seeded dense-table sample'),('data/E2E/annual_reports/2023-09-21_FY2022-23.pdf',125,'scanned cash flow adjacent to original golden statement'),('data/APARINDS/investor_presentations/Sep-2024.pdf',140,'MinerU residual repetition candidate'),('data/E2E/investor_presentations/Nov-2021.pdf',24,'MinerU residual repetition candidate'),('data/HEROMOTOCO/annual_reports/FY2025-26.pdf',35,'Paddle residual repetition candidate')]
chosen += [dict(path=p,page=n,reason=r,selection='additional') for p,n,r in new]
if '--viewer-only' in sys.argv:
 entries=json.loads((out/'manifest.json').read_text())
else:
 cache={}; entries=[]
 for i,r in enumerate(chosen,1):
  rid=f'H{i:02}';folder=out/rid;folder.mkdir(exist_ok=True);r['id']=rid
  with pymupdf.open(r['path']) as doc:
   page=doc[r['page']-1];page.get_pixmap(dpi=170).save(folder/'source.jpg',jpg_quality=88)
   (folder/'source-text-layer.txt').write_text(page.get_text())
  r['parsers']={}
  for name,base,p in [('mineru_advanced','parsed_advanced','mineru'),('paddleocr_vl','parsed','paddleocr_vl'),('docling','parsed','docling'),('mineru_standard','parsed','mineru')]:
   key=(base,p,r['path'])
   f=pathlib.Path(base)/p/pathlib.Path(r['path']).relative_to('data').with_suffix('')/'pages.json'
   if not f.exists():continue
   if key not in cache:
    raw=json.load(open(f))['pages'];clean,st=clean_pages(raw,pathlib.Path(r['path']));cache[key]=(dict(raw),dict(clean),chunks_for(p,clean),st)
   raw,clean,chunks,st=cache[key];n=r['page']
   selected=[dict(index=c.index,kind=c.kind,section=c.section,page_start=c.page_start,page_end=c.page_end,text=c.text) for c in chunks if c.page_start<=n<=c.page_end]
   (folder/f'{name}-raw.md').write_text(raw.get(n,''));(folder/f'{name}-clean.md').write_text(clean.get(n,''));(folder/f'{name}-chunks.json').write_text(json.dumps(selected,ensure_ascii=False,indent=2))
   (folder/f'{name}-chunks.md').write_text('\n\n'.join(f'### Chunk {c["index"]} — pages {c["page_start"]}–{c["page_end"]}\n\n{c["text"]}' for c in selected))
   r['parsers'][name]=dict(raw_chars=len(raw.get(n,'')),clean_chars=len(clean.get(n,'')),chunks=[c['index'] for c in selected],unit_restored=n in st['units_restored_pages'])
  entries.append(r)
 (out/'manifest.json').write_text(json.dumps(entries,indent=2))
style='<style>body{font:16px system-ui;margin:24px;background:#f4f5f7;color:#18202b}article{margin-bottom:45px;background:white;padding:20px;border-radius:8px}.panes{display:grid;grid-template-columns:1fr 1fr 1fr;gap:16px}img{width:100%}pre{white-space:pre-wrap;overflow-wrap:anywhere;font:12px monospace;max-height:850px;overflow:auto;background:#fafafa;padding:12px}summary{cursor:pointer;font-weight:600}a{color:#164bb8}@media(max-width:1000px){.panes{grid-template-columns:1fr}}</style>'
body=['<!doctype html><meta charset="utf-8"><title>Hard-page parser review</title>'+style,'<h1>Hard-page visual review — 2026-10-06</h1><p>Source images, cached parser text, and chunks regenerated with the current shared cleanup/chunker on the entire document. These are candidate embedding chunks; the indexer has not been switched. Selected cases are diagnostic, not a random accuracy estimate.</p>','<nav>'+ ' · '.join(f'<a href="#{r["id"]}">{r["id"]}</a>' for r in entries)+'</nav>']
for r in entries:
 rid=r['id'];folder=out/rid
 source_uri='data:image/jpeg;base64,'+base64.b64encode((folder/'source.jpg').read_bytes()).decode('ascii')
 body += [f'<article id="{rid}"><h2>{rid}: {html.escape(r["path"])} — PDF p.{r["page"]}</h2><p>{html.escape(r["reason"])}</p><div class="panes"><div><img alt="Source PDF page for {rid}" src="{source_uri}"></div>']
 for p in ['mineru_advanced','paddleocr_vl']:
  body.append(f'<div><h3>{p}</h3>')
  for stage in ['raw','clean','chunks']:
   t=(folder/f'{p}-{stage}.md').read_text();body.append(f'<details {"open" if stage=="chunks" else ""}><summary>{stage} ({len(t):,} chars)</summary><pre>{html.escape(t)}</pre></details>')
  body.append('</div>')
 body.append('</div>')
 for p in ['docling','mineru_standard']:
  if p not in r['parsers']:continue
  body.append(f'<details><summary>Additional comparison: {p}</summary>')
  for stage in ['raw','clean','chunks']:
   t=(folder/f'{p}-{stage}.md').read_text()
   body.append(f'<details><summary>{stage}</summary><pre>{html.escape(t)}</pre></details>')
  body.append('</details>')
 for raw_file in sorted(folder.glob('*-r2-page.json')):
  body.append(f'<details><summary>R2 raw excerpt: {raw_file.name}</summary><pre>{html.escape(raw_file.read_text())}</pre></details>')
 body.append('</article>')
body.append('<details><summary>Page manifest</summary><pre>'+html.escape(json.dumps(entries,indent=2))+'</pre></details>')
if (out/'provenance.json').exists():
 body.append('<details><summary>Original audit provenance (code and R2 object hashes)</summary><pre>'+html.escape((out/'provenance.json').read_text())+'</pre></details>')
(out/'index.html').write_text('\n'.join(line.rstrip() for line in '\n'.join(body).splitlines())+'\n')
print(json.dumps([dict(id=r['id'],path=r['path'],page=r['page'],reason=r['reason']) for r in entries],indent=1))
