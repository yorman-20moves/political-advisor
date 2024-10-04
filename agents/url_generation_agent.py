# File: url_generation_agent.py
# Directory: my_app/agents/

# Overall Role and Purpose:
# - Generates URLs for articles based on search terms.
# - Uses an LLM prompt to develop the most effective 5 search terms.
# - Decides whether to use the General URL Generation Agent or the Contextual URL Generation Agent based on the nature of the search terms.

# Expected Inputs:
# - `SharedState` with the user query.
# - `Config` with API keys and settings.

# Expected Outputs:
# - Updates `search_terms` in the state with the generated search terms.
# - Updates `urls_to_be_processed` in the state with the list of generated URLs.

from models.state import SharedState
from tools.searching.google_cse import GoogleCSE
from tools.searching.tavily_search import TavilySearch
from prompts.search_term_generation_prompt import SEARCH_TERM_GENERATION_PROMPT
import openai

async def url_generation_agent(state: SharedState):
    # Generate 5 search terms using LLM
    search_terms = await generate_search_terms(state.user_query, state.config)
    state.search_terms = search_terms

    # Decide whether to use general or contextual agent
    if should_use_contextual_agent(search_terms):
        state.add_log("Decided to use Contextual URL Generation Agent.")
        await contextual_url_generation_agent(state)
    else:
        state.add_log("Decided to use General URL Generation Agent.")
        await general_url_generation_agent(state)

async def generate_search_terms(user_query: str, config):
    prompt = SEARCH_TERM_GENERATION_PROMPT.format(query=user_query)
    # Call LLM to generate search terms
    openai.api_key = config.LLM_API_KEY
    response = await openai.Completion.create(
        engine=config.LLM_MODEL_NAME,
        prompt=prompt,
        max_tokens=50,
        n=1,
        stop=None,
    )
    search_terms_text = response.choices[0].text.strip()
    # Parse the response to get a list of search terms
    if "No search terms could be generated." in search_terms_text:
        return []
    search_terms = [term.strip() for term in search_terms_text.split(',') if term.strip()]
    return search_terms

def should_use_contextual_agent(search_terms: list) -> bool:
    # Decide which agent to use based on the specificity of search terms
    broad_terms = 0
    specific_terms = 0
    for term in search_terms:
        word_count = len(term.split())
        if word_count <= 3:
            broad_terms += 1
        else:
            specific_terms += 1
    # If more than half of the terms are specific, use the contextual agent
    return specific_terms > broad_terms

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
