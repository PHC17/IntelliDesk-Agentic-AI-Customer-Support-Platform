"""ChromaDB persistence adapter."""

from functools import lru_cache
from typing import Any

import chromadb

from app.core.config import get_settings


@lru_cache
def get_collection() -> Any:
    """Return the persistent document collection."""
    client = chromadb.PersistentClient(path=str(get_settings().chroma_persist_directory))
    return client.get_or_create_collection(
        name="intellidesk_documents",
        metadata={"hnsw:space": "cosine"},
    )
