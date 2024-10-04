# my_agent/agent.py

# Standard library imports
import logging
from typing import Dict, TypedDict

# LangGraph imports
from langgraph.graph import StateGraph, END
from my_agent.utils.nodes import url_lookup_agent, article_extraction_agent, knowledge_graph_uploader_agent, router_agent
from my_agent.utils.config import Config

# Initialize configuration and logger
config = Config()
logger = config.get_logger('Agent')

# Define a schema for our state
class AgentState(TypedDict):
    messages: list
    search_terms: list
    urls_to_be_processed: list
    files_to_be_processed: list
    log_messages: list
    sender: str
    completed_upload: bool

def run_agent(initial_state: Dict) -> Dict:
    """
    Run the agent workflow.

    This function sets up and executes the state machine for the agent workflow.
    It handles URL lookup, article extraction, and knowledge graph uploading.

    Args:
        initial_state (AgentState): The initial state of the agent.

    Returns:
        AgentState: The final state after the workflow completion.
    """
    try:
        logger.info("Starting the agent workflow.")
        
        # Initialize log_messages in the state
        initial_state['log_messages'] = []

        # Create a new graph with the defined schema
        workflow = StateGraph(AgentState)

        # Add nodes to the graph
        workflow.add_node("URL Lookup", url_lookup_agent)
        workflow.add_node("Article Extraction", article_extraction_agent)
        workflow.add_node("Knowledge Graph Upload", knowledge_graph_uploader_agent)

        # Set the entry point
        workflow.set_entry_point("URL Lookup")

        # Add edges with conditions
        workflow.add_edge("URL Lookup", "Article Extraction")
        workflow.add_edge("Article Extraction", "Knowledge Graph Upload")
        workflow.add_edge("Knowledge Graph Upload", END)

        # Add conditional edges based on the router_agent logic
        workflow.add_conditional_edges(
            "URL Lookup",
            router_agent,
            {
                "URL Lookup": "URL Lookup",
                "Article Extraction": "Article Extraction",
                "Knowledge Graph Upload": "Knowledge Graph Upload",
                END: END
            }
        )

        # Compile the graph
        app = workflow.compile()

        # Run the graph
        final_state = app.invoke(initial_state)
        
        logger.info("Agent workflow completed successfully.")
        logger.info(f"Final state: {final_state}")
        
        return final_state
    except Exception as e:
        logger.exception(f"An error occurred during the agent workflow: {e}")
        raise
