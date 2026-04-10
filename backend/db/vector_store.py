from __future__ import annotations
import json
import uuid
from db.client import get_pool


# ── KB Files ──────────────────────────────────────────────────────────────────

async def create_kb_file(
    name: str,
    size: int,
    source: str,  # 'pdf' | 'web'
    url: str | None = None,
    status: str = "ready",
) -> dict:
    pool = await get_pool()
    row = await pool.fetchrow(
        """
        INSERT INTO kb_files (name, size, source, url, status)
        VALUES ($1, $2, $3, $4, $5)
        RETURNING id, name, size, source, url, status, uploaded_at
        """,
        name, size, source, url, status,
    )
    return dict(row)


async def list_kb_files() -> list[dict]:
    pool = await get_pool()
    rows = await pool.fetch(
        "SELECT id, name, size, source, url, status, uploaded_at FROM kb_files ORDER BY uploaded_at DESC"
    )
    return [dict(r) for r in rows]


async def get_kb_file(file_id: str) -> dict | None:
    pool = await get_pool()
    row = await pool.fetchrow(
        "SELECT id, name, size, source, url, status, uploaded_at FROM kb_files WHERE id = $1",
        uuid.UUID(file_id),
    )
    return dict(row) if row else None


async def delete_kb_file(file_id: str) -> bool:
    pool = await get_pool()
    result = await pool.execute(
        "DELETE FROM kb_files WHERE id = $1", uuid.UUID(file_id)
    )
    return result == "DELETE 1"


async def update_kb_file_status(file_id: str, status: str) -> None:
    pool = await get_pool()
    await pool.execute(
        "UPDATE kb_files SET status = $1 WHERE id = $2",
        status, uuid.UUID(file_id),
    )


# ── Documents (chunks) ────────────────────────────────────────────────────────

async def insert_document(
    kb_file_id: str,
    content: str,
    embedding: list[float],
    metadata: dict | None = None,
) -> str:
    pool = await get_pool()
    row = await pool.fetchrow(
        """
        INSERT INTO documents (kb_file_id, content, embedding, metadata)
        VALUES ($1, $2, $3::vector, $4)
        RETURNING id
        """,
        uuid.UUID(kb_file_id),
        content,
        str(embedding),        # pgvector accepts '[x,y,z,...]' string format
        json.dumps(metadata or {}),
    )
    return str(row["id"])


async def similarity_search(
    query_embedding: list[float],
    top_k: int = 5,
    kb_file_ids: list[str] | None = None,
) -> list[dict]:
    """
    Return top_k most similar document chunks to the query embedding.
    Optionally filter to specific KB file IDs.
    """
    pool = await get_pool()

    if kb_file_ids:
        uuids = [uuid.UUID(fid) for fid in kb_file_ids]
        rows = await pool.fetch(
            """
            SELECT d.id, d.content, d.metadata, d.kb_file_id,
                   1 - (d.embedding <=> $1::vector) AS similarity
            FROM documents d
            WHERE d.kb_file_id = ANY($2::uuid[])
            ORDER BY d.embedding <=> $1::vector
            LIMIT $3
            """,
            str(query_embedding), uuids, top_k,
        )
    else:
        rows = await pool.fetch(
            """
            SELECT d.id, d.content, d.metadata, d.kb_file_id,
                   1 - (d.embedding <=> $1::vector) AS similarity
            FROM documents d
            ORDER BY d.embedding <=> $1::vector
            LIMIT $2
            """,
            str(query_embedding), top_k,
        )

    return [dict(r) for r in rows]


async def delete_documents_by_file(file_id: str) -> None:
    """Cascade delete is handled by FK, but explicit call for clarity."""
    pool = await get_pool()
    await pool.execute(
        "DELETE FROM documents WHERE kb_file_id = $1", uuid.UUID(file_id)
    )


async def delete_web_documents() -> None:
    """Remove all web-sourced chunks before a fresh scrape."""
    pool = await get_pool()
    await pool.execute(
        "DELETE FROM documents WHERE kb_file_id IN (SELECT id FROM kb_files WHERE source = 'web')"
    )
    await pool.execute("DELETE FROM kb_files WHERE source = 'web'")
