# my_agent/utils/state.py

from typing import List, TypedDict
from langchain_core.messages import BaseMessage

class AgentState(TypedDict):
    messages: List[BaseMessage]
    search_terms: List[str]
    urls_to_be_processed: List[str]
    files_to_be_processed: List[str]
    log_messages: List[str]
    sender: str  # Keeps track of the last agent that acted
