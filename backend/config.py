"""
Shared constants. Centralized here so Phase 3+ tuning (chunk size, top_k,
etc.) doesn't mean hunting through multiple files.
"""

import os

# --- Chunking ---
# Character-based, not token-based — good enough approximation without
# pulling in a tokenizer dependency. ~2000 chars ≈ ~500 tokens for English text.
CHUNK_SIZE_CHARS = 2000
CHUNK_OVERLAP_CHARS = 200

# --- Embeddings ---
# Runs locally via sentence-transformers — free, no API key, no internet
# needed after the first download of the model weights.
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"

# --- Retrieval ---
TOP_K_CHUNKS = 4

# --- Vector store ---
CHROMA_PERSIST_DIR = os.path.join(os.path.dirname(__file__), "chroma_data")

# --- Upload limits ---
MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB

# --- Usage limits ---
# Caps questions per document so a free API key (and your own time) don't
# get burned by one runaway session. Each new upload gets a fresh count.
MAX_QUESTIONS_PER_DOCUMENT = 20
