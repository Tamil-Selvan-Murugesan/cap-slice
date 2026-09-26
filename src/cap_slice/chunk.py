"""Split extracted pages into overlapping chunks that remember their pages.

Sizes are in words, which keeps this independent of any tokenizer. Filings
average ~1.56 Voyage tokens per word, so defaults give ~840-token chunks
(more for number-heavy text).
"""

from __future__ import annotations

from dataclasses import dataclass

from cap_slice.extract import Page

CHUNK_WORDS = 500
OVERLAP_WORDS = 75


@dataclass
class Chunk:
    index: int
    text: str
    page_start: int
    page_end: int


def _paragraphs(pages: list[Page]) -> list[tuple[int, list[str]]]:
    """(page number, words) per paragraph, in document order."""
    out = []
    for page in pages:
        for para in page.text.split("\n\n"):
            words = para.split()
            # Very long "paragraphs" (tables, run-on text) are cut so one never
            # exceeds a chunk on its own.
            for i in range(0, len(words), CHUNK_WORDS):
                if piece := words[i:i + CHUNK_WORDS]:
                    out.append((page.number, piece))
    return out


def chunk_pages(pages: list[Page], chunk_words: int = CHUNK_WORDS,
                overlap_words: int = OVERLAP_WORDS) -> list[Chunk]:
    chunks: list[Chunk] = []
    # Each buffered entry is one word tagged with its page, so the overlap
    # carried into the next chunk keeps correct page numbers.
    buf: list[tuple[int, str]] = []

    def flush() -> None:
        if not buf:
            return
        chunks.append(Chunk(
            index=len(chunks),
            text=" ".join(w for _, w in buf),
            page_start=buf[0][0],
            page_end=buf[-1][0],
        ))

    for page_no, words in _paragraphs(pages):
        if buf and len(buf) + len(words) > chunk_words:
            flush()
            buf = buf[-overlap_words:] if overlap_words else []
        buf.extend((page_no, w) for w in words)
    if len(buf) > overlap_words or not chunks:
        flush()
    return chunks
