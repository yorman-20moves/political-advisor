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

import logging
from models.state import SharedState
from agents.url_generation_agent import url_generation_agent
from agents.scraper_selection_agent import scraper_selection_agent
from agents.article_extraction_agent import article_extraction_agent
from agents.reviewer_agent import reviewer_agent
from agents.knowledge_graph_uploader_agent import knowledge_graph_uploader_agent

logger = logging.getLogger(__name__)

async def router_agent(state: SharedState):
    state.add_log(f"Routing to next step based on current state.", level="DEBUG")

    # Use a loop to progress through the workflow until completion
    while state.next_step != "end":
        if state.next_step == "url_generation":
            await url_generation_agent(state)
            # After the agent runs, update next_step based on the new state
            if state.urls_to_be_processed:
                state.next_step = "scraper_selection"
            else:
                state.add_log("No URLs to process. Ending workflow.", level="ERROR")
                state.next_step = "end"

        elif state.next_step == "scraper_selection":
            await scraper_selection_agent(state)
            if state.scraper_choices:
                state.next_step = "article_extraction"
            else:
                state.add_log("No scraper choices made. Ending workflow.", level="ERROR")
                state.next_step = "end"

        elif state.next_step == "article_extraction":
            await article_extraction_agent(state)
            if state.extracted_data:
                state.next_step = "review"
            else:
                state.add_log("No extracted data. Ending workflow.", level="ERROR")
                state.next_step = "end"

        elif state.next_step == "review":
            await reviewer_agent(state)
            if state.reviewed_data:
                state.next_step = "knowledge_graph_upload"
            else:
                state.add_log("No reviewed data. Ending workflow.", level="ERROR")
                state.next_step = "end"

        elif state.next_step == "knowledge_graph_upload":
            await knowledge_graph_uploader_agent(state)
            if state.upload_complete:
                state.next_step = "end"
            else:
                state.add_log("Upload incomplete. Ending workflow.", level="ERROR")
                state.next_step = "end"

        else:
            state.add_log("Unknown next step. Ending workflow.", level="ERROR")
            state.next_step = "end"

    state.add_log("Workflow complete.", level="INFO")