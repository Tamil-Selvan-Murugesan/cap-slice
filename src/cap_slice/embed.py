"""Embed text with Voyage AI.

Reads VOYAGE_API_KEY from the environment. VOYAGE_MODEL overrides the model
(default voyage-finance-2: 1024-dim, 32K context, 120K tokens per request).
"""

from __future__ import annotations

import os

import voyageai

DEFAULT_MODEL = "voyage-finance-2"
# Per-request caps: 1,000 texts and 120K tokens for voyage-finance-2. Batches
# are sized by token count (tokenizer runs locally) with headroom below that.
MAX_BATCH_TEXTS = 128
MAX_BATCH_TOKENS = 100_000


class VoyageEmbedder:
    def __init__(self, model: str | None = None) -> None:
        self.model = model or os.environ.get("VOYAGE_MODEL", DEFAULT_MODEL)
        self.client = voyageai.Client(max_retries=5)  # uses VOYAGE_API_KEY

    def _batches(self, texts: list[str]) -> list[list[str]]:
        batches: list[list[str]] = [[]]
        used = 0
        for text in texts:
            n = self.client.count_tokens([text], model=self.model)
            if batches[-1] and (used + n > MAX_BATCH_TOKENS
                                or len(batches[-1]) >= MAX_BATCH_TEXTS):
                batches.append([])
                used = 0
            batches[-1].append(text)
            used += n
        return [b for b in batches if b]

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        vectors: list[list[float]] = []
        for batch in self._batches(texts):
            result = self.client.embed(batch, model=self.model, input_type="document")
            vectors.extend(result.embeddings)
        return vectors

    def embed_query(self, text: str) -> list[float]:
        return self.client.embed([text], model=self.model,
                                 input_type="query").embeddings[0]
