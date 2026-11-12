# Week 1 architecture

The FastAPI API accepts PDFs, extracts page text with `pypdf`, creates
overlapping page-aware chunks, embeds them with Sentence Transformers, and
persists them in a local ChromaDB collection. Queries embed the question,
retrieve the nearest chunks, send only that context to an OpenAI-compatible
chat completion endpoint, and return citations containing document, page,
snippet, and similarity confidence.

The Streamlit client is intentionally thin: it uploads documents and renders
the answer and citations returned by the API. This separation leaves room for
future agent routing, evaluation, authentication, and asynchronous ingestion.
