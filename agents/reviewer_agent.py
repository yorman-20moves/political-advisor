# File: reviewer_agent.py
# Directory: my_app/agents/

# Overall Role and Purpose:
# - Reviews the extracted data for quality and correctness.
# - Uses an LLM guided by `REVIEW_PROMPT` to validate data.

# Expected Inputs:
# - `SharedState` with `extracted_data`.
# - `Config` with LLM API keys and settings.

# Expected Outputs:
# - Updates `reviewed_data` in the state with data that passed the review.
# - Logs any issues found during the review.

from models.state import SharedState
from prompts.review_prompt import REVIEW_PROMPT
import openai

async def reviewer_agent(state: SharedState):
    state.add_log("Starting data review.")
    for url, data in state.extracted_data.items():
        prompt = REVIEW_PROMPT.format(extracted_data=data)
        review_result = await call_llm(prompt, state.config)
        if is_valid(review_result):
            state.reviewed_data[url] = data
        else:
            state.add_log(f"Data for {url} failed review: {review_result}")
    state.add_log(f"Reviewed and approved data for {len(state.reviewed_data)} articles.")

def is_valid(review_result: str) -> bool:
    # Implement logic to determine if data is valid based on review_result
    return "Valid" in review_result  # Placeholder

async def call_llm(prompt: str, config):
    openai.api_key = config.LLM_API_KEY
    response = await openai.Completion.create(
        engine=config.LLM_MODEL_NAME,
        prompt=prompt,
        max_tokens=200,
    )
    return response.choices[0].text.strip()
