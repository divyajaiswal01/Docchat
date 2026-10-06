"""
Splits per-page text into overlapping chunks.

Overlap matters: without it, an answer that spans a chunk boundary can get
cut in half and retrieval misses it. We use a character-based sliding
window — simple, dependency-free, and good enough for this project.
"""

from config import CHUNK_OVERLAP_CHARS, CHUNK_SIZE_CHARS


class Chunk:
    def __init__(self, text: str, page: int, chunk_index: int):
        self.text = text
        self.page = page
        self.chunk_index = chunk_index

    @property
    def id(self) -> str:
        return f"page{self.page}-chunk{self.chunk_index}"


def chunk_pages(pages_text: list[str]) -> list[Chunk]:
    """
    pages_text[i] is the text of page i+1 (1-indexed pages).
    Returns a flat list of Chunk objects across the whole document.
    """
    chunks: list[Chunk] = []

    for page_number, page_text in enumerate(pages_text, start=1):
        page_text = page_text.strip()
        if not page_text:
            continue

        start = 0
        chunk_index = 0
        while start < len(page_text):
            end = start + CHUNK_SIZE_CHARS
            chunk_text = page_text[start:end].strip()

            if chunk_text:
                chunks.append(Chunk(text=chunk_text, page=page_number, chunk_index=chunk_index))
                chunk_index += 1

            if end >= len(page_text):
                break
            start = end - CHUNK_OVERLAP_CHARS

    return chunks
