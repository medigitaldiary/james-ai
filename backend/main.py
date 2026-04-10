import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import get_settings
from db.client import get_pool, close_pool
from scheduler.jobs import start_scheduler, stop_scheduler
from routers import chat, kb, scraper, feedback

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s — %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # ── Startup ──────────────────────────────────────────────
    logger.info("Starting James AI backend...")
    await get_pool()           # warm up DB connection pool
    start_scheduler()          # start daily scrape cron
    logger.info("James AI backend ready.")

    yield

    # ── Shutdown ─────────────────────────────────────────────
    stop_scheduler()
    await close_pool()
    logger.info("James AI backend shut down cleanly.")


settings = get_settings()

app = FastAPI(
    title="James AI — BondScanner",
    description="RAG-powered AI assistant for BondScanner (SEBI-compliant OBPP)",
    version="0.1.0",
    lifespan=lifespan,
)

# ── CORS ──────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(chat.router)
app.include_router(kb.router)
app.include_router(scraper.router)
app.include_router(feedback.router)


# ── Health check ─────────────────────────────────────────────────────────────
@app.get("/health", tags=["meta"])
async def health():
    return {"status": "ok", "service": "james-ai"}
