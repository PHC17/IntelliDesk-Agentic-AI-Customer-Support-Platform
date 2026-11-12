"""Page-aware text chunking utilities."""

import re

from app.retrieval.models import Chunk


def _normalize_text(text: str) -> str:
    """Collapse layout whitespace without removing paragraph boundaries."""
    paragraphs = [re.sub(r"[ \t]+", " ", part).strip() for part in text.splitlines()]
    return "\n".join(part for part in paragraphs if part)


def chunk_pages(
    pages: list[tuple[int, str]],
    document_name: str,
    chunk_size: int,
    chunk_overlap: int,
) -> list[Chunk]:
    """Split pages into overlapping chunks while retaining page provenance."""
    if chunk_size <= 0 or chunk_overlap < 0 or chunk_overlap >= chunk_size:
        raise ValueError("chunk_overlap must be non-negative and smaller than chunk_size")

    chunks: list[Chunk] = []
    for page_number, raw_text in pages:
        text = _normalize_text(raw_text)
        if not text:
            continue
        start = 0
        page_chunk_index = 0
        while start < len(text):
            end = min(start + chunk_size, len(text))
            if end < len(text):
                boundary = max(text.rfind("\n", start, end), text.rfind(" ", start, end))
                if boundary > start + chunk_size // 2:
                    end = boundary
            chunk_text = text[start:end].strip()
            if chunk_text:
                chunks.append(
                    Chunk(
                        text=chunk_text,
                        document_name=document_name,
                        page_number=page_number,
                        chunk_id=f"{document_name}:{page_number}:{page_chunk_index}",
                    )
                )
                page_chunk_index += 1
            if end >= len(text):
                break
            start = max(end - chunk_overlap, start + 1)
    return chunks
