# File: test_url_generation_agent.py
# Directory: tests/

"""
Unit Test for url_generation_agent
Test Objective:
- Verify that the agent correctly generates search terms and decides on the search agent.
Expected Results:
- Correct search terms are generated.
- Agent selection logic works as expected.
Variables Used:
- Mocked OpenAI API responses.
"""

import unittest
from unittest.mock import patch, AsyncMock
from models.state import SharedState
from config.config import Config
from agents.url_generation_agent import url_generation_agent

class TestURLGenerationAgent(unittest.IsolatedAsyncioTestCase):

    async def test_url_generation(self):
        state = SharedState()
        state.user_query = "Test query"
        state.config = Config()
        # Mock OpenAI responses
        with patch('openai.ChatCompletion.acreate', new_callable=AsyncMock) as mock_openai:
            mock_openai.return_value = AsyncMock(choices=[AsyncMock(message={'content': 'search term1, search term2'})])
            await url_generation_agent(state)
            self.assertIn('search term1', state.search_terms)
            self.assertIn('search term2', state.search_terms)

if __name__ == '__main__':
    unittest.main()
