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

from models.state import SharedState
from tools.searching.google_cse import GoogleCSE
from tools.searching.tavily_search import TavilySearch
from prompts.search_term_generation_prompt import SEARCH_TERM_GENERATION_PROMPT
from prompts.search_agent_selection_prompt import SEARCH_AGENT_SELECTION_PROMPT
import openai

async def url_generation_agent(state: SharedState):
    # Generate 5 search terms using LLM
    search_terms = await generate_search_terms(state.user_query, state.config)
    state.search_terms = search_terms

    # Decide whether to use general or contextual agent using LLM
    agent_choice = await decide_search_agent(state.user_query, search_terms, state.config)
    if agent_choice == "Contextual":
        state.add_log("Decided to use Contextual URL Generation Agent.")
        await contextual_url_generation_agent(state)
    else:
        state.add_log("Decided to use General URL Generation Agent.")
        await general_url_generation_agent(state)

async def generate_search_terms(user_query: str, config):
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

async def decide_search_agent(user_query: str, search_terms: list, config):
    # Prepare the prompt with the descriptions
    tavily_description = """Tavily Search API is a specialized search engine optimized for AI agents and LLMs. It aggregates information from multiple online sources, using proprietary AI to score, filter, and rank the most relevant content for a given query or task. Tavily offers customizable search depths, domain management, and the ability to parse HTML content. It provides real-time, trusted information and can include short answers for cross-agent communication, making it particularly useful for RAG applications and AI-driven research tasks."""
    
    google_cse_description = """The New York Politics News Aggregator is a custom Google search engine focused on retrieving relevant news articles about New York politics from a curated list of sources. It covers comprehensive citywide news outlets, local borough-specific media, Black and Latino media, and official newsrooms from New York State and City government entities. This search engine is specifically tailored to provide targeted results from authoritative sources on New York political news, making it ideal for queries related to local and state politics in the New York area."""

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

async def general_url_generation_agent(state: SharedState):
    state.add_log("Starting general URL generation using Google CSE.")
    search_terms = state.search_terms
    urls = []
    for term in search_terms:
        cse = GoogleCSE(api_key=state.config.GOOGLE_CSE_API_KEY, cx=state.config.GOOGLE_CSE_CX)
        results = await cse.search(term)
        urls.extend(results)
    # Limit to 15 URLs
    state.urls_to_be_processed = list(set(urls))[:15]  # Remove duplicates and limit to 15
    state.add_log(f"Generated {len(state.urls_to_be_processed)} URLs.")

async def contextual_url_generation_agent(state: SharedState):
    state.add_log("Starting contextual URL generation using Tavily API.")
    search_terms = state.search_terms
    urls = []
    for term in search_terms:
        tavily = TavilySearch(api_key=state.config.TAVILY_API_KEY)
        results = await tavily.search(term)
        urls.extend(results)
    # Limit to 15 URLs
    state.urls_to_be_processed = list(set(urls))[:15]  # Remove duplicates and limit to 15
    state.add_log(f"Generated {len(state.urls_to_be_processed)} URLs.")
