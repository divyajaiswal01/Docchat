"""
Thin wrapper around Chroma (local, file-based vector store — free, no infra).

One collection per uploaded document, named by document_id, so documents
never leak into each other's retrieval results.
"""

import chromadb

from config import CHROMA_PERSIST_DIR
from services.chunker import Chunk
from services.embeddings import embed_query, embed_texts

_client = None


def _get_client():
    global _client
    if _client is None:
        _client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)
    return _client


def _collection_name(document_id: str) -> str:
    return f"doc_{document_id}"


def store_chunks(document_id: str, chunks: list[Chunk]) -> None:
    if not chunks:
        return

    client = _get_client()
    collection = client.get_or_create_collection(name=_collection_name(document_id))

    texts = [c.text for c in chunks]
    embeddings = embed_texts(texts)

    collection.add(
        ids=[c.id for c in chunks],
        embeddings=embeddings,
        documents=texts,
        metadatas=[{"page": c.page} for c in chunks],
    )


def query_chunks(document_id: str, question: str, top_k: int) -> list[dict]:
    """
    Returns the top_k most relevant chunks for the question, each as
    {"text": ..., "page": ...}. Returns [] if the document has no chunks
    (e.g. document_id doesn't exist).
    """
    client = _get_client()
    try:
        collection = client.get_collection(name=_collection_name(document_id))
    except Exception:
        return []

    if collection.count() == 0:
        return []

    query_embedding = embed_query(question)
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=min(top_k, collection.count()),
    )

    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]

    return [
        {"text": doc, "page": meta.get("page")}
        for doc, meta in zip(documents, metadatas)
    ]
