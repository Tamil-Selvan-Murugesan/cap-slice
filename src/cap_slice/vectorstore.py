"""Qdrant storage for document chunks.

Runs Qdrant in local (embedded) mode under data/qdrant/ - no server needed.
Set QDRANT_URL to point the same code at a Qdrant server instead.
"""

from __future__ import annotations

import os
import uuid
from pathlib import Path

from qdrant_client import QdrantClient, models

COLLECTION = "filings"
LOCAL_PATH = Path(__file__).resolve().parents[2] / "data" / "qdrant"
FILTER_FIELDS = ("symbol", "doc_type", "period_label", "doc_id")

# Fixed namespace so the same document + chunk always maps to the same point ID.
_NS = uuid.UUID("5b0f7a52-3c1e-4d7a-9a51-6f1a2c9e8d10")


def point_id(doc_id: str, chunk_index: int) -> str:
    return str(uuid.uuid5(_NS, f"{doc_id}#{chunk_index}"))


class ChunkStore:
    def __init__(self, collection: str = COLLECTION) -> None:
        url = os.environ.get("QDRANT_URL")
        self.client = QdrantClient(url=url) if url else QdrantClient(path=str(LOCAL_PATH))
        self.is_server = bool(url)
        self.collection = collection

    def close(self) -> None:
        self.client.close()

    def ensure_collection(self, dim: int) -> None:
        if self.client.collection_exists(self.collection):
            return
        self.client.create_collection(
            self.collection,
            vectors_config=models.VectorParams(size=dim, distance=models.Distance.COSINE),
        )
        # Payload indexes only take effect on a Qdrant server; local mode scans.
        for field in FILTER_FIELDS if self.is_server else ():
            self.client.create_payload_index(
                self.collection, field, models.PayloadSchemaType.KEYWORD)

    def _doc_filter(self, doc_id: str) -> models.Filter:
        return models.Filter(must=[models.FieldCondition(
            key="doc_id", match=models.MatchValue(value=doc_id))])

    def has_doc(self, doc_id: str, sha256: str) -> bool:
        """True if this exact file version is already fully indexed.

        Compares the stored point count with the n_chunks each point records,
        so a run interrupted mid-upsert doesn't leave a partial doc marked done.
        """
        if not self.client.collection_exists(self.collection):
            return False
        flt = self._doc_filter(doc_id)
        flt.must.append(models.FieldCondition(
            key="sha256", match=models.MatchValue(value=sha256)))
        points, _ = self.client.scroll(self.collection, scroll_filter=flt, limit=1,
                                       with_payload=["n_chunks"])
        if not points:
            return False
        stored = self.client.count(self.collection, count_filter=flt, exact=True).count
        return stored == points[0].payload.get("n_chunks")

    def replace_doc(self, doc_id: str, vectors: list[list[float]],
                    payloads: list[dict]) -> None:
        """Remove any earlier chunks of this document, then write the new ones."""
        self.client.delete(self.collection,
                           points_selector=models.FilterSelector(filter=self._doc_filter(doc_id)))
        points = [
            models.PointStruct(id=point_id(doc_id, p["chunk_index"]), vector=v, payload=p)
            for v, p in zip(vectors, payloads, strict=True)
        ]
        for i in range(0, len(points), 256):
            self.client.upsert(self.collection, points=points[i:i + 256])

    def search(self, vector: list[float], limit: int = 5,
               **filters: str) -> list[models.ScoredPoint]:
        flt = models.Filter(must=[
            models.FieldCondition(key=k, match=models.MatchValue(value=v))
            for k, v in filters.items() if v
        ]) if any(filters.values()) else None
        return self.client.query_points(self.collection, query=vector, query_filter=flt,
                                        limit=limit, with_payload=True).points
