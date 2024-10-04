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

import asyncio
import unittest
from unittest.mock import patch, AsyncMock
from tools.searching.google_cse import GoogleCSE

class TestGoogleCSE(unittest.IsolatedAsyncioTestCase):

    async def test_successful_search(self):
        async def mock_get(*args, **kwargs):
            class MockResponse:
                status = 200
                async def json(self):
                    return {
                        "items": [
                            {"link": "http://example.com/1"},
                            {"link": "http://example.com/2"},
                        ]
                    }
            return MockResponse()
        
        with patch('aiohttp.ClientSession.get', new=mock_get):
            cse = GoogleCSE(api_key='test_key', cx='test_cx')
            results = await cse.search('test query')
            self.assertEqual(results, ['http://example.com/1', 'http://example.com/2'])

    async def test_api_error(self):
        async def mock_get(*args, **kwargs):
            class MockResponse:
                status = 403
                async def text(self):
                    return "Forbidden"
            return MockResponse()
        
        with patch('aiohttp.ClientSession.get', new=mock_get):
            cse = GoogleCSE(api_key='test_key', cx='test_cx')
            results = await cse.search('test query')
            self.assertEqual(results, [])

    async def test_timeout(self):
        with patch('aiohttp.ClientSession.get', new_callable=AsyncMock) as mock_get:
            mock_get.side_effect = asyncio.TimeoutError
            cse = GoogleCSE(api_key='test_key', cx='test_cx')
            results = await cse.search('test query')
            self.assertEqual(results, [])

if __name__ == '__main__':
    unittest.main()
