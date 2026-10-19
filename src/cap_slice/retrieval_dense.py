"""Dense (embedding) retrieval runs for the retrieval experiments — round 1 in docs/plan.md.

    uv run cap-slice-retrieval-dense count  --model voyage-4-large                 # tokens + cost, no API calls
    uv run cap-slice-retrieval-dense embed  --model voyage-4-large --dim 2048      # embed chunks (resumable)
    uv run cap-slice-retrieval-dense load   --model voyage-4-large --dim 2048      # vectors -> local Qdrant
    uv run cap-slice-retrieval-dense search --model voyage-4-large --dim 2048 --filter question

Corpus: the same chunk file as the BM25 baseline (parsed_advanced/_chunks/mineru.jsonl: MinerU advanced ->
page_clean -> structured_chunk at tag chunker-baseline-2026-10-18). Round 1 embeds the bare chunk text;
all metadata goes in the Qdrant payload (docs/plan.md, Vector store and metadata).

embed  Documents in batches of <= 1,000 texts and <= 100K tokens (counted locally), input_type
       "document". Each batch is saved as a float32 shard under parsed_advanced/_vectors/<model>-<dim>/
       (gitignored) before the next is sent, so an interrupted run resumes without paying twice.
load   Shards -> collection r1__<model>-<dim>__baseline on the local Qdrant server
       (tools/qdrant/serve.sh; QDRANT_URL, default http://127.0.0.1:6333): cosine, HNSW (m 16,
       ef_construct 128), payload indexes on the filter fields, batched upload, then waits for indexing.
       Payload: provenance, filter fields (symbol, doc_type, fiscal_year, period_kind, chunk_kind,
       section) and bookkeeping (period, period_source, parser, chunker_version, embedding_model,
       image_only_page, generated).
search The 200 questions (input_type "query", cached), top 50 per question -> run JSONL for
       cap-slice-retrieval-score. Filters as in retrieval_bm25.py: none / company / question /
       question_next / answer_key; hard = Qdrant payload filter; --soft = top 500 unfiltered, cosine x
       SOFT_BOOST per matching filter field (the same boost as BM25, fixed before the first run).
       HNSW search with hnsw_ef 128; --exact searches exhaustively (to measure what HNSW loses).

--dry-run N  embed / load / search only the first N chunks (and the first 3 questions) into a separate
             vectors folder and a `dryrun__` collection: checks the whole path for a few cents.

Providers: `voyage` (VOYAGE_API_KEY). Another provider (e.g. a hosted Nemotron endpoint) only needs an
Embedder with embed(texts, input_type) and count(texts).
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import time
import uuid
from pathlib import Path

import numpy as np

from cap_slice.downloader import REPO_ROOT

CHUNKS = REPO_ROOT / "parsed_advanced" / "_chunks" / "mineru.jsonl"
VECTORS = REPO_ROOT / "parsed_advanced" / "_vectors"
QDRANT_URL = os.environ.get("QDRANT_URL", "http://127.0.0.1:6333")
HNSW_M, HNSW_EF_CONSTRUCT, HNSW_EF = 16, 128, 128
INDEXED = {"symbol": "keyword", "doc_type": "keyword", "fiscal_year": "integer", "period_kind": "keyword",
           "chunk_kind": "keyword", "doc_id": "keyword"}
CHUNKER_VERSION = "chunker-baseline-2026-10-18"
PARSER = "mineru_advanced"
MAX_TEXTS, MAX_TOKENS = 1000, 100_000
SOFT_BOOST, SOFT_POOL = 1.5, 500
_NS = uuid.UUID("5b0f7a52-3c1e-4d7a-9a51-6f1a2c9e8d10")  # same namespace as vectorstore.py
PRICES = {"voyage-4-large": 0.12}  # USD per 1M tokens, docs.voyageai.com/docs/pricing (checked 2026-10-19)


class VoyageEmbedder:
    def __init__(self, model: str, dim: int, need_key: bool = True):
        import voyageai
        self.model, self.dim = model, dim
        self.client = voyageai.Client(max_retries=5) if need_key else voyageai.Client(api_key="unused")

    def count(self, texts: list[str]) -> list[int]:
        out = []
        for i in range(0, len(texts), 1000):
            out += [len(t) for t in self.client.tokenize(texts[i:i + 1000], model=self.model)]
        return out

    def embed(self, texts: list[str], input_type: str) -> tuple[np.ndarray, int]:
        r = self.client.embed(texts, model=self.model, input_type=input_type, output_dimension=self.dim)
        return np.asarray(r.embeddings, dtype=np.float32), r.total_tokens


def embedder(provider: str, model: str, dim: int, need_key: bool = True):
    if provider == "voyage":
        return VoyageEmbedder(model, dim, need_key)
    raise SystemExit(f"unknown provider {provider!r}")


DRY_RUN = 0  # set from --dry-run


def load_chunks() -> list[dict]:
    chunks = [json.loads(line) for line in CHUNKS.open()]
    return chunks[:DRY_RUN] if DRY_RUN else chunks


def tag(model: str, dim: int) -> str:
    return f"{model}-{dim}" + (f"-dryrun{DRY_RUN}" if DRY_RUN else "")


def client():
    from qdrant_client import QdrantClient
    return QdrantClient(url=QDRANT_URL, timeout=300)


def batches(ntok: list[int]) -> list[tuple[int, int]]:
    out, start, used = [], 0, 0
    for i, n in enumerate(ntok):
        if i > start and (used + n > MAX_TOKENS or i - start >= MAX_TEXTS):
            out.append((start, i))
            start, used = i, 0
        used += n
    out.append((start, len(ntok)))
    return out


def cmd_count(args) -> int:
    chunks = load_chunks()
    ntok = embedder(args.provider, args.model, args.dim, need_key=False).count([c["text"] for c in chunks])
    total = sum(ntok)
    price = PRICES.get(args.model)
    print(f"{len(chunks):,} chunks, {total:,} tokens (max {max(ntok):,}), {len(batches(ntok))} requests"
          + (f"; ${total / 1e6 * price:.2f} at ${price}/1M tokens" if price else ""))
    return 0


def cmd_embed(args) -> int:
    chunks = load_chunks()
    texts = [c["text"] for c in chunks]
    emb = embedder(args.provider, args.model, args.dim)
    out = VECTORS / tag(args.model, args.dim)
    out.mkdir(parents=True, exist_ok=True)
    manifest = out / "manifest.json"
    corpus_hash = hashlib.sha256(CHUNKS.read_bytes()).hexdigest()  # of the whole file, also in a dry run
    if manifest.exists() and json.loads(manifest.read_text())["corpus_sha256"] != corpus_hash:
        raise SystemExit(f"{out} was embedded from a different chunk file; move it away first")
    manifest.write_text(json.dumps({"model": args.model, "dim": args.dim, "provider": args.provider,
                                    "corpus": str(CHUNKS.relative_to(REPO_ROOT)), "corpus_sha256": corpus_hash,
                                    "n_chunks": len(chunks), "chunker_version": CHUNKER_VERSION}, indent=1))
    plan = batches(emb.count(texts))
    log = out / "log.jsonl"
    done = sum((out / f"{a:06d}-{b:06d}.npy").exists() for a, b in plan)
    print(f"{len(plan)} requests, {done} already done")
    for k, (a, b) in enumerate(plan):
        shard = out / f"{a:06d}-{b:06d}.npy"
        if shard.exists():
            continue
        t = time.time()
        vecs, used = emb.embed(texts[a:b], "document")
        assert vecs.shape == (b - a, args.dim), vecs.shape
        np.save(shard.with_suffix(".tmp.npy"), vecs)
        shard.with_suffix(".tmp.npy").rename(shard)
        with log.open("a") as f:
            f.write(json.dumps({"shard": shard.name, "texts": b - a, "tokens": used,
                                "seconds": round(time.time() - t, 2), "at": time.strftime("%Y-%m-%dT%H:%M:%S")}) + "\n")
        print(f"[{k + 1}/{len(plan)}] chunks {a}-{b}: {used:,} tokens, {time.time() - t:.1f}s", flush=True)
    return 0


def all_vectors(model: str, dim: int, n: int) -> np.ndarray:
    out = VECTORS / tag(model, dim)
    shards = sorted(out.glob("[0-9]*-[0-9]*.npy"))
    spans = [tuple(int(x) for x in s.stem.split("-")) for s in shards]
    if not spans or spans[0][0] != 0 or spans[-1][1] != n or any(a[1] != b[0] for a, b in zip(spans, spans[1:])):
        raise SystemExit(f"{out}: shards incomplete — run `embed` first")
    return np.concatenate([np.load(s) for s in shards])


def payloads(chunks: list[dict], model: str) -> list[dict]:
    from cap_slice.periods import documents, load_overrides, normalise_doc, sme_symbols
    matrix = {r["url"]: r for r in csv.DictReader((REPO_ROOT / "data" / "document_availability_matrix.csv").open())}
    ov, sme = load_overrides(), sme_symbols()
    docs = {}
    for r in documents():
        n = normalise_doc(r["path"], r["doc_type"], r["period_label"], r["filed_date"], ov, r["symbol"] in sme)
        m = matrix.get(r["url"], {})
        docs[r["path"]] = {"doc_id": r["path"][len("data/"):-len(".pdf")], "path": r["path"],
                           "company": m.get("company", ""), "symbol": r["symbol"],
                           "listing_tier": m.get("listing_tier", ""), "doc_type": r["doc_type"],
                           "period_label": r["period_label"], "filed_date": r["filed_date"], "source_url": r["url"],
                           "fiscal_year": n["fiscal_year"], "period_kind": n["period_kind"], "period": n["period"],
                           "period_source": n["source"]}
    low = {}
    for r in csv.DictReader((REPO_ROOT / "data" / "golden" / "page_inventory.csv").open()):
        low[(r["doc"], int(r["page"]))] = r["low_text"] == "1"
    out = []
    for c in chunks:
        pages = range(c["page_start"], max(c["page_start"], c["page_end"]) + 1)
        out.append({**docs[c["doc"]], "chunk_index": c["chunk"], "page_start": c["page_start"],
                    "page_end": c["page_end"], "chunk_kind": c["kind"], "section": c["section"], "text": c["text"],
                    "parser": PARSER, "chunker_version": CHUNKER_VERSION, "embedding_model": model,
                    "image_only_page": all(low.get((c["doc"], p), False) for p in pages), "generated": False})
    return out


def collection_name(model: str, dim: int) -> str:
    return ("dryrun__" if DRY_RUN else "r1__") + f"{model}-{dim}__baseline"


def cmd_load(args) -> int:
    from qdrant_client import models
    chunks = load_chunks()
    vecs = all_vectors(args.model, args.dim, len(chunks))
    pays = payloads(chunks, args.model)
    qc = client()
    name = collection_name(args.model, args.dim)
    if qc.collection_exists(name):
        qc.delete_collection(name)
    qc.create_collection(name,
                         vectors_config=models.VectorParams(size=args.dim, distance=models.Distance.COSINE),
                         hnsw_config=models.HnswConfigDiff(m=HNSW_M, ef_construct=HNSW_EF_CONSTRUCT))
    for field, kind in INDEXED.items():
        qc.create_payload_index(name, field, field_schema=kind, wait=True)
    t = time.time()
    qc.upload_points(name, (models.PointStruct(id=str(uuid.uuid5(_NS, f"{p['doc_id']}#{p['chunk_index']}")),
                                               vector=vecs[j].tolist(), payload=p) for j, p in enumerate(pays)),
                     batch_size=256, wait=True)
    while (info := qc.get_collection(name)).status != models.CollectionStatus.GREEN:
        time.sleep(2)
    n = qc.count(name, exact=True).count
    print(f"{name}: {n:,} points, {info.indexed_vectors_count or 0:,} in the HNSW index, "
          f"{time.time() - t:.0f}s")
    qc.close()
    if n != len(chunks):
        raise SystemExit(f"expected {len(chunks)} points")
    return 0


def query_vectors(args, qs: list[dict]) -> np.ndarray:
    path = VECTORS / tag(args.model, args.dim) / "queries.json"
    cache = json.loads(path.read_text()) if path.exists() else {}
    missing = [q for q in qs if cache.get(q["qid"], {}).get("question") != q["question"]]
    if missing:
        emb = embedder(args.provider, args.model, args.dim)
        for i in range(0, len(missing), 128):
            vecs, _ = emb.embed([q["question"] for q in missing[i:i + 128]], "query")
            for q, v in zip(missing[i:i + 128], vecs):
                cache[q["qid"]] = {"question": q["question"], "vector": v.tolist()}
        path.write_text(json.dumps(cache))
    return np.asarray([cache[q["qid"]]["vector"] for q in qs], dtype=np.float32)


def qdrant_filter(f: dict, fields: tuple[str, ...], next_year: bool):
    from qdrant_client import models
    must = []
    if "symbol" in fields and f.get("symbol"):
        must.append(models.FieldCondition(key="symbol", match=models.MatchValue(value=f["symbol"])))
    if "year" in fields and f.get("fiscal_years"):
        years = set(f["fiscal_years"]) | ({y + 1 for y in f["fiscal_years"]} if next_year else set())
        must.append(models.FieldCondition(key="fiscal_year", match=models.MatchAny(any=sorted(years))))
    if "doc_type" in fields and f.get("doc_type"):
        must.append(models.FieldCondition(key="doc_type", match=models.MatchValue(value=f["doc_type"])))
    return models.Filter(must=must) if must else None


def cmd_search(args) -> int:
    from qdrant_client import models

    from cap_slice.query_reader import answer_key_filter, doc_meta, keeps, read
    from cap_slice.retrieval_score import load_questions
    qs = load_questions()[:3] if DRY_RUN else load_questions()
    qv = query_vectors(args, qs)
    meta = doc_meta()
    qc = client()
    name = collection_name(args.model, args.dim)
    params = models.SearchParams(exact=True) if args.exact else models.SearchParams(hnsw_ef=HNSW_EF)
    fields = {"none": (), "company": ("symbol",), "question": ("symbol", "year", "doc_type"),
              "question_next": ("symbol", "year", "doc_type"),
              "answer_key": ("symbol", "year", "doc_type")}[args.filter]
    nxt = args.filter == "question_next"
    keep = ["doc_id", "path", "chunk_index", "page_start", "page_end"]
    lines = []
    for q, v in zip(qs, qv):
        f = (answer_key_filter(q, meta) if args.filter == "answer_key" else read(q["question"])) if fields else {}
        if args.soft and fields:
            hits = qc.query_points(name, query=v.tolist(), limit=SOFT_POOL, search_params=params,
                                   with_payload=keep).points
            scored = [(h.score * SOFT_BOOST ** sum(keeps(f, meta[h.payload["path"]], (fld,), nxt) for fld in fields), h)
                      for h in hits]
        else:
            flt = qdrant_filter(f, fields, nxt) if fields else None
            hits = qc.query_points(name, query=v.tolist(), query_filter=flt, limit=args.top,
                                   search_params=params, with_payload=keep).points
            scored = [(h.score, h) for h in hits]
        scored.sort(key=lambda x: -x[0])
        lines.append(json.dumps({"qid": q["qid"], "results": [
            {"doc": h.payload["path"], "chunk": h.payload["chunk_index"], "page_start": h.payload["page_start"],
             "page_end": h.payload["page_end"], "score": round(s, 5)} for s, h in scored[:args.top]]}))
    qc.close()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text("\n".join(lines) + "\n")
    args.out.with_suffix(".meta.json").write_text(json.dumps(
        {"retriever": "dense", "provider": args.provider, "model": args.model, "dim": args.dim,
         "collection": name, "qdrant": "server 1.19.1", "search": "exact" if args.exact else f"hnsw_ef={HNSW_EF}",
         "hnsw": {"m": HNSW_M, "ef_construct": HNSW_EF_CONSTRUCT}, "corpus": str(CHUNKS.relative_to(REPO_ROOT)), "chunker_version": CHUNKER_VERSION,
         "filter": args.filter, "soft": args.soft, "soft_boost": SOFT_BOOST if args.soft else None,
         "soft_pool": SOFT_POOL if args.soft else None, "top": args.top}, indent=1))
    print(f"wrote {args.out}")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("command", choices=["count", "embed", "load", "search"])
    ap.add_argument("--provider", default="voyage")
    ap.add_argument("--model", default="voyage-4-large")
    ap.add_argument("--dim", type=int, default=2048)
    ap.add_argument("--filter", choices=["none", "company", "question", "question_next", "answer_key"], default="none")
    ap.add_argument("--soft", action="store_true")
    ap.add_argument("--top", type=int, default=50)
    ap.add_argument("--out", type=Path)
    ap.add_argument("--exact", action="store_true", help="exhaustive search instead of HNSW")
    ap.add_argument("--dry-run", type=int, default=0, metavar="N")
    args = ap.parse_args(argv)
    global DRY_RUN
    DRY_RUN = args.dry_run
    if args.command == "search" and not args.out:
        suffix = "" if args.filter == "none" else f"-{args.filter}" + ("-soft" if args.soft else "")
        suffix += "-exact" if args.exact else ""
        args.out = REPO_ROOT / "review" / "retrieval" / f"dense-{tag(args.model, args.dim)}{suffix}.jsonl"
    return {"count": cmd_count, "embed": cmd_embed, "load": cmd_load, "search": cmd_search}[args.command](args)


if __name__ == "__main__":
    raise SystemExit(main())
