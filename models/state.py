# File: state.py
# Directory: my_app/models/

# Overall Role and Purpose:
# - Defines the `SharedState` class.
# - Manages the state data shared across agents during the workflow.
# - Holds data like search terms, URLs, articles, extracted data, reviewed data, logs, and configuration.

# Expected Inputs:
# - Initialization parameters like `search_terms`.
# - Updates from agents as the workflow progresses.

# Expected Outputs:
# - Updated state reflecting the current progress of the workflow.
# - Provides methods to log messages and reset the state.

from typing import List, Optional, Dict
from pydantic import BaseModel
from config.config import Config

class SharedState(BaseModel):
    search_terms: List[str]
    urls_to_be_processed: List[str] = []
    scraper_choices: Dict[str, str] = {}  # URL to scraper mapping
    articles: Dict[str, str] = {}  # URL to article content
    extracted_data: Dict[str, Dict] = {}  # URL to extracted data
    reviewed_data: Dict[str, Dict] = {}  # URL to reviewed data
    upload_complete: bool = False
    next_step: str = "url_generation"
    logs: List[str] = []
    config: Config = None  # Configuration object

    def add_log(self, message: str):
        self.logs.append(message)
        print(message)  # For demonstration purposes

    def reset(self):
        self.urls_to_be_processed = []
        self.scraper_choices = {}
        self.articles = {}
        self.extracted_data = {}
        self.reviewed_data = {}
        self.upload_complete = False
        self.next_step = "url_generation"
        self.logs = []
