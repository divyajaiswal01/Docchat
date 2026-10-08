"""
Tests the wrapper logic in services/embeddings.py without downloading the
real model: we swap in a fake TextEmbedding that returns known vectors.
"""

import numpy as np
import pytest

import services.embeddings as embeddings


class FakeTextEmbedding:
    def __init__(self, **kwargs):
        self.init_kwargs = kwargs
        self.batch_sizes_seen = []

    def embed(self, texts, batch_size=256):
        self.batch_sizes_seen.append(batch_size)
        for text in texts:
            yield np.array([float(len(text)), 1.0], dtype=np.float32)


@pytest.fixture(autouse=True)
def fake_model(monkeypatch):
    fake = FakeTextEmbedding()
    monkeypatch.setattr(embeddings, "_model", fake)
    yield fake


def test_embed_texts_returns_plain_python_lists():
    result = embeddings.embed_texts(["abc", "hello"])

    assert result == [[3.0, 1.0], [5.0, 1.0]]
    assert all(isinstance(v, list) for v in result)


def test_embed_query_returns_a_single_vector():
    assert embeddings.embed_query("abcd") == [4.0, 1.0]


def test_uses_small_batch_size_to_limit_memory(fake_model):
    embeddings.embed_texts(["a", "b"])
    assert fake_model.batch_sizes_seen == [embeddings._BATCH_SIZE]
    assert embeddings._BATCH_SIZE <= 16
