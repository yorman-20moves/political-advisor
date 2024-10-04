# File: scraping_agent.py
# Directory: my_app/agents/

# Overall Role and Purpose:
# - Scrapes the content of articles using the selected scrapers.
# - Asynchronously fetches content for each URL.

# Expected Inputs:
# - `SharedState` with `urls_to_be_processed` and `scraper_choices`.

# Expected Outputs:
# - Updates `articles` in the state with scraped content.

from models.state import SharedState
from tools.scraping.jina_scraper import JinaScraper
from tools.scraping.web_base_loader_scraper import WebBaseLoaderScraper
import asyncio

async def scraping_agent(state: SharedState):
    state.add_log("Starting article scraping.")
    tasks = []
    for url in state.urls_to_be_processed:
        scraper_name = state.scraper_choices.get(url)
        if scraper_name == "jina_scraper":
            tasks.append(scrape_with_jina(url, state))
        elif scraper_name == "web_base_loader_scraper":
            tasks.append(scrape_with_web_base_loader(url, state))
    await asyncio.gather(*tasks)
    state.add_log(f"Scraped {len(state.articles)} articles.")

async def scrape_with_jina(url: str, state: SharedState):
    scraper = JinaScraper(api_key=state.config.JINA_API_KEY)
    content = await scraper.scrape(url)
    if content:
        state.articles[url] = content
    else:
        state.add_log(f"Failed to scrape {url} with JinaScraper.")

async def scrape_with_web_base_loader(url: str, state: SharedState):
    scraper = WebBaseLoaderScraper()
    content = await scraper.scrape(url)
    if content:
        state.articles[url] = content
