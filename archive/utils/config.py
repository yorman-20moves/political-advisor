# my_agent/utils/config.py

import os
import sys
import logging
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Logger setup
    @staticmethod
    def get_logger(name):
        logging.basicConfig(level=logging.INFO)
        return logging.getLogger(name)

    logger = get_logger('Config')

    # OpenAI configuration
    openai_api_key = os.getenv('OPENAI_API_KEY')
    if not openai_api_key:
        logger.error("OPENAI_API_KEY is not set in the environment variables.")
        sys.exit(1)

    openai_model_name = os.getenv('OPENAI_MODEL_NAME', 'gpt-4o')
    openai_max_tokens = int(os.getenv('OPENAI_MAX_TOKENS', '4095'))
    openai_temperature = float(os.getenv('OPENAI_TEMPERATURE', '1'))

    # Neo4j configuration
    neo4j_uri = os.getenv('NEO4J_URI')
    neo4j_username = os.getenv('NEO4J_USERNAME')
    neo4j_password = os.getenv('NEO4J_PASSWORD')
    if not neo4j_uri or not neo4j_username or not neo4j_password:
        logger.error("Neo4j credentials are not fully set in the environment variables.")
        sys.exit(1)

    # Scraping configuration
    jina_api_key = os.getenv('JINA_API_KEY')
    nytimes_api_key = os.getenv('NYTIMES_API_KEY')
    if not jina_api_key:
        logger.warning("JINA_API_KEY is not set. Some scraping functions may not work.")
    if not nytimes_api_key:
        logger.warning("NYTIMES_API_KEY is not set. NYTimes scraping will not work.")

    # LangChain/LangSmith configuration
    langchain_tracing_v2 = os.getenv('LANGCHAIN_TRACING_V2', 'false').lower() == 'true'
    langchain_endpoint = os.getenv('LANGCHAIN_ENDPOINT')
    langchain_api_key = os.getenv('LANGCHAIN_API_KEY')
    langchain_project = os.getenv('LANGCHAIN_PROJECT')

    # Other configurations
    locale = 'en-US'
    return_format = 'text'
