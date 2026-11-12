"""Lazy sentence-transformers embedding provider."""

from functools import lru_cache

from sentence_transformers import SentenceTransformer

from app.core.config import get_settings


@lru_cache
def get_embedding_model() -> SentenceTransformer:
    """Load the embedding model once per process."""
    return SentenceTransformer(get_settings().embedding_model)


def embed_texts(texts: list[str]) -> list[list[float]]:
    """Encode text into normalized vectors for cosine similarity."""
    if not texts:
        return []
    vectors = get_embedding_model().encode(
        texts,
        normalize_embeddings=True,
        show_progress_bar=False,
    )
    return vectors.tolist()
