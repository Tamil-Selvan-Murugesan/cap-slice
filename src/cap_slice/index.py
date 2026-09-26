"""Extract, chunk, embed and store downloaded documents in Qdrant.

Works from the availability matrix: every row with download_status == yes.
Re-runs skip documents whose exact file (by sha256) is already indexed.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import sys

from cap_slice.chunk import chunk_pages
from cap_slice.downloader import DATA_DIR, DOC_TYPE_DIRS, MATRIX_PATH, REPO_ROOT, existing_file
from cap_slice.extract import extract_pdf


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--symbol", action="append", help="limit to these NSE symbols")
    ap.add_argument("--doc-type", action="append", choices=sorted(DOC_TYPE_DIRS))
    ap.add_argument("--dry-run", action="store_true",
                    help="extract and chunk only; no embedding calls, nothing stored")
    ap.add_argument("--reindex", action="store_true",
                    help="re-embed documents even if already indexed")
    args = ap.parse_args(argv)

    with MATRIX_PATH.open(newline="") as f:
        rows = [
            r for r in csv.DictReader(f)
            if r.get("download_status") == "yes"
            and (not args.symbol or r["symbol"] in args.symbol)
            and (not args.doc_type or r["doc_type"] in args.doc_type)
        ]
    print(f"{len(rows)} downloaded documents match the filters", file=sys.stderr)

    embedder = store = None
    if not args.dry_run:
        # Imported here so --dry-run works without an API key.
        from cap_slice.embed import VoyageEmbedder
        from cap_slice.vectorstore import ChunkStore
        embedder, store = VoyageEmbedder(), ChunkStore()

    totals = {"indexed": 0, "skipped": 0, "needs_ocr": 0, "failed": 0, "chunks": 0}
    for i, row in enumerate(rows, 1):
        path = existing_file(row)
        label = f"[{i}/{len(rows)}] {row['symbol']:<10} {row['doc_type']:<21} {row['period_label']}"
        if path is None or path.suffix != ".pdf":
            print(f"{label}  failed: no PDF on disk", file=sys.stderr)
            totals["failed"] += 1
            continue

        doc_id = str(path.relative_to(DATA_DIR).with_suffix(""))
        sha = hashlib.sha256(path.read_bytes()).hexdigest()
        if store and not args.reindex and store.has_doc(doc_id, sha):
            totals["skipped"] += 1
            continue

        try:
            doc = extract_pdf(path)
        except Exception as e:  # corrupt/encrypted PDFs
            print(f"{label}  failed: {type(e).__name__}: {e}", file=sys.stderr)
            totals["failed"] += 1
            continue
        if doc.needs_ocr:
            print(f"{label}  needs OCR ({len(doc.scanned_pages)}/{doc.page_count} "
                  f"pages have no text) - skipped", file=sys.stderr)
            totals["needs_ocr"] += 1
            continue

        chunks = chunk_pages(doc.pages)
        print(f"{label}  {doc.page_count} pages, {len(chunks)} chunks"
              + (f", {len(doc.scanned_pages)} pages without text" if doc.scanned_pages else ""),
              file=sys.stderr)
        totals["chunks"] += len(chunks)
        if args.dry_run or not chunks:
            continue

        vectors = embedder.embed_documents([c.text for c in chunks])
        store.ensure_collection(len(vectors[0]))
        payloads = [{
            "doc_id": doc_id,
            "sha256": sha,
            "company": row["company"],
            "symbol": row["symbol"],
            "listing_tier": row["listing_tier"],
            "doc_type": row["doc_type"],
            "period_label": row["period_label"],
            "filed_date": row["filed_date"],
            "source_url": row["url"],
            "path": str(path.relative_to(REPO_ROOT)),
            "chunk_index": c.index,
            "n_chunks": len(chunks),
            "page_start": c.page_start,
            "page_end": c.page_end,
            "text": c.text,
            "embedding_model": embedder.model,
        } for c in chunks]
        store.replace_doc(doc_id, vectors, payloads)
        totals["indexed"] += 1

    if store:
        store.close()
    print(f"done: {totals}", file=sys.stderr)
    return 1 if totals["failed"] else 0


def search_main(argv: list[str] | None = None) -> int:
    """Quick check of the index: cap-slice-search "query" [--symbol X]."""
    from cap_slice.embed import VoyageEmbedder
    from cap_slice.vectorstore import ChunkStore

    ap = argparse.ArgumentParser(description="Search indexed filings")
    ap.add_argument("query")
    ap.add_argument("--symbol")
    ap.add_argument("--doc-type", choices=sorted(DOC_TYPE_DIRS))
    ap.add_argument("-k", type=int, default=5)
    args = ap.parse_args(argv)

    vector = VoyageEmbedder().embed_query(args.query)
    store = ChunkStore()
    hits = store.search(vector, args.k, symbol=args.symbol, doc_type=args.doc_type)
    store.close()
    for hit in hits:
        p = hit.payload
        print(f"{hit.score:.3f}  {p['symbol']} {p['doc_type']} {p['period_label']} "
              f"p.{p['page_start']}-{p['page_end']}\n    {p['text'][:200]}...\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
