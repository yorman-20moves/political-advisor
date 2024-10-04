# File: google_cse.py
# Directory: my_app/tools/searching/

# Overall Role and Purpose:
# - Provides the `GoogleCSE` class to perform searches using the Google Custom Search Engine API.
# - Used by the General URL Generation Agent.

# Expected Inputs:
# - Search query string.
# - API key and CX identifier from the configuration.

# Expected Outputs:
# - List of URLs resulting from the search.

import aiohttp
import logging
import asyncio

logger = logging.getLogger(__name__)

class GoogleCSE:
    def __init__(self, api_key: str, cx: str):
        self.api_key = api_key
        self.cx = cx

    async def search(self, query: str) -> list:
        url = "https://www.googleapis.com/customsearch/v1"
        params = {
            "key": self.api_key,
            "cx": self.cx,
            "q": query,
            "num": 10  # Max number of results per page
        }
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()
                        results = [item["link"] for item in data.get("items", [])]
                        return results
                    else:
                        error_data = await response.text()
                        logger.error(f"Google CSE API error ({response.status}): {error_data}")
                        return []
        except asyncio.TimeoutError:
            logger.error("Google CSE API request timed out.")
            return []
        except Exception as e:
            logger.error(f"Exception during Google CSE API call: {e}")
            return []
