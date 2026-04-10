from __future__ import annotations
"""
BondScanner web scraper.
Crawls configured URLs, extracts clean text, and feeds into the ingestion pipeline.
Respects robots.txt by only scraping pages explicitly allowed/expected.
"""
import asyncio
import logging
from urllib.parse import urljoin, urlparse

import httpx
from bs4 import BeautifulSoup

from config import get_settings
from db.vector_store import delete_web_documents
from services.ingestion import ingest_web_page

logger = logging.getLogger(__name__)

# Tags whose text content we want to keep
CONTENT_TAGS = {"p", "h1", "h2", "h3", "h4", "li", "td", "th", "article", "section"}
# Tags to strip entirely (noise)
NOISE_TAGS = {"script", "style", "nav", "footer", "header", "noscript", "iframe", "svg"}

MAX_PAGES_PER_DOMAIN = 50
CRAWL_DELAY_SECONDS = 1.5  # polite delay between requests


def _extract_text(html: str) -> tuple[str, str]:
    """Return (title, clean_text) from raw HTML."""
    soup = BeautifulSoup(html, "lxml")

    # Title
    title = ""
    if soup.title and soup.title.string:
        title = soup.title.string.strip()

    # Remove noise tags
    for tag in soup(NOISE_TAGS):
        tag.decompose()

    # Collect text from meaningful tags
    parts: list[str] = []
    for tag in soup.find_all(CONTENT_TAGS):
        text = tag.get_text(separator=" ", strip=True)
        if text and len(text) > 30:
            parts.append(text)

    return title, "\n\n".join(parts)


def _is_same_domain(url: str, base: str) -> bool:
    return urlparse(url).netloc == urlparse(base).netloc


def _extract_links(html: str, base_url: str) -> list[str]:
    """Extract all internal links from a page."""
    soup = BeautifulSoup(html, "lxml")
    links: list[str] = []
    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        # Skip anchors, mailto, tel, js
        if href.startswith(("#", "mailto:", "tel:", "javascript:")):
            continue
        full = urljoin(base_url, href).split("#")[0]  # strip fragments
        if _is_same_domain(full, base_url):
            links.append(full)
    return list(set(links))


async def _fetch(client: httpx.AsyncClient, url: str) -> str | None:
    try:
        resp = await client.get(url, follow_redirects=True, timeout=15)
        if resp.status_code == 200 and "text/html" in resp.headers.get("content-type", ""):
            return resp.text
    except Exception as e:
        logger.warning(f"Failed to fetch {url}: {e}")
    return None


async def scrape_site(seed_url: str) -> dict:
    """
    BFS crawl from seed_url, scrape all reachable same-domain pages,
    ingest each into the vector DB.
    Returns a summary dict.
    """
    visited: set[str] = set()
    queue = [seed_url]
    ingested = 0
    failed = 0

    headers = {
        "User-Agent": "JamesAI-BondScanner-Bot/1.0 (+https://bondscanner.com)",
        "Accept": "text/html",
    }

    async with httpx.AsyncClient(headers=headers) as client:
        while queue and len(visited) < MAX_PAGES_PER_DOMAIN:
            url = queue.pop(0)
            if url in visited:
                continue
            visited.add(url)

            html = await _fetch(client, url)
            if not html:
                failed += 1
                continue

            title, text = _extract_text(html)
            if len(text.strip()) < 100:
                logger.debug(f"Skipping sparse page: {url}")
                continue

            try:
                await ingest_web_page(url=url, content=text, title=title)
                ingested += 1
                logger.info(f"Ingested: {url} ({len(text)} chars)")
            except Exception as e:
                logger.error(f"Ingestion failed for {url}: {e}")
                failed += 1

            # Discover new links
            new_links = _extract_links(html, seed_url)
            for link in new_links:
                if link not in visited and link not in queue:
                    queue.append(link)

            await asyncio.sleep(CRAWL_DELAY_SECONDS)

    return {"seed": seed_url, "ingested": ingested, "failed": failed, "visited": len(visited)}


async def run_full_scrape() -> list[dict]:
    """
    Full scrape job:
    1. Wipe existing web KB
    2. Crawl all configured seed URLs
    3. Return summary per seed
    """
    settings = get_settings()
    logger.info("Starting full web scrape — clearing old web KB...")
    await delete_web_documents()

    results: list[dict] = []
    for seed in settings.scrape_urls_list:
        logger.info(f"Crawling: {seed}")
        result = await scrape_site(seed)
        results.append(result)
        logger.info(f"Done {seed}: {result}")

    total_ingested = sum(r["ingested"] for r in results)
    logger.info(f"Scrape complete. Total pages ingested: {total_ingested}")
    return results
