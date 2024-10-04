# File: search_term_generation_prompt.py
# Directory: my_app/prompts/

# Overall Role and Purpose:
# - Provides the prompt template for generating effective search terms from the user query using LLM.

# Expected Inputs:
# - User query.

# Expected Outputs:
# - A formatted prompt string to be used with the LLM to generate 5 search terms.

from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate

SEARCH_TERM_GENERATION_SYSTEM_PROMPT = """
Generate 5 search terms that would be effective for finding relevant news articles about this topic.
Provide the search terms as a comma-separated list.
Do not include any other text or explanation in your response.
If you cannot generate search terms, write "No search terms could be generated.
"""

SEARCH_TERM_GENERATION_HUMAN_PROMPT = """
{query}
"""

SEARCH_TERM_GENERATION_PROMPT = ChatPromptTemplate.from_messages(
    [
        ("system", SEARCH_TERM_GENERATION_SYSTEM_PROMPT),
        ("human", SEARCH_TERM_GENERATION_HUMAN_PROMPT),
    ]
)

