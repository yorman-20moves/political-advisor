# File: article_extraction_agent.py
# Directory: my_app/agents/

# Overall Role and Purpose:
# - Processes scraped content to extract structured data.
# - Utilizes an LLM guided by `ARTICLE_EXTRACTION_PROMPT`.

# Expected Inputs:
# - `SharedState` with `articles`.
# - `Config` with LLM API keys and settings.

# Expected Outputs:
# - Updates `extracted_data` in the state with structured data extracted from each article.

from models.state import SharedState
from prompts.article_extraction_prompt import ARTICLE_EXTRACTION_PROMPT
import openai

async def article_extraction_agent(state: SharedState):
    state.add_log("Starting article extraction.")
    for url, content in state.articles.items():
        prompt = ARTICLE_EXTRACTION_PROMPT.format(article_text=content)
        extracted_data = await call_llm(prompt, state.config)
        state.extracted_data[url] = extracted_data
    state.add_log(f"Extracted data from {len(state.extracted_data)} articles.")

async def call_llm(prompt: str, config):
    openai.api_key = config.LLM_API_KEY
    response = await openai.Completion.create(
        engine=config.LLM_MODEL_NAME,
        prompt=prompt,
        max_tokens=500,
    )
    return response.choices[0].text.strip()
