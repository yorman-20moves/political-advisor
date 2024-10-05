# File: test_google_cse.py
# Directory: tests/

"""
Unit Test for GoogleCSE Class
Test Objective:
- Verify that the GoogleCSE class correctly handles successful API calls and error scenarios.
Expected Results:
- Successful search returns a list of URLs.
- API errors are handled gracefully, returning an empty list.
Variables Used:
- Mocked API responses for success and error cases.
"""

import pytest
from unittest.mock import AsyncMock, patch
from tools.searching.google_cse import GoogleCSE
import asyncio

class TestGoogleCSE:
    @pytest.mark.asyncio
    async def test_successful_search(self):
        async def mock_get(*args, **kwargs):
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.__aenter__.return_value = mock_response
            mock_response.json.return_value = {
                "items": [
                    {"link": "http://example.com/1"},
                    {"link": "http://example.com/2"}
                ]
            }
            return mock_response

        with patch('aiohttp.ClientSession.get', new=mock_get):
            cse = GoogleCSE(api_key='test_key', cx='test_cx')
            results = await cse.search('test query')
            assert results == ['http://example.com/1', 'http://example.com/2']

    @pytest.mark.asyncio
    async def test_api_error(self):
        async def mock_get(*args, **kwargs):
            mock_response = AsyncMock()
            mock_response.status = 500
            mock_response.__aenter__.return_value = mock_response
            mock_response.json.return_value = {"error": "API Error"}
            return mock_response

        with patch('aiohttp.ClientSession.get', new=mock_get):
            cse = GoogleCSE(api_key='test_key', cx='test_cx')
            results = await cse.search('test query')
            assert results == []

    @pytest.mark.asyncio
    async def test_timeout(self):
        async def mock_get(*args, **kwargs):
            raise asyncio.TimeoutError()

        with patch('aiohttp.ClientSession.get', side_effect=mock_get):
            cse = GoogleCSE(api_key='test_key', cx='test_cx')
            results = await cse.search('test query')
            assert results == []

if __name__ == '__main__':
    pytest.main()
