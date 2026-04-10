from __future__ import annotations
from config import get_settings


def chunk_text(text: str, chunk_size: int | None = None, overlap: int | None = None) -> list[str]:
    """
    Split text into overlapping chunks by word count.
    Respects paragraph boundaries where possible.
    """
    settings = get_settings()
    chunk_size = chunk_size or settings.chunk_size
    overlap = overlap or settings.chunk_overlap

    # Split into paragraphs first to preserve context boundaries
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]

    chunks: list[str] = []
    current_words: list[str] = []

    for para in paragraphs:
        para_words = para.split()

        # If a single paragraph exceeds chunk_size, break it up
        if len(para_words) > chunk_size:
            # Flush current buffer first
            if current_words:
                chunks.append(" ".join(current_words))
                current_words = current_words[-overlap:] if overlap else []

            # Slide through the large paragraph
            for i in range(0, len(para_words), chunk_size - overlap):
                window = para_words[i : i + chunk_size]
                if window:
                    chunks.append(" ".join(window))
            continue

        # Would adding this paragraph overflow the chunk?
        if len(current_words) + len(para_words) > chunk_size:
            if current_words:
                chunks.append(" ".join(current_words))
                # Keep overlap words from the end for continuity
                current_words = current_words[-overlap:] if overlap else []

        current_words.extend(para_words)

    # Flush any remaining words
    if current_words:
        chunks.append(" ".join(current_words))

    return [c for c in chunks if len(c.strip()) > 20]  # drop tiny fragments
