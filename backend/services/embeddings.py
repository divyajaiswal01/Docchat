"""
Generates embeddings locally with fastembed (ONNX runtime).

Why local instead of an API: Groq doesn't offer an embeddings endpoint, and
this avoids adding a second paid/rate-limited API into the pipeline.

Why fastembed instead of sentence-transformers: it runs the exact same
all-MiniLM-L6-v2 model, but through ONNX Runtime instead of PyTorch. PyTorch
alone needs several hundred MB of RAM just to load, which crashed the 512MB
free-tier Render instance. ONNX Runtime uses a fraction of that.
"""

from config import EMBEDDING_CACHE_DIR, EMBEDDING_MODEL_NAME

_model = None

# Small batches + a single thread keep peak memory low on tiny instances.
_BATCH_SIZE = 16


def _get_model():
    global _model
    if _model is None:
        # Imported lazily so importing this module (e.g. in tests) is cheap.
        from fastembed import TextEmbedding

        _model = TextEmbedding(
            model_name=EMBEDDING_MODEL_NAME,
            cache_dir=EMBEDDING_CACHE_DIR,
            threads=1,
        )
    return _model


def warm_up() -> None:
    """Downloads/loads the model. Run at build time so the first real
    upload doesn't have to wait for a ~90MB download."""
    _get_model()


def embed_texts(texts: list[str]) -> list[list[float]]:
    """Embeds a batch of texts. Returns one vector (as a plain list) per text."""
    model = _get_model()
    return [vector.tolist() for vector in model.embed(texts, batch_size=_BATCH_SIZE)]


def embed_query(text: str) -> list[float]:
    """Embeds a single query string."""
    return embed_texts([text])[0]
