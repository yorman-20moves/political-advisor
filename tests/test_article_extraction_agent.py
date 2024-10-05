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

class TestArticleExtractionAgent:
    @pytest.mark.asyncio
    async def test_article_extraction(self):
        state = SharedState()
        state.urls_to_be_processed = ["http://example.com"]
        state.scraper_choices = {"http://example.com": "some_scraper"}

        mock_scraper = AsyncMock()
        mock_scraper.return_value = "Mocked article content"

        mock_openai_response = AsyncMock()
        mock_openai_response.choices[0].message.content = '{"Article": {"Title": "Test Article", "URL": "http://example.com", "Date Published": "01/01/2023"}}'

        with patch('agents.article_extraction_agent.scrape_article', new=mock_scraper), \
             patch('openai.AsyncOpenAI.chat.completions.create', return_value=mock_openai_response):
            await article_extraction_agent(state)

        assert "http://example.com" in state.extracted_data
        assert state.extracted_data["http://example.com"]["Article"]["Title"] == "Test Article"

if __name__ == '__main__':
    pytest.main()
