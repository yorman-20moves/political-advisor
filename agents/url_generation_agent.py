# File: url_generation_agent.py
# Directory: my_app/agents/

# Overall Role and Purpose:
# - Generates URLs for articles based on search terms.
# - Uses an LLM prompt to develop the most effective 5 search terms.
# - Decides whether to use the General URL Generation Agent or the Contextual URL Generation Agent based on reasoning using provided descriptions.

# Expected Inputs:
# - `SharedState` with the user query.
# - `Config` with API keys and settings.

# Expected Outputs:
# - Updates `search_terms` in the state with the generated search terms.
# - Updates `urls_to_be_processed` in the state with the list of generated URLs.

import asyncio
import logging
from models.state import SharedState
from tools.searching.google_cse import GoogleCSE
from tools.searching.tavily_search import TavilySearch
from prompts.search_term_generation_prompt import SEARCH_TERM_GENERATION_PROMPT
from prompts.search_agent_selection_prompt import SEARCH_AGENT_SELECTION_PROMPT
import openai
import json

logger = logging.getLogger(__name__)

async def url_generation_agent(state: SharedState):
    try:
        # Generate 5 search terms using LLM
        search_terms = await generate_search_terms(state.user_query, state.config, state)
        state.search_terms = search_terms

        if not search_terms:
            state.add_log("No search terms could be generated.", level="ERROR")
            state.next_step = "end"
            return

        # Decide whether to use general or contextual agent using LLM
        agent_choice = await decide_search_agent(state.user_query, search_terms, state.config, state)
        if agent_choice == "Contextual":
            state.add_log("Decided to use Contextual URL Generation Agent.", level="INFO")
            await contextual_url_generation_agent(state)
        else:
            state.add_log("Decided to use General URL Generation Agent.", level="INFO")
            await general_url_generation_agent(state)
    except Exception as e:
        state.add_log(f"Error in url_generation_agent: {e}", level="ERROR")
        logger.error(f"Error in url_generation_agent: {e}")

async def generate_search_terms(user_query: str, config, state: SharedState):
    try:
        prompt = SEARCH_TERM_GENERATION_PROMPT.format(query=user_query)
        # Call LLM to generate search terms
        openai.api_key = config.OPENAI_API_KEY
        openai.api_base = config.OPENAI_API_BASE
        response = await openai.ChatCompletion.acreate(
            model=config.LLM_MODEL_NAME,
            messages=[
                {"role": "system", "content": "You are an assistant that generates effective search terms based on user queries."},
                {"role": "user", "content": prompt}
            ],
            temperature=config.LLM_TEMPERATURE,
            max_tokens=50,
            n=1,
        )
        search_terms_text = response.choices[0].message['content'].strip()
        # Parse the response to get a list of search terms
        if "No search terms could be generated." in search_terms_text:
            return []
        search_terms = [term.strip() for term in search_terms_text.split(',') if term.strip()]
        return search_terms
    except Exception as e:
        state.add_log(f"Error in generate_search_terms: {e}", level="ERROR")
        logger.error(f"Error in generate_search_terms: {e}")
        return []

async def decide_search_agent(user_query: str, search_terms: list, config, state: SharedState):
    try:
        # Prepare the prompt with the descriptions
        tavily_description = """[Tavily description here]"""
        google_cse_description = """[Google CSE description here]"""

        # Create the prompt
        prompt = SEARCH_AGENT_SELECTION_PROMPT.format(
            user_query=user_query,
            search_terms=", ".join(search_terms),
            tavily_description=tavily_description,
            google_cse_description=google_cse_description
        )

        # Call LLM to decide which agent to use
        response = await openai.ChatCompletion.acreate(
            model=config.LLM_MODEL_NAME,
            messages=[
                {"role": "system", "content": "You are an assistant that decides which search engine is better suited for a given query based on their descriptions."},
                {"role": "user", "content": prompt}
            ],
            temperature=config.LLM_TEMPERATURE,
            max_tokens=10,
            n=1,
        )
        decision_text = response.choices[0].message['content'].strip()

        if "Contextual" in decision_text:
            return "Contextual"
        else:
            return "General"
    except Exception as e:
        state.add_log(f"Error in decide_search_agent: {e}", level="ERROR")
        logger.error(f"Error in decide_search_agent: {e}")
        return "General"  # Default to General if error occurs

async def general_url_generation_agent(state: SharedState):
    state.add_log("Starting general URL generation using Google CSE.", level="INFO")
    search_terms = state.search_terms
    urls = []
    semaphore = asyncio.Semaphore(5)  # Limit concurrency to 5
    async def fetch_urls(term):
        async with semaphore:
            cse = GoogleCSE(api_key=state.config.GOOGLE_CSE_API_KEY, cx=state.config.GOOGLE_CSE_CX)
            try:
                results = await cse.search(term)
                urls.extend(results)
            except Exception as e:
                state.add_log(f"Error during Google CSE search for term '{term}': {e}", level="ERROR")

    tasks = [fetch_urls(term) for term in search_terms]
    await asyncio.gather(*tasks)
    # Limit to 15 URLs
    state.urls_to_be_processed = list(set(urls))[:15]
    state.add_log(f"Generated {len(state.urls_to_be_processed)} URLs.", level="INFO")

async def contextual_url_generation_agent(state: SharedState):
    state.add_log("Starting contextual URL generation using Tavily API.", level="INFO")
    search_terms = state.search_terms
    urls = []
    semaphore = asyncio.Semaphore(5)  # Limit concurrency to 5
    async def fetch_urls(term):
        async with semaphore:
            tavily = TavilySearch(api_key=state.config.TAVILY_API_KEY)
            try:
                results = await tavily.search(term)
                urls.extend(results)
            except Exception as e:
                state.add_log(f"Error during Tavily search for term '{term}': {e}", level="ERROR")

    tasks = [fetch_urls(term) for term in search_terms]
    await asyncio.gather(*tasks)
    # Limit to 15 URLs
    state.urls_to_be_processed = list(set(urls))[:15]
    state.add_log(f"Generated {len(state.urls_to_be_processed)} URLs.", level="INFO")
