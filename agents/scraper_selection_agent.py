# File: scraper_selection_agent.py
# Directory: my_app/agents/

# Overall Role and Purpose:
# - Determines the most appropriate scraper for each URL.
# - Chooses between `JinaScraper` for simple text extraction and `WebBaseLoaderScraper` for complex sites.

# Expected Inputs:
# - `SharedState` with `urls_to_be_processed`.

# Expected Outputs:
# - Updates `scraper_choices` in the state, mapping each URL to a scraper.

from models.state import SharedState
import re

async def scraper_selection_agent(state: SharedState):
    state.add_log("Selecting appropriate scrapers for each URL.")
    for url in state.urls_to_be_processed:
        scraper = select_scraper(url)
        state.scraper_choices[url] = scraper
    state.add_log(f"Scraper choices: {state.scraper_choices}")
    await scraping_agent(state)

def select_scraper(url: str) -> str:
    # Implement logic to select scraper based on URL
    # For simplicity, using regex or domain matching
    if is_simple_text_site(url):
        return "jina_scraper"
    else:
        return "web_base_loader_scraper"

def is_simple_text_site(url: str) -> bool:
    # Placeholder logic
    return True  # Assume all are simple text sites for now
