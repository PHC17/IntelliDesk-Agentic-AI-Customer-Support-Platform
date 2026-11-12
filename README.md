# IntelliDesk — Agentic AI Customer Support Platform

IntelliDesk is an explainable customer-support platform built around
retrieval-augmented generation (RAG). Its long-term vision is hybrid search,
dynamic multi-agent routing, human escalation, and an evaluation dashboard.

## Week 1 progress

- FastAPI backend with health, PDF ingestion, and query endpoints.
- Page-aware overlapping chunks with document/page/chunk provenance.
- Local persistent ChromaDB vector store and Sentence Transformers embeddings.
- OpenAI-compatible grounded answer generation with source citations.
- Streamlit upload and chat UI.
- Starter answerable/unanswerable evaluation questions.

See [docs/architecture.md](docs/architecture.md) for the request flow.

## Run locally

```bash
cp .env.example .env
# Set OPENAI_API_KEY in .env
python3 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
pip install -r frontend/requirements.txt

export PYTHONPATH="$PWD/backend"
uvicorn app.main:app --reload --port 8000
```

In another terminal:

```bash
source .venv/bin/activate
streamlit run frontend/app.py
```

The API is available at `http://localhost:8000`, Swagger UI at
`http://localhost:8000/docs`, and the frontend at `http://localhost:8501`.
The first ingestion downloads the embedding model and may take a few minutes.

## Test with a sample PDF

```bash
curl http://localhost:8000/health
curl -X POST http://localhost:8000/documents \
  -F "file=@/path/to/sample.pdf;type=application/pdf"
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query":"What does the document say about refunds?"}'
```

The query response includes `answer` and `citations`; each citation has the
document name, one-based page number, relevant snippet, and confidence score.

## Docker

```bash
cp .env.example .env
docker compose up --build backend
```

PostgreSQL and Redis are available as optional compose profiles:
`docker compose --profile optional up`.

## Week 2 recommendations

1. Add hybrid BM25/vector retrieval, reranking, and duplicate-document handling.
2. Add authentication, rate limiting, structured request IDs, and async ingestion.
3. Add a citation-grounded evaluation runner using `data/evaluation/questions.json`.
4. Introduce PostgreSQL metadata, Redis job queues, and agent/tool routing.
5. Add automated tests with fixture PDFs and CI lint/type-check checks.
