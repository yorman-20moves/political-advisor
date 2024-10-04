# File: article_extraction_prompt.py
# Directory: my_app/prompts/

# Overall Role and Purpose:
# - Defines the `ARTICLE_EXTRACTION_PROMPT` template.
# - Guides the LLM to extract structured data from the article content.

# Expected Inputs:
# - Article text to be processed.

# Expected Outputs:
# - A formatted prompt string ready for use with the LLM.

ARTICLE_EXTRACTION_PROMPT = """
Extract the key information from the following article text and present it in JSON format.

Article Text:
{article_text}

Instructions:
- Identify and extract entities such as stakeholders, events, dates, locations, etc.
- Organize the information in a structured JSON format as per the schema:
{
    "title": "",
    "date": "",
    "author": "",
    "stakeholders": [],
    "events": [],
    "locations": [],
    "summary": ""
}

Output:
"""
