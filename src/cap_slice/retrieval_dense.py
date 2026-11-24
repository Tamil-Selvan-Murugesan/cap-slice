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

--corpus V   round 2 (docs/plan.md): use parsed_advanced/_chunks/r2-<V>.jsonl from cap-slice-chunk-variants.
             Embeds each record's `embed_text`, returns its `text`; vectors in _vectors/<model>-<dim>__r2-<V>/,
             collection r2__<model>-<dim>__<V>; searches return each `parent` once (small-to-big returns the
             parent chunk of the best piece) and write to review/retrieval/round2/. Question vectors are
             shared with round 1 (same model, same questions).

--dry-run N  embed / load / search only the first N chunks (and the first 3 questions) into a separate
             vectors folder and a `dryrun__` collection: checks the whole path for a few cents.

Providers:
  voyage   Voyage API (VOYAGE_API_KEY); input_type does the query/document prompts.
  openai   any OpenAI-compatible /v1/embeddings server, e.g. a self-hosted Nemotron 3 Embed 8B:
           --endpoint (or EMBED_ENDPOINT), key from --key-env (default NEMOTRON_API_KEY), `dimensions` sent
           with every request. Nemotron's /v1/embeddings ignores input_type, so the retrieval prompts are
           added here (--doc-prefix "passage: ", --query-prefix "query: "); without them quality drops
           silently. Token counts are estimated (chars / 3) for batching; the server's counts are logged.
           Requests run --workers at a time.
"""

from __future__ import annotations

import argparse
import concurrent.futures
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
    max_texts, max_tokens, workers = MAX_TEXTS, MAX_TOKENS, 1

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


class OpenAICompatEmbedder:
    """OpenAI-compatible /v1/embeddings (self-hosted Nemotron 3 Embed); prompts added client-side."""
    max_texts, max_tokens = 32, 24_000

    def __init__(self, model: str, dim: int, endpoint: str, key_env: str, prefixes: dict[str, str],
                 workers: int = 4, need_key: bool = True):
        import requests
        self.model, self.dim, self.prefixes, self.workers = model, dim, prefixes, workers
        self.url = endpoint.rstrip("/") + ("" if endpoint.rstrip("/").endswith("/v1/embeddings") else "/v1/embeddings")
        key = os.environ.get(key_env, "") if need_key else ""
        if need_key and not key:
            raise SystemExit(f"{key_env} is not set")
        self.session = requests.Session()
        self.session.headers["Authorization"] = f"Bearer {key}"

    def count(self, texts: list[str]) -> list[int]:
        return [len(t) // 3 + 1 for t in texts]  # estimate, for batching only

    def embed(self, texts: list[str], input_type: str) -> tuple[np.ndarray, int]:
        body = {"model": self.model, "input": [self.prefixes[input_type] + t for t in texts], "dimensions": self.dim}
        for attempt in range(6):
            try:
                r = self.session.post(self.url, json=body, timeout=300)
                if r.status_code < 500 and r.status_code != 429:
                    r.raise_for_status()
                    j = r.json()
                    data = sorted(j["data"], key=lambda d: d["index"])
                    return (np.asarray([d["embedding"] for d in data], dtype=np.float32),
                            j.get("usage", {}).get("total_tokens", 0))
            except Exception:
                if attempt == 5:
                    raise
            time.sleep(2 ** attempt)
        raise SystemExit(f"{self.url}: failed after retries (HTTP {r.status_code}: {r.text[:200]})")


PROVIDER_ARGS: dict = {}  # set from the command line


def embedder(provider: str, model: str, dim: int, need_key: bool = True):
    if provider == "voyage":
        return VoyageEmbedder(model, dim, need_key)
    if provider == "openai":
        a = PROVIDER_ARGS
        if not a.get("endpoint"):
            raise SystemExit("--endpoint (or EMBED_ENDPOINT) is required for provider openai")
        return OpenAICompatEmbedder(model, dim, a["endpoint"], a["key_env"],
                                    {"document": a["doc_prefix"], "query": a["query_prefix"]}, a["workers"], need_key)
    raise SystemExit(f"unknown provider {provider!r}")


DRY_RUN = 0  # set from --dry-run
CORPUS = ""  # set from --corpus (round 2 variant)


def load_chunks() -> list[dict]:
    chunks = [json.loads(line) for line in CHUNKS.open()]
    return chunks[:DRY_RUN] if DRY_RUN else chunks


def tag(model: str, dim: int) -> str:
    """Folder / collection tag: nvidia/Nemotron-3-Embed-8B-BF16 -> nemotron-3-embed-8b-bf16-2048."""
    return (f"{model.split('/')[-1].lower()}-{dim}" + (f"__r2-{CORPUS}" if CORPUS else "")
            + (f"-dryrun{DRY_RUN}" if DRY_RUN else ""))


def chunker_version() -> str:
    return CHUNKER_VERSION + (f"+r2-{CORPUS}" if CORPUS else "")


def embed_texts(chunks: list[dict]) -> list[str]:
    return [c.get("embed_text", c["text"]) for c in chunks]


def client():
    from qdrant_client import QdrantClient
    return QdrantClient(url=QDRANT_URL, timeout=300)


def batches(ntok: list[int], max_texts: int = MAX_TEXTS, max_tokens: int = MAX_TOKENS) -> list[tuple[int, int]]:
    out, start, used = [], 0, 0
    for i, n in enumerate(ntok):
        if i > start and (used + n > max_tokens or i - start >= max_texts):
            out.append((start, i))
            start, used = i, 0
        used += n
    out.append((start, len(ntok)))
    return out


def cmd_count(args) -> int:
    chunks = load_chunks()
    emb = embedder(args.provider, args.model, args.dim, need_key=False)
    ntok = emb.count(embed_texts(chunks))
    total = sum(ntok)
    price = PRICES.get(args.model)
    print(f"{len(chunks):,} chunks, {total:,} tokens (max {max(ntok):,}), "
          f"{len(batches(ntok, emb.max_texts, emb.max_tokens))} requests"
          + (f"; ${total / 1e6 * price:.2f} at ${price}/1M tokens" if price else ""))
    return 0


def cmd_embed(args) -> int:
    chunks = load_chunks()
    texts = embed_texts(chunks)
    emb = embedder(args.provider, args.model, args.dim)
    out = VECTORS / tag(args.model, args.dim)
    out.mkdir(parents=True, exist_ok=True)
    manifest = out / "manifest.json"
    corpus_hash = hashlib.sha256(CHUNKS.read_bytes()).hexdigest()  # of the whole file, also in a dry run
    if manifest.exists() and json.loads(manifest.read_text())["corpus_sha256"] != corpus_hash:
        raise SystemExit(f"{out} was embedded from a different chunk file; move it away first")
    extra = ({"prefixes": emb.prefixes, "served_by": "self-hosted OpenAI-compatible server"}
             if args.provider == "openai" else {})
    manifest.write_text(json.dumps({"model": args.model, "dim": args.dim, "provider": args.provider, **extra,
                                    "corpus": str(CHUNKS.relative_to(REPO_ROOT)), "corpus_sha256": corpus_hash,
                                    "n_chunks": len(chunks), "chunker_version": chunker_version()}, indent=1))
    plan = batches(emb.count(texts), emb.max_texts, emb.max_tokens)
    log = out / "log.jsonl"
    todo = [(k, a, b) for k, (a, b) in enumerate(plan) if not (out / f"{a:06d}-{b:06d}.npy").exists()]
    print(f"{len(plan)} requests, {len(plan) - len(todo)} already done, {emb.workers} at a time")

    def one(k: int, a: int, b: int) -> str:
        shard = out / f"{a:06d}-{b:06d}.npy"
        t = time.time()
        vecs, used = emb.embed(texts[a:b], "document")
        assert vecs.shape == (b - a, args.dim), vecs.shape
        np.save(shard.with_suffix(".tmp.npy"), vecs)
        shard.with_suffix(".tmp.npy").rename(shard)
        with log.open("a") as f:
            f.write(json.dumps({"shard": shard.name, "texts": b - a, "tokens": used,
                                "seconds": round(time.time() - t, 2), "at": time.strftime("%Y-%m-%dT%H:%M:%S")}) + "\n")
        return f"[{k + 1}/{len(plan)}] chunks {a}-{b}: {used:,} tokens, {time.time() - t:.1f}s"

    t0 = time.time()
    with concurrent.futures.ThreadPoolExecutor(emb.workers) as pool:
        for i, fut in enumerate(concurrent.futures.as_completed([pool.submit(one, *x) for x in todo]), 1):
            msg = fut.result()
            if i % max(1, len(todo) // 50) == 0 or i == len(todo):
                print(f"{msg}  ({i}/{len(todo)} this run, {time.time() - t0:.0f}s)", flush=True)
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
                    "parent": c.get("parent", c["chunk"]), "parser": PARSER, "chunker_version": chunker_version(), "embedding_model": model,
                    "image_only_page": all(low.get((c["doc"], p), False) for p in pages), "generated": False})
    return out


def collection_name(model: str, dim: int) -> str:
    base = f"{model.split('/')[-1].lower()}-{dim}"
    if CORPUS:
        return ("dryrun__" if DRY_RUN else "r2__") + f"{base}__{CORPUS}"
    return ("dryrun__" if DRY_RUN else "r1__") + f"{base}__baseline"


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
    # Question vectors depend only on model and dim: shared by every corpus (and by dry runs).
    path = VECTORS / f"{args.model.split('/')[-1].lower()}-{args.dim}" / "queries.json"
    path.parent.mkdir(parents=True, exist_ok=True)
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
    keep = ["doc_id", "path", "chunk_index", "page_start", "page_end", "parent"]
    fetch = SOFT_POOL if CORPUS == "e" else args.top  # small-to-big: enough pieces for args.top parents
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
            hits = qc.query_points(name, query=v.tolist(), query_filter=flt, limit=fetch,
                                   search_params=params, with_payload=keep).points
            scored = [(h.score, h) for h in hits]
        scored.sort(key=lambda x: -x[0])
        seen, best = set(), []  # each returned unit (parent chunk) once, at its best-scoring piece
        for s, h in scored:
            key = (h.payload["path"], h.payload.get("parent", h.payload["chunk_index"]))
            if key not in seen:
                seen.add(key)
                best.append((s, h))
        lines.append(json.dumps({"qid": q["qid"], "results": [
            {"doc": h.payload["path"], "chunk": h.payload.get("parent", h.payload["chunk_index"]),
             "page_start": h.payload["page_start"], "page_end": h.payload["page_end"], "score": round(s, 5)}
            for s, h in best[:args.top]]}))
    qc.close()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text("\n".join(lines) + "\n")
    args.out.with_suffix(".meta.json").write_text(json.dumps(
        {"retriever": "dense", "provider": args.provider, "model": args.model, "dim": args.dim,
         "collection": name, "qdrant": "server 1.19.1", "search": "exact" if args.exact else f"hnsw_ef={HNSW_EF}",
         "hnsw": {"m": HNSW_M, "ef_construct": HNSW_EF_CONSTRUCT}, "corpus": str(CHUNKS.relative_to(REPO_ROOT)), "chunker_version": chunker_version(),
         "filter": args.filter, "soft": args.soft, "soft_boost": SOFT_BOOST if args.soft else None,
         "soft_pool": SOFT_POOL if args.soft else None, "top": args.top}, indent=1))
    print(f"wrote {args.out}")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("command", choices=["count", "embed", "load", "search"])
    ap.add_argument("--provider", default="voyage", choices=["voyage", "openai"])
    ap.add_argument("--endpoint", default=os.environ.get("EMBED_ENDPOINT"), help="provider openai: server base URL")
    ap.add_argument("--key-env", default="NEMOTRON_API_KEY", help="provider openai: env var holding the API key")
    ap.add_argument("--doc-prefix", default="passage: ")
    ap.add_argument("--query-prefix", default="query: ")
    ap.add_argument("--workers", type=int, default=4, help="provider openai: concurrent requests")
    ap.add_argument("--model", default="voyage-4-large")
    ap.add_argument("--dim", type=int, default=2048)
    ap.add_argument("--filter", choices=["none", "company", "question", "question_next", "answer_key"], default="none")
    ap.add_argument("--soft", action="store_true")
    ap.add_argument("--top", type=int, default=50)
    ap.add_argument("--out", type=Path)
    ap.add_argument("--exact", action="store_true", help="exhaustive search instead of HNSW")
    ap.add_argument("--dry-run", type=int, default=0, metavar="N")
    ap.add_argument("--corpus", default="", help="round-2 variant: use parsed_advanced/_chunks/r2-<corpus>.jsonl")
    args = ap.parse_args(argv)
    global DRY_RUN, CORPUS, CHUNKS
    DRY_RUN, CORPUS = args.dry_run, args.corpus
    if CORPUS:
        CHUNKS = CHUNKS.parent / f"r2-{CORPUS}.jsonl"
    PROVIDER_ARGS.update(endpoint=args.endpoint, key_env=args.key_env, doc_prefix=args.doc_prefix,
                         query_prefix=args.query_prefix, workers=args.workers)
    if args.command == "search" and not args.out:
        suffix = "" if args.filter == "none" else f"-{args.filter}" + ("-soft" if args.soft else "")
        suffix += "-exact" if args.exact else ""
        sub = ("round2",) if CORPUS else ()
        args.out = REPO_ROOT.joinpath("review", "retrieval", *sub, f"dense-{tag(args.model, args.dim)}{suffix}.jsonl")
    return {"count": cmd_count, "embed": cmd_embed, "load": cmd_load, "search": cmd_search}[args.command](args)


if __name__ == "__main__":
    raise SystemExit(main())
