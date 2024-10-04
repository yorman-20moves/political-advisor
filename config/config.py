# File: config.py
# Directory: my_app/config/

# Overall Role and Purpose:
# - Manages application configuration settings.
# - Loads API keys, database credentials, user agent strings, and other configurable parameters from the `.env` file.

# Expected Inputs:
# - Environment variables defined in the `.env` file.

# Expected Outputs:
# - A `Config` object with accessible attributes for configurations.
# - Provides methods to get configuration values.

import os
from typing import Any
from dotenv import load_dotenv

class Config:
    def __init__(self):
        # Load environment variables from .env file
        load_dotenv()

        self.GOOGLE_CSE_API_KEY = os.getenv("GOOGLE_CSE_API_KEY")
        self.GOOGLE_CSE_CX = os.getenv("GOOGLE_CSE_CX")
        self.TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
        self.NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        self.NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
        self.NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")
        self.JINA_API_KEY = os.getenv("JINA_API_KEY")
        self.USER_AGENT = os.getenv("USER_AGENT", "Mozilla/5.0 (compatible; MyAppBot/1.0)")

        # OpenAI LLM configurations
        self.OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
        self.OPENAI_API_BASE = os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1")
        self.LLM_MODEL_NAME = os.getenv("LLM_MODEL_NAME", "gpt-4")
        self.LLM_MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", "500"))
        self.LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.7"))

    def get(self, key: str, default: Any = None) -> Any:
        return getattr(self, key, default)
