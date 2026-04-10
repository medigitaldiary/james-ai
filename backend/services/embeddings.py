from __future__ import annotations
import google.generativeai as genai
from tenacity import retry, stop_after_attempt, wait_exponential
from config import get_settings

_configured = False


def _ensure_configured() -> None:
    global _configured
    if not _configured:
        settings = get_settings()
        genai.configure(api_key=settings.gemini_api_key)
        _configured = True


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
async def embed_text(text: str) -> list[float]:
    """Embed a single text string — output truncated to 768 dims for pgvector compatibility."""
    _ensure_configured()
    settings = get_settings()
    result = genai.embed_content(
        model=settings.gemini_embedding_model,
        content=text,
        task_type="retrieval_document",
        output_dimensionality=settings.embedding_dimensions,
    )
    return result["embedding"]


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
async def embed_query(text: str) -> list[float]:
    """Embed a query string (retrieval_query task type for better recall)."""
    _ensure_configured()
    settings = get_settings()
    result = genai.embed_content(
        model=settings.gemini_embedding_model,
        content=text,
        task_type="retrieval_query",
        output_dimensionality=settings.embedding_dimensions,
    )
    return result["embedding"]


async def embed_batch(texts: list[str]) -> list[list[float]]:
    """Embed a list of texts one by one (Gemini free tier has no batch endpoint)."""
    embeddings: list[list[float]] = []
    for text in texts:
        emb = await embed_text(text)
        embeddings.append(emb)
    return embeddings
