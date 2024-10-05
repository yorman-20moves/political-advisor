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

import pytest
from unittest.mock import AsyncMock, patch
from models.state import SharedState
from agents.router_agent import router_agent
from config import config  # Adjust the import path if necessary

class TestWorkflow:
    @pytest.mark.asyncio
    async def test_full_workflow(self):
        state = SharedState()
        state.user_query = "Test query"
        state.config = config()
        state.next_step = "url_generation"  # Set initial step

        # Mock all agent functions
        with patch('agents.url_generation_agent.url_generation_agent', new_callable=AsyncMock) as mock_url_gen, \
             patch('agents.scraper_selection_agent.scraper_selection_agent', new_callable=AsyncMock) as mock_scraper_select, \
             patch('agents.article_extraction_agent.article_extraction_agent', new_callable=AsyncMock) as mock_article_extract, \
             patch('agents.reviewer_agent.reviewer_agent', new_callable=AsyncMock) as mock_reviewer, \
             patch('agents.knowledge_graph_uploader_agent.knowledge_graph_uploader_agent', new_callable=AsyncMock) as mock_uploader:

            # Set up mock behaviors
            mock_url_gen.side_effect = lambda s: setattr(s, 'urls_to_be_processed', ['http://example.com'])
            mock_scraper_select.side_effect = lambda s: setattr(s, 'scraper_choices', {'http://example.com': 'some_scraper'})
            mock_article_extract.side_effect = lambda s: setattr(s, 'extracted_data', {'http://example.com': {'content': 'test'}})
            mock_reviewer.side_effect = lambda s: setattr(s, 'reviewed_data', {'http://example.com': {'content': 'approved'}})
            mock_uploader.side_effect = lambda s: setattr(s, 'upload_complete', True)

            # Run the workflow
            await router_agent(state)

        # Assert that each agent was called once
        mock_url_gen.assert_called_once()
        mock_scraper_select.assert_called_once()
        mock_article_extract.assert_called_once()
        mock_reviewer.assert_called_once()
        mock_uploader.assert_called_once()

        # Assert that the workflow completed successfully
        assert state.next_step == "end"
        assert state.upload_complete == True

if __name__ == '__main__':
    pytest.main()
