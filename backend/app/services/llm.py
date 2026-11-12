"""OpenAI-compatible answer generation."""

import httpx

from app.core.config import get_settings
from app.retrieval.models import Chunk


async def generate_answer(query: str, retrieved: list[tuple[Chunk, float]]) -> str:
    """Generate a grounded answer from retrieved context using an OpenAI-compatible API."""
    settings = get_settings()
    if not settings.openai_api_key:
        raise RuntimeError("OPENAI_API_KEY is not configured.")
    context = "\n\n".join(
        f"[{chunk.document_name}, page {chunk.page_number}]\n{chunk.text}"
        for chunk, _ in retrieved
    )
    payload = {
        "model": settings.llm_model,
        "temperature": 0.1,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are a customer support assistant. Answer only from the provided context. "
                    "If the context does not support an answer, say you do not know and recommend "
                    "contacting support. Do not invent policies, prices, or citations."
                ),
            },
            {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {query}"},
        ],
    }
    headers = {"Authorization": f"Bearer {settings.openai_api_key}"}
    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.post(
            f"{settings.openai_base_url.rstrip('/')}/chat/completions",
            headers=headers,
            json=payload,
        )
    response.raise_for_status()
    data = response.json()
    return data["choices"][0]["message"]["content"].strip()
