"""Domain models used by document ingestion and retrieval."""

from pydantic import BaseModel, Field


class Chunk(BaseModel):
    """A searchable text segment and its source metadata."""

    text: str = Field(min_length=1)
    document_name: str
    page_number: int = Field(ge=1)
    chunk_id: str


class Citation(BaseModel):
    """A source reference returned with an answer."""

    document_name: str
    page_number: int = Field(ge=1)
    snippet: str
    confidence: float = Field(ge=0, le=1)


class QueryRequest(BaseModel):
    """A user question sent to the RAG endpoint."""

    query: str = Field(min_length=1, max_length=4000)
    top_k: int | None = Field(default=None, ge=1, le=20)


class QueryResponse(BaseModel):
    """An answer and its explainability metadata."""

    answer: str
    citations: list[Citation]
