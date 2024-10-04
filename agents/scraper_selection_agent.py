# File: scraper_selection_agent.py
# Directory: my_app/agents/

# Overall Role and Purpose:
# - Determines the most appropriate scraper for each URL.
# - Currently defaults to using `JinaScraper` as it's effective for text extraction.

# Expected Inputs:
# - `SharedState` with `urls_to_be_processed`.

# Expected Outputs:
# - Updates `scraper_choices` in the state, mapping each URL to a scraper.

from models.state import SharedState
from agents.scraping_agent import scraping_agent

async def scraper_selection_agent(state: SharedState):
    state.add_log("Selecting appropriate scrapers for each URL.")
    for url in state.urls_to_be_processed:
        # For simplicity, we'll default to using JinaScraper
        state.scraper_choices[url] = "jina_scraper"
    state.add_log(f"Scraper choices: {state.scraper_choices}")
    await scraping_agent(state)
