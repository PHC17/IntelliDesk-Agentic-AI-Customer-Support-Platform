"""PDF text extraction."""

from io import BytesIO

from pypdf import PdfReader


def extract_pdf_pages(content: bytes) -> list[tuple[int, str]]:
    """Extract one text string per PDF page, using one-based page numbers."""
    if not content:
        raise ValueError("The uploaded PDF is empty.")
    reader = PdfReader(BytesIO(content))
    return [(index + 1, page.extract_text() or "") for index, page in enumerate(reader.pages)]
