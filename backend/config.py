from __future__ import annotations
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore", env_ignore_empty=True)

    # Anthropic (LLM)
    anthropic_api_key: str

    # Claude model — override via CLAUDE_MODEL in .env
    claude_model: str = "claude-3-5-haiku-20241022"

    # Gemini (embeddings only — not used for chat)
    gemini_api_key: str
    gemini_embedding_model: str = "models/gemini-embedding-001"
    embedding_dimensions: int = 768

    # Neon DB
    database_url: str

    # App
    environment: str = "development"
    cors_origins: str = "http://localhost:5173"

    # RAG
    rag_top_k: int = 5
    chunk_size: int = 500
    chunk_overlap: int = 50

    # Scraper
    scrape_urls: str = "https://bondscanner.com"
    scrape_cron_hour: int = 2
    scrape_cron_minute: int = 0

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",")]

    @property
    def scrape_urls_list(self) -> list[str]:
        return [u.strip() for u in self.scrape_urls.split(",")]


@lru_cache
def get_settings() -> Settings:
    return Settings()
