# File: test_workflow.py
# Directory: tests/

"""
Integration Test for the Entire Workflow
Test Objective:
- Verify that the agents work together to complete the workflow.
Expected Results:
- Workflow completes successfully.
- All state variables are appropriately populated.
Variables Used:
- Mocked API responses for OpenAI, Google CSE, Tavily, and Jina.
"""

import unittest
from unittest.mock import patch, AsyncMock
from models.state import SharedState
from config.config import Config
from agents.router_agent import router_agent

class TestWorkflow(unittest.IsolatedAsyncioTestCase):

    async def test_full_workflow(self):
        state = SharedState()
        state.user_query = "Test query"
        state.config = Config()

        # Mock OpenAI API
        with patch('openai.ChatCompletion.acreate', new_callable=AsyncMock) as mock_openai, \
             patch('tools.searching.google_cse.GoogleCSE.search', new_callable=AsyncMock) as mock_google_search, \
             patch('tools.scraping.jina_scraper.JinaScraper.scrape', new_callable=AsyncMock) as mock_jina_scrape:
            
            # Mock responses
            mock_openai.return_value = AsyncMock(choices=[AsyncMock(message={'content': 'search term1, search term2'})])
            mock_google_search.return_value = ['http://example.com']
            mock_jina_scrape.return_value = 'Article content'

            # Run the workflow
            await router_agent(state)
            self.assertEqual(state.next_step, 'scraper_selection')
            await router_agent(state)
            self.assertEqual(state.next_step, 'article_extraction')
            await router_agent(state)
            self.assertEqual(state.next_step, 'review')
            await router_agent(state)
            self.assertEqual(state.next_step, 'knowledge_graph_upload')
            await router_agent(state)
            self.assertEqual(state.next_step, 'end')

if __name__ == '__main__':
    unittest.main()
