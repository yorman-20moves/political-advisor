# File: jina_scraper.py
# Directory: my_app/tools/scraping/

# Overall Role and Purpose:
# - Implements the `JinaScraper` class for simple text extraction from URLs.
# - Correctly utilizes Jina's Reader API for full text extraction.

# Expected Inputs:
# - URL to scrape.

# Expected Outputs:
# - Extracted text content from the webpage.

import aiohttp

class JinaScraper:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = 'https://r.jina.ai/'

    async def scrape(self, url: str) -> str:
        # Construct the Jina Reader API URL
        reader_url = self.base_url + url

        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'X-Return-Format': 'text',
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(reader_url, headers=headers) as response:
                if response.status == 200:
                    text = await response.text()
                    return text
                else:
                    # Log the error or handle it as needed
                    return None
