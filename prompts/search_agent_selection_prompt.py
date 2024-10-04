# File: search_agent_selection_prompt.py
# Directory: my_app/prompts/

# Overall Role and Purpose:
# - Provides the prompt template for deciding which search agent to use based on the user query, search terms, and descriptions.

# Expected Inputs:
# - User query, generated search terms, descriptions of Tavily and Google CSE.

# Expected Outputs:
# - A formatted prompt string to be used with the LLM to decide whether to use the General or Contextual URL Generation Agent.

from langchain_core.prompts import ChatPromptTemplate

SEARCH_AGENT_SELECTION_SYSTEM_PROMPT = """
Based on the user query and the generated search terms, determine which search engine is better suited to retrieve relevant URLs. Consider the capabilities and focus areas of each search engine.

Respond with either "Contextual" if Tavily Search API is better suited, or "General" if the Custom Google CSE is better suited.

Do not include any other text or explanation in your response.

Available Search Engines:

1. Tavily Search API:
{tavily_description}

2. New York Politics News Aggregator (Custom Google CSE):
{google_cse_description}
"""

SEARCH_AGENT_SELECTION_HUMAN_PROMPT = """
User Query:
"{user_query}"

Generated Search Terms:
{search_terms}
"""

SEARCH_AGENT_SELECTION_PROMPT = ChatPromptTemplate.from_messages(
    [
        ("system", SEARCH_AGENT_SELECTION_SYSTEM_PROMPT),
        ("human", SEARCH_AGENT_SELECTION_HUMAN_PROMPT),
    ]
)
