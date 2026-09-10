"""
rag/embeddings.py
------------------
Wraps Sentence Transformers to turn text into embedding vectors.

The model is loaded lazily (only once) and cached at module level so that
Streamlit re-runs do not reload it repeatedly.
"""

from typing import List
import numpy as np

from config.config import Config

_model = None  # Module-level cache for the loaded SentenceTransformer model.


def get_embedding_model():
    """Load (once) and return the SentenceTransformer embedding model."""
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer

        _model = SentenceTransformer(Config.EMBEDDING_MODEL_NAME)
    return _model


def embed_texts(texts: List[str]) -> np.ndarray:
    """Embed a list of strings and return a numpy array of shape (N, D)."""
    if not texts:
        return np.array([])
    model = get_embedding_model()
    embeddings = model.encode(
        texts, convert_to_numpy=True, show_progress_bar=False, normalize_embeddings=True
    )
    return embeddings


def embed_query(query: str) -> np.ndarray:
    """Embed a single query string and return a 1D numpy vector."""
    result = embed_texts([query])
    if result.size == 0:
        return result
    return result[0]
