"""Document ingestion service."""

from app.db.chroma import get_collection
from app.core.config import get_settings
from app.retrieval.chunking import chunk_pages
from app.retrieval.embeddings import embed_texts
from app.retrieval.models import Chunk
from app.retrieval.pdf import extract_pdf_pages


def ingest_pdf(content: bytes, document_name: str) -> int:
    """Extract, chunk, embed, and persist a PDF; return chunk count."""
    pages = extract_pdf_pages(content)
    chunks = chunk_pages(
        pages,
        document_name=document_name,
        chunk_size=get_settings().chunk_size,
        chunk_overlap=get_settings().chunk_overlap,
    )
    if not chunks:
        raise ValueError("The PDF did not contain extractable text.")
    embeddings = embed_texts([chunk.text for chunk in chunks])
    collection = get_collection()
    collection.upsert(
        ids=[chunk.chunk_id for chunk in chunks],
        documents=[chunk.text for chunk in chunks],
        metadatas=[chunk.model_dump(exclude={"text"}) for chunk in chunks],
        embeddings=embeddings,
    )
    return len(chunks)


def retrieve_chunks(query: str, top_k: int) -> list[tuple[Chunk, float]]:
    """Retrieve relevant chunks with normalized similarity confidence scores."""
    collection = get_collection()
    if collection.count() == 0:
        return []
    query_embedding = embed_texts([query])[0]
    result = collection.query(
        query_embeddings=[query_embedding],
        n_results=min(top_k, collection.count()),
        include=["documents", "metadatas", "distances"],
    )
    documents = result.get("documents", [[]])[0]
    metadatas = result.get("metadatas", [[]])[0]
    distances = result.get("distances", [[]])[0]
    retrieved: list[tuple[Chunk, float]] = []
    for text, metadata, distance in zip(documents, metadatas, distances):
        chunk = Chunk(text=text, **metadata)
        retrieved.append((chunk, max(0.0, min(1.0, 1.0 - float(distance)))))
    return retrieved
