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

import unittest
from unittest.mock import patch, AsyncMock
from models.state import SharedState
from config.config import Config
from agents.article_extraction_agent import article_extraction_agent

class TestArticleExtractionAgent(unittest.IsolatedAsyncioTestCase):

    async def test_article_extraction(self):
        state = SharedState()
        state.articles = {'http://example.com': 'Article content'}
        state.config = Config()
        # Mock OpenAI responses
        with patch('openai.ChatCompletion.acreate', new_callable=AsyncMock) as mock_openai:
            mock_openai.return_value = AsyncMock(choices=[AsyncMock(message={'content': '{"key": "value"}'})])
            await article_extraction_agent(state)
            self.assertIn('http://example.com', state.extracted_data)
            self.assertEqual(state.extracted_data['http://example.com'], {'key': 'value'})

if __name__ == '__main__':
    unittest.main()
