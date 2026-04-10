from __future__ import annotations
"""
RAG retrieval service.
Given a user query, retrieve the most relevant chunks from the vector DB
and return them as context for the LLM.
"""
import logging
from services.embeddings import embed_query
from db.vector_store import similarity_search
from config import get_settings

logger = logging.getLogger(__name__)


async def retrieve_context(
    query: str,
    kb_file_ids: list[str] | None = None,
    top_k: int | None = None,
) -> list[str]:
    """
    Embed the query, retrieve top-k similar chunks.
    Returns a list of text chunks ready to inject into the system prompt.
    """
    settings = get_settings()
    k = top_k or settings.rag_top_k

    query_embedding = await embed_query(query)

    results = await similarity_search(
        query_embedding=query_embedding,
        top_k=k,
        kb_file_ids=kb_file_ids if kb_file_ids else None,
    )

    # Filter out low-confidence results (similarity < 0.3)
    relevant = [r for r in results if float(r.get("similarity", 0)) >= 0.3]

    # Log retrieved sources
    logger.info("─── RAG SOURCES for query: %r ───", query[:80])
    if relevant:
        for i, r in enumerate(relevant, 1):
            meta = r.get("metadata") or {}
            source_url = meta.get("url", "web-scrape") if isinstance(meta, dict) else "web-scrape"
            similarity = float(r.get("similarity", 0))
            preview = r["content"][:120].replace("\n", " ")
            logger.info(
                "  [%d] score=%.3f | source=%s | %s…",
                i, similarity, source_url, preview,
            )
    else:
        logger.info("  No chunks above threshold — falling back to Claude general knowledge")

    return [r["content"] for r in relevant]


def build_messages(
    messages: list[dict],  # [{"role": "user"|"james", "content": str}]
) -> list[dict]:
    """
    Convert frontend message format to Anthropic's expected format.
    Anthropic uses "user" and "assistant" roles with a "content" string.
    Keeps last 20 turns max.
    """
    converted = []
    for msg in messages[-20:]:
        role = "assistant" if msg["role"] == "james" else "user"
        converted.append({"role": role, "content": msg["content"]})
    return converted
