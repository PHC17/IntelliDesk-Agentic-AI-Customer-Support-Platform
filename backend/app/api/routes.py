"""HTTP endpoints for health, ingestion, and querying."""

from fastapi import APIRouter, File, HTTPException, UploadFile, status
from pypdf.errors import PdfReadError

from app.core.config import get_settings
from app.retrieval.models import QueryRequest, QueryResponse
from app.services.ingestion import ingest_pdf, retrieve_chunks
from app.services.llm import generate_answer

router = APIRouter()


@router.get("/health")
async def health() -> dict[str, str]:
    """Return service readiness information."""
    return {"status": "ok", "service": get_settings().app_name}


@router.post("/documents", status_code=status.HTTP_201_CREATED)
async def upload_document(file: UploadFile = File(...)) -> dict[str, object]:
    """Ingest a PDF document into the local vector store."""
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=415, detail="Only PDF files are supported.")
    content = await file.read()
    max_bytes = get_settings().max_upload_size_mb * 1024 * 1024
    if len(content) > max_bytes:
        raise HTTPException(status_code=413, detail="The uploaded PDF exceeds the size limit.")
    try:
        chunk_count = ingest_pdf(content, file.filename or "uploaded.pdf")
    except (ValueError, PdfReadError, RuntimeError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return {"document_name": file.filename or "uploaded.pdf", "chunks_indexed": chunk_count}


@router.post("/query", response_model=QueryResponse)
async def query_documents(request: QueryRequest) -> QueryResponse:
    """Answer a question using retrieved chunks and return source citations."""
    settings = get_settings()
    retrieved = retrieve_chunks(request.query, request.top_k or settings.retrieval_top_k)
    if not retrieved:
        raise HTTPException(status_code=404, detail="No indexed documents were found.")
    try:
        answer = await generate_answer(request.query, retrieved)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    citations = [
        {
            "document_name": chunk.document_name,
            "page_number": chunk.page_number,
            "snippet": chunk.text[:500],
            "confidence": round(confidence, 4),
        }
        for chunk, confidence in retrieved
    ]
    return QueryResponse(answer=answer, citations=citations)
