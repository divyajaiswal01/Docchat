"""
Tests the retrieval logic (store_chunks + query_chunks) without loading the
real sentence-transformers model — that model is slow to load and its exact
output isn't what we're testing here. Instead we substitute a tiny fake
embedding function with vectors we fully control, so we can assert exactly
which chunk should come back for a given question.
"""

import uuid

import pytest

import services.vector_store as vector_store
from services.chunker import Chunk


# Fixed 2D vectors we control completely. "Refund" and "shipping" point in
# clearly different directions, so a question embedded near one should
# retrieve the matching chunk, not the other.
_FAKE_VECTORS = {
    "chunk about refunds": [1.0, 0.0],
    "chunk about shipping": [0.0, 1.0],
    "refund question": [0.95, 0.05],
    "shipping question": [0.05, 0.95],
}


def _fake_embed_texts(texts):
    return [_FAKE_VECTORS[t] for t in texts]


def _fake_embed_query(text):
    return _FAKE_VECTORS[text]


@pytest.fixture(autouse=True)
def isolate_vector_store(tmp_path, monkeypatch):
    """Each test gets its own throwaway Chroma directory and a fresh client,
    so tests can't see each other's data or the real chroma_data/ folder."""
    monkeypatch.setattr(vector_store, "CHROMA_PERSIST_DIR", str(tmp_path))
    monkeypatch.setattr(vector_store, "_client", None)
    monkeypatch.setattr(vector_store, "embed_texts", _fake_embed_texts)
    monkeypatch.setattr(vector_store, "embed_query", _fake_embed_query)
    yield


def _chunk(text: str, page: int, index: int) -> Chunk:
    return Chunk(text=text, page=page, chunk_index=index)


def test_query_returns_the_most_relevant_chunk():
    document_id = str(uuid.uuid4())
    chunks = [
        _chunk("chunk about refunds", page=1, index=0),
        _chunk("chunk about shipping", page=2, index=0),
    ]

    vector_store.store_chunks(document_id, chunks)
    results = vector_store.query_chunks(document_id, "refund question", top_k=1)

    assert len(results) == 1
    assert results[0]["text"] == "chunk about refunds"
    assert results[0]["page"] == 1


def test_different_question_retrieves_the_other_chunk():
    document_id = str(uuid.uuid4())
    chunks = [
        _chunk("chunk about refunds", page=1, index=0),
        _chunk("chunk about shipping", page=2, index=0),
    ]

    vector_store.store_chunks(document_id, chunks)
    results = vector_store.query_chunks(document_id, "shipping question", top_k=1)

    assert results[0]["text"] == "chunk about shipping"
    assert results[0]["page"] == 2


def test_unknown_document_id_returns_empty_list():
    results = vector_store.query_chunks("no-such-document", "refund question", top_k=4)
    assert results == []


def test_storing_no_chunks_is_a_no_op():
    document_id = str(uuid.uuid4())
    vector_store.store_chunks(document_id, [])  # should not raise

    results = vector_store.query_chunks(document_id, "refund question", top_k=4)
    assert results == []
