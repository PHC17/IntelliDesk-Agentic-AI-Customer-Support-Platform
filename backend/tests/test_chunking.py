from app.retrieval.chunking import chunk_pages


def test_chunking_preserves_page_metadata_and_overlap() -> None:
    chunks = chunk_pages(
        [(1, "alpha " * 30)],
        document_name="guide.pdf",
        chunk_size=40,
        chunk_overlap=10,
    )
    assert len(chunks) > 1
    assert all(chunk.document_name == "guide.pdf" for chunk in chunks)
    assert all(chunk.page_number == 1 for chunk in chunks)
    assert chunks[0].chunk_id.startswith("guide.pdf:1:")
    assert chunks[0].text[-10:] in chunks[1].text
