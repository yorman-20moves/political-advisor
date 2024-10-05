# File: test_article_extraction_agent.py
# Directory: tests/

"""
Unit Test for article_extraction_agent
Test Objective:
- Verify that the agent correctly extracts data from articles.
Expected Results:
- Extracted data is stored in the state.
- Errors are handled gracefully.
Variables Used:
- Mocked OpenAI API responses.
"""

import pytest
from unittest.mock import AsyncMock, patch
from agents.article_extraction_agent import article_extraction_agent
from models.state import SharedState
from config import config  # Import Config if it's a class, or import necessary config values

class TestArticleExtractionAgent:
    @pytest.mark.asyncio
    async def test_article_extraction(self):
        # Setup
        state = SharedState()
        state.articles = {
            "http://example.com": "This is a test article content."
        }
        state.config = config  # If Config is a class, or use a dict if it's not
        state.config.OPENAI_API_KEY = "test_api_key"
        state.config.LLM_MODEL_NAME = "gpt-3.5-turbo"
        state.config.LLM_TEMPERATURE = 0.7
        state.config.LLM_MAX_TOKENS = 1000

        # Mock OpenAI API response
        mock_openai_response = AsyncMock()
        mock_openai_response.choices = [
            AsyncMock(message={
                'content': '{"Article": {"Title": "Test Article", "URL": "http://example.com", "Date Published": "01/01/2023"}}'
            })
        ]

        # Patch the OpenAI API call
        with patch('openai.ChatCompletion.acreate', return_value=mock_openai_response):
            await article_extraction_agent(state)

        # Assertions
        assert "http://example.com" in state.extracted_data
        assert state.extracted_data["http://example.com"]["Article"]["Title"] == "Test Article"
        assert state.extracted_data["http://example.com"]["Article"]["URL"] == "http://example.com"
        assert state.extracted_data["http://example.com"]["Article"]["Date Published"] == "01/01/2023"

if __name__ == '__main__':
    pytest.main()
