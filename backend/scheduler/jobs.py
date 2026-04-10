from __future__ import annotations
import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from config import get_settings

logger = logging.getLogger(__name__)

_scheduler: AsyncIOScheduler | None = None


async def _scrape_job() -> None:
    """Scheduled job: runs the full web scrape."""
    from services.scraper import run_full_scrape
    logger.info("Scheduled scrape job starting...")
    try:
        results = await run_full_scrape()
        total = sum(r["ingested"] for r in results)
        logger.info(f"Scheduled scrape complete: {total} pages ingested.")
    except Exception as e:
        logger.error(f"Scheduled scrape failed: {e}", exc_info=True)


def start_scheduler() -> AsyncIOScheduler:
    global _scheduler
    settings = get_settings()

    _scheduler = AsyncIOScheduler(timezone="Asia/Kolkata")
    _scheduler.add_job(
        _scrape_job,
        trigger=CronTrigger(
            hour=settings.scrape_cron_hour,
            minute=settings.scrape_cron_minute,
        ),
        id="web_scrape",
        name="BondScanner Web Scrape",
        replace_existing=True,
        misfire_grace_time=3600,  # allow 1h grace if server was down
    )

    _scheduler.start()
    next_run = _scheduler.get_job("web_scrape").next_run_time
    logger.info(f"Scheduler started. Next scrape at: {next_run}")
    return _scheduler


def stop_scheduler() -> None:
    global _scheduler
    if _scheduler and _scheduler.running:
        _scheduler.shutdown(wait=False)
        logger.info("Scheduler stopped.")
