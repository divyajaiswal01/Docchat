"""
Generates embeddings locally with sentence-transformers.

Why local instead of an API: Groq doesn't offer an embeddings endpoint, and
this avoids adding a second paid/rate-limited API into the pipeline. The
model downloads once (~80MB) on first run, then works offline.
"""

from config import EMBEDDING_MODEL_NAME

_model = None


def _get_model():
    global _model
    if _model is None:
        # Imported lazily — this import pulls in torch, which is slow to
        # load, so we only pay that cost on the first real embedding call.
        from sentence_transformers import SentenceTransformer

        _model = SentenceTransformer(EMBEDDING_MODEL_NAME)
    return _model


def embed_texts(texts: list[str]) -> list[list[float]]:
    """Embeds a batch of texts. Returns one vector (as a plain list) per text."""
    model = _get_model()
    vectors = model.encode(texts, convert_to_numpy=True, show_progress_bar=False)
    return vectors.tolist()


def embed_query(text: str) -> list[float]:
    """Embeds a single query string."""
    return embed_texts([text])[0]
