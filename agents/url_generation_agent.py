# File: url_generation_agent.py
# Directory: my_app/agents/

# Overall Role and Purpose:
# - Generates URLs for articles based on search terms.
# - Contains two agents:
#   - General URL Generation Agent: Uses Google Custom Search Engine (CSE) for general searches.
#   - Contextual URL Generation Agent: Uses Tavily API for context-specific searches.

# Expected Inputs:
# - `SharedState` with `search_terms`.
# - `Config` with API keys and settings.

# Expected Outputs:
# - Updates `urls_to_be_processed` in the state with the list of generated URLs.

from models.state import SharedState
from tools.searching.google_cse import GoogleCSE
from tools.searching.tavily_search import TavilySearch

async def url_generation_agent(state: SharedState):
    if state.next_step == "general_url_generation":
        await general_url_generation_agent(state)
    elif state.next_step == "contextual_url_generation":
        await contextual_url_generation_agent(state)

async def general_url_generation_agent(state: SharedState):
    state.add_log("Starting general URL generation using Google CSE.")
    search_terms = state.search_terms
    urls = []
    for term in search_terms:
        cse = GoogleCSE(api_key=state.config.GOOGLE_CSE_API_KEY, cx=state.config.GOOGLE_CSE_CX)
        results = await cse.search(term)
        urls.extend(results)
    state.urls_to_be_processed = list(set(urls))  # Remove duplicates
    state.add_log(f"Generated {len(state.urls_to_be_processed)} URLs.")

async def contextual_url_generation_agent(state: SharedState):
    state.add_log("Starting contextual URL generation using Tavily API.")
    search_terms = state.search_terms
    urls = []
    for term in search_terms:
        tavily = TavilySearch(api_key=state.config.TAVILY_API_KEY)
        results = await tavily.search(term)
        urls.extend(results)
    state.urls_to_be_processed = list(set(urls))  # Remove duplicates
    state.add_log(f"Generated {len(state.urls_to_be_processed)} URLs.")
