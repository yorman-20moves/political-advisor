# File: config.py
# Directory: my_app/config/

# Overall Role and Purpose:
# - Manages application configuration settings.
# - Loads API keys, database credentials, user agent strings, and other configurable parameters.

# Expected Inputs:
# - Environment variables or default values for various configurations.

# Expected Outputs:
# - A `Config` object with accessible attributes for configurations.
# - Provides a method to get configuration values.

import os
from typing import Any, Dict

class Config:
    def __init__(self):
        self.GOOGLE_CSE_API_KEY = os.getenv("GOOGLE_CSE_API_KEY", "your_google_cse_api_key")
        self.GOOGLE_CSE_CX = os.getenv("GOOGLE_CSE_CX", "your_google_cse_cx")
        self.TAVILY_API_KEY = os.getenv("TAVILY_API_KEY", "your_tavily_api_key")
        self.NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        self.NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
        self.NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")
        self.USER_AGENT = "Mozilla/5.0 (compatible; MyAppBot/1.0)"
        self.LLM_MODEL_NAME = "gpt-4"
        self.LLM_API_KEY = os.getenv("LLM_API_KEY", "your_openai_api_key")
        # Add other configurations as needed

    def get(self, key: str, default: Any = None) -> Any:
        return getattr(self, key, default)
