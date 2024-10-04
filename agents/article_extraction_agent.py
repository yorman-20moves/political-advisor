# File: article_extraction_agent.py
# Directory: my_app/agents/

# Overall Role and Purpose:
# - Processes scraped content to extract structured data.
# - Utilizes an LLM guided by system and human message templates.

# Expected Inputs:
# - `SharedState` with `articles`.
# - `Config` with LLM API keys and settings.

# Expected Outputs:
# - Updates `extracted_data` in the state with structured data extracted from each article.

# File: article_extraction_agent.py
# Directory: my_app/agents/

import asyncio
import json
import logging
from models.state import SharedState
from prompts.article_extraction_prompt import get_article_extraction_prompt
import openai

logger = logging.getLogger(__name__)

async def article_extraction_agent(state: SharedState):
    state.add_log("Starting article extraction.", level="INFO")
    tasks = []
    semaphore = asyncio.Semaphore(5)  # Limit concurrency to 5
    for url, content in state.articles.items():
        tasks.append(extract_article_data(url, content, state, semaphore))
    await asyncio.gather(*tasks)
    state.add_log(f"Extracted data from {len(state.extracted_data)} articles.", level="INFO")

async def extract_article_data(url: str, content: str, state: SharedState, semaphore):
    async with semaphore:
        prompt_messages = get_article_extraction_prompt(url, content)
        extracted_data = await call_llm(prompt_messages, state.config, state)
        if extracted_data:
            state.extracted_data[url] = extracted_data
        else:
            state.add_log(f"Failed to extract data from {url}.", level="ERROR")

async def call_llm(prompt_messages: list, config, state: SharedState):
    try:
        openai.api_key = config.OPENAI_API_KEY
        openai.api_base = config.OPENAI_API_BASE
        response = await openai.ChatCompletion.acreate(
            model=config.LLM_MODEL_NAME,
            messages=prompt_messages,
            temperature=config.LLM_TEMPERATURE,
            max_tokens=config.LLM_MAX_TOKENS,
            n=1,
            stop=None,
        )
        assistant_message = response.choices[0].message['content'].strip()
        # Try to parse the response as JSON
        extracted_data = json.loads(assistant_message)
        return extracted_data
    except json.JSONDecodeError as e:
        state.add_log(f"JSON parsing error for article: {e}", level="ERROR")
        logger.error(f"JSON parsing error: {e}")
        return None
    except Exception as e:
        state.add_log(f"OpenAI API error: {e}", level="ERROR")
        logger.error(f"OpenAI API error: {e}")
        return None
