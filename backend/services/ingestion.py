from __future__ import annotations
"""
Ingestion pipeline: raw text → chunks → embeddings → Neon DB
Used by both PDF upload and web scraper.
"""
import asyncio
from utils.chunker import chunk_text
from services.embeddings import embed_text
from db.vector_store import insert_document, create_kb_file, update_kb_file_status


EMBED_CONCURRENCY = 5  # max parallel embedding calls


async def ingest_text(
    text: str,
    kb_file_id: str,
    metadata_base: dict | None = None,
) -> int:
    """
    Chunk `text`, embed each chunk, store in vector DB.
    Returns the number of chunks stored.
    """
    chunks = chunk_text(text)
    if not chunks:
        return 0

    semaphore = asyncio.Semaphore(EMBED_CONCURRENCY)

    async def embed_and_store(i: int, chunk: str) -> None:
        async with semaphore:
            embedding = await embed_text(chunk)
            metadata = {**(metadata_base or {}), "chunk_index": i}
            await insert_document(
                kb_file_id=kb_file_id,
                content=chunk,
                embedding=embedding,
                metadata=metadata,
            )

    await asyncio.gather(*[embed_and_store(i, c) for i, c in enumerate(chunks)])
    return len(chunks)


async def ingest_pdf(
    file_bytes: bytes,
    filename: str,
    file_size: int,
) -> dict:
    """
    Full PDF ingestion flow:
    1. Create KB file record (status=uploading)
    2. Extract text
    3. Chunk + embed + store
    4. Mark status=ready
    Returns the KB file record.
    """
    from utils.pdf_parser import extract_text_from_pdf

    # Create file record immediately so the frontend gets an ID
    kb_file = await create_kb_file(
        name=filename,
        size=file_size,
        source="pdf",
        status="uploading",
    )
    kb_file_id = str(kb_file["id"])

    try:
        text = extract_text_from_pdf(file_bytes)
        if not text.strip():
            raise ValueError("PDF appears to be empty or image-only (no extractable text).")

        chunk_count = await ingest_text(
            text=text,
            kb_file_id=kb_file_id,
            metadata_base={"source": "pdf", "filename": filename},
        )

        await update_kb_file_status(kb_file_id, "ready")
        kb_file["status"] = "ready"
        kb_file["chunk_count"] = chunk_count
    except Exception as e:
        await update_kb_file_status(kb_file_id, "error")
        kb_file["status"] = "error"
        raise RuntimeError(f"PDF ingestion failed: {e}") from e

    return kb_file


async def ingest_web_page(
    url: str,
    content: str,
    title: str = "",
) -> dict:
    """
    Ingest a scraped web page.
    Creates a KB file record and stores chunks.
    """
    kb_file = await create_kb_file(
        name=title or url,
        size=len(content.encode()),
        source="web",
        url=url,
        status="uploading",
    )
    kb_file_id = str(kb_file["id"])

    try:
        chunk_count = await ingest_text(
            text=content,
            kb_file_id=kb_file_id,
            metadata_base={"source": "web", "url": url, "title": title},
        )
        await update_kb_file_status(kb_file_id, "ready")
        kb_file["status"] = "ready"
        kb_file["chunk_count"] = chunk_count
    except Exception as e:
        await update_kb_file_status(kb_file_id, "error")
        raise RuntimeError(f"Web ingestion failed for {url}: {e}") from e

    return kb_file
