"""Score a parser's batch cache against a golden facts file.

    uv run cap-slice-score --parser docling                       # v2 facts, cache in parsed/
    uv run cap-slice-score --parser mineru --cache parsed --facts data/golden/v2_facts.csv

Reads ``<cache>/<parser>/<doc_id>/pages.json`` (written by cap-slice-parse),
chunks it (old chunk.py for ``baseline``, structured_chunk.py for the rest) and
scores every fact with compare_parsers.score_fact — the same L1–L4 levels as
v1, only chunks covering the fact's page count. Writes
``review/v2/<parser>.json`` and a Markdown report, and also reports how much
text each parser produced for the decorative "hallucination check" pages in
v2_skipped.csv (a good parser outputs ~nothing there).
"""

from __future__ import annotations

import argparse
import collections
import csv
import json
import sys
from pathlib import Path

from cap_slice.batch_parse import doc_id_for
from cap_slice.compare_parsers import OutChunk, score_fact
from cap_slice.downloader import REPO_ROOT

GOLDEN = REPO_ROOT / "data" / "golden"
TAGS = {"two_level_header": "TWO-LEVEL HEADER", "bad_text_layer": "OCR text layer WITH ERRORS"}


def chunks_for(parser: str, pages: list[list]) -> list[OutChunk]:
    if parser == "baseline":
        from cap_slice.chunk import chunk_pages
        from cap_slice.extract import Page
        return [OutChunk(c.index, "text", c.text, "", c.page_start, c.page_end, [])
                for c in chunk_pages([Page(n, t) for n, t in pages])]
    from cap_slice.parsing import ParsedPage
    from cap_slice.structured_chunk import chunk_structured
    return [OutChunk(c.index, c.kind, c.text, c.section, c.page_start, c.page_end, c.notes)
            for c in chunk_structured([ParsedPage(n, t) for n, t in pages])]


def load_pages(cache: Path, parser: str, path: str) -> dict | None:
    f = cache / parser / doc_id_for(REPO_ROOT / path) / "pages.json"
    return json.loads(f.read_text()) if f.exists() else None


def groups(fact: dict) -> list[str]:
    g = [f"stratum:{fact['stratum']}", f"kind:{fact['kind']}"]
    g += [f"tag:{t}" for t, marker in TAGS.items() if marker in fact.get("note", "")]
    if fact["stratum"] == "low_text_numeric":
        g.append("tag:image_only_page")
    return g


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--parser", required=True)
    ap.add_argument("--cache", default="parsed")
    ap.add_argument("--facts", default=str(GOLDEN / "v2_facts.csv"))
    ap.add_argument("--skipped", default=str(GOLDEN / "v2_skipped.csv"))
    ap.add_argument("--out", default="review/v2")
    ap.add_argument("--name", help="output file stem (default: the parser name)")
    ap.add_argument("--clean", action="store_true",
                    help="apply page_clean.py first (drop invented picture text, unwrap layout HTML, "
                         "restore a missed units line from the PDF text layer) — same for every parser")
    args = ap.parse_args(argv)
    cache = Path(args.cache) if Path(args.cache).is_absolute() else REPO_ROOT / args.cache
    facts = list(csv.DictReader(open(args.facts)))
    if facts and "path" not in facts[0]:  # v1 facts: document keys, paths in compare_docs.csv
        paths = {d["key"]: d["path"] for d in csv.DictReader((GOLDEN / "compare_docs.csv").open())}
        for f in facts:
            f["path"] = paths[f["doc"]]
            f["stratum"] = f.get("stratum") or "v1"

    results, by_doc, missing = [], {}, set()
    clean_stats = {"docs": 0, "units_restored_pages": 0}
    for path in sorted({f["path"] for f in facts}):
        data = load_pages(cache, args.parser, path)
        if data is None:
            missing.add(path)
            continue
        pages = data["pages"]
        if args.clean:
            from cap_slice.page_clean import clean_pages
            pages, st = clean_pages(pages, REPO_ROOT / path)
            clean_stats["docs"] += 1
            clean_stats["units_restored_pages"] += len(st["units_restored_pages"])
        by_doc[path] = chunks_for(args.parser, pages)
    for f in facts:
        if f["path"] in missing:
            results.append({"id": f["id"], "level": None, "chunk": None, "groups": groups(f)})
            continue
        level, where = score_fact(f, by_doc[f["path"]])
        results.append({"id": f["id"], "level": level, "chunk": where, "groups": groups(f)})

    scored = [r for r in results if r["level"] is not None]
    summary = {"parser": args.parser, "facts": len(facts), "scored": len(scored),
               "docs_missing": sorted(missing),
               "levels": {f"L{l}+": sum(r["level"] >= l for r in scored) for l in (1, 2, 3, 4)}}
    per_group = collections.defaultdict(lambda: [0, 0])
    for r in scored:
        for g in r["groups"]:
            per_group[g][0] += r["level"] >= 4
            per_group[g][1] += 1
    summary["l4_by_group"] = {g: f"{a}/{b}" for g, (a, b) in sorted(per_group.items())}

    halluc = []
    if Path(args.skipped).exists():
        for row in csv.DictReader(open(args.skipped)):
            if "hallucination" not in row["reason"]:
                continue
            data = load_pages(cache, args.parser, row["path"])
            if data and args.clean:
                from cap_slice.page_clean import clean_pages
                data = {"pages": clean_pages(data["pages"])[0]}
            text = dict((n, t) for n, t in data["pages"]).get(int(row["page"]), "") if data else None
            halluc.append({"path": row["path"], "page": int(row["page"]),
                           "chars": None if text is None else len(text.strip()),
                           "sample": None if not text else " / ".join(text.split("\n")).strip()[:120]})
    summary["hallucination_check"] = halluc
    if args.clean:
        summary["clean"] = clean_stats

    out = REPO_ROOT / args.out
    out.mkdir(parents=True, exist_ok=True)
    (out / f"{args.name or args.parser}.json").write_text(json.dumps({"summary": summary, "facts": results}, indent=1))
    lines = [f"# Golden v2 — {args.parser}\n",
             f"{summary['scored']}/{summary['facts']} facts scored "
             f"({len(missing)} documents not in the cache).\n",
             "| Level | Facts |", "|---|---|"]
    lines += [f"| ≥ {k[:-1]} | {v}/{summary['scored']} |" for k, v in summary["levels"].items()]
    lines += ["\n## L4 by group\n", "| Group | L4 |", "|---|---|"]
    lines += [f"| {g} | {v} |" for g, v in summary["l4_by_group"].items()]
    if halluc:
        lines += ["\n## Hallucination check (decorative pages — expect only the slide's own few words, e.g. \"THANK YOU\")\n",
                  "| Page | Chars | Start of output |", "|---|---|---|"]
        lines += [f"| {Path(h['path']).name} p{h['page']} | {h['chars']} | {(h['sample'] or '').replace('|', '/')} |"
                  for h in halluc]
    lines += ["\n## Facts below L4\n", "| Fact | Level | Chunk |", "|---|---|---|"]
    lines += [f"| {r['id']} | {r['level']} | {r['chunk']} |" for r in results
              if r["level"] is not None and r["level"] < 4]
    (out / f"{args.name or args.parser}.md").write_text("\n".join(lines) + "\n")
    print(json.dumps({k: summary[k] for k in ("parser", "scored", "levels")}), file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
