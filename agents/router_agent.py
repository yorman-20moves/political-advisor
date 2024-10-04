# File: router_agent.py
# Directory: my_app/agents/

# Overall Role and Purpose:
# - Central decision-making agent that routes the workflow to the appropriate next agent.
# - Examines the current state to determine which agent should be executed next.

# Expected Inputs:
# - Current `SharedState`.

# Expected Outputs:
# - Updates the `next_step` in the state.
# - Invokes the next agent based on the workflow logic.

from models.state import SharedState
from agents.url_generation_agent import url_generation_agent
from agents.scraper_selection_agent import scraper_selection_agent
from agents.article_extraction_agent import article_extraction_agent
from agents.reviewer_agent import reviewer_agent
from agents.knowledge_graph_uploader_agent import knowledge_graph_uploader_agent

async def router_agent(state: SharedState):
    state.add_log(f"Routing to next step based on current state.")

    if not state.urls_to_be_processed:
        if need_more_context(state):
            state.next_step = "contextual_url_generation"
        else:
            state.next_step = "general_url_generation"
        await url_generation_agent(state)
    elif not state.articles:
        state.next_step = "scraper_selection"
        await scraper_selection_agent(state)
    elif not state.extracted_data:
        state.next_step = "article_extraction"
        await article_extraction_agent(state)
    elif not state.reviewed_data:
        state.next_step = "review"
        await reviewer_agent(state)
    elif not state.upload_complete:
        state.next_step = "knowledge_graph_upload"
        await knowledge_graph_uploader_agent(state)
    else:
        state.next_step = "end"

def need_more_context(state: SharedState) -> bool:
    # Implement logic to determine if more context is needed
    return False  # Placeholder
