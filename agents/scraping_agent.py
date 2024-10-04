# File: scraping_agent.py
# Directory: my_app/agents/

# Overall Role and Purpose:
# - Scrapes the content of articles using the selected scrapers.
# - Asynchronously fetches content for each URL.

# Expected Inputs:
# - `SharedState` with `urls_to_be_processed` and `scraper_choices`.

# Expected Outputs:
# - Updates `articles` in the state with scraped content.

import asyncio
import logging
from models.state import SharedState
from tools.scraping.jina_scraper import JinaScraper
from tools.scraping.web_base_loader_scraper import WebBaseLoaderScraper

logger = logging.getLogger(__name__)

async def scraping_agent(state: SharedState):
    state.add_log("Starting article scraping.", level="INFO")
    tasks = []
    semaphore = asyncio.Semaphore(5)  # Limit concurrency to 5
    for url in state.urls_to_be_processed:
        scraper_name = state.scraper_choices.get(url)
        if scraper_name == "jina_scraper":
            tasks.append(scrape_with_jina(url, state, semaphore))
        elif scraper_name == "web_base_loader_scraper":
            tasks.append(scrape_with_web_base_loader(url, state, semaphore))
    await asyncio.gather(*tasks)
    state.add_log(f"Scraped {len(state.articles)} articles.", level="INFO")

async def scrape_with_jina(url: str, state: SharedState, semaphore):
    async with semaphore:
        scraper = JinaScraper(api_key=state.config.JINA_API_KEY)
        try:
            content = await scraper.scrape(url)
            if content:
                state.articles[url] = content
            else:
                state.add_log(f"Failed to scrape {url} with JinaScraper.", level="ERROR")
        except Exception as e:
            state.add_log(f"Error scraping {url} with JinaScraper: {e}", level="ERROR")
            logger.error(f"Error scraping {url} with JinaScraper: {e}")

async def scrape_with_web_base_loader(url: str, state: SharedState, semaphore):
    async with semaphore:
        scraper = WebBaseLoaderScraper()
        try:
            content = await scraper.scrape(url)
            if content:
                state.articles[url] = content
            else:
                state.add_log(f"Failed to scrape {url} with WebBaseLoaderScraper.", level="ERROR")
        except Exception as e:
            state.add_log(f"Error scraping {url} with WebBaseLoaderScraper: {e}", level="ERROR")
            logger.error(f"Error scraping {url} with WebBaseLoaderScraper: {e}")
