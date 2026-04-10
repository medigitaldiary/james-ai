from __future__ import annotations
from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel

from services.scraper import run_full_scrape

router = APIRouter(prefix="/scraper", tags=["scraper"])


class ScrapeResult(BaseModel):
    seed: str
    ingested: int
    failed: int
    visited: int


class ScrapeResponse(BaseModel):
    message: str
    results: list[ScrapeResult] | None = None


@router.post("/run", response_model=ScrapeResponse)
async def trigger_scrape(background_tasks: BackgroundTasks):
    """
    Manually trigger a full scrape in the background.
    Returns immediately — scraping happens async.
    """
    background_tasks.add_task(_run_and_log)
    return ScrapeResponse(message="Scrape job started in background.")


@router.post("/run-sync", response_model=ScrapeResponse)
async def trigger_scrape_sync():
    """
    Trigger a full scrape synchronously (for testing/debugging).
    Waits until complete before returning.
    """
    try:
        results = await run_full_scrape()
        return ScrapeResponse(
            message=f"Scrape complete. {sum(r['ingested'] for r in results)} pages ingested.",
            results=[ScrapeResult(**r) for r in results],
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def _run_and_log():
    import logging
    logger = logging.getLogger(__name__)
    try:
        results = await run_full_scrape()
        total = sum(r["ingested"] for r in results)
        logger.info(f"Background scrape complete: {total} pages ingested.")
    except Exception as e:
        logger.error(f"Background scrape failed: {e}")
