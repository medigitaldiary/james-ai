import io
from pypdf import PdfReader


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extract all text from a PDF given its raw bytes."""
    reader = PdfReader(io.BytesIO(file_bytes))
    parts: list[str] = []

    for page_num, page in enumerate(reader.pages, start=1):
        text = page.extract_text()
        if text and text.strip():
            # Tag each page so metadata can reference it later
            parts.append(f"[Page {page_num}]\n{text.strip()}")

    return "\n\n".join(parts)
