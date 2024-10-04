# File: tavily_search.py
# Directory: my_app/tools/searching/

# Overall Role and Purpose:
# - Provides the `TavilySearch` class to perform context-specific searches using the Tavily API.
# - Used by the Contextual URL Generation Agent.

# Expected Inputs:
# - Search query string.
# - API key from the configuration.

# Expected Outputs:
# - List of URLs resulting from the search.

import aiohttp

class TavilySearch:
    def __init__(self, api_key: str):
        self.api_key = api_key

    async def search(self, query: str) -> list:
        url = "https://api.tavily.com/search"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
        }
        params = {
            "query": query,
        }
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, params=params) as response:
                data = await response.json()
                results = [item["url"] for item in data.get("results", [])]
                return results
