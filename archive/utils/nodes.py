# my_agent/utils/nodes.py

# Standard library imports
import json
from pathlib import Path
from typing import List, Optional, Dict
from urllib.parse import quote, urlencode
import logging

# Third-party imports
import requests  # For making HTTP requests
from bs4 import BeautifulSoup  # For parsing HTML
from neo4j import GraphDatabase  # For interacting with Neo4j database
import jsonschema  # For JSON schema validation

# LangChain imports for NLP tasks
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langgraph.graph import END

# Local imports
from .state import AgentState  # Custom state management
from .config import Config  # Configuration settings
from .prompts.article_extraction_prompts import ARTICLE_EXTRACTION_PROMPT  # Predefined prompts
from .custom_logging import StateLogHandler

# Initialize configuration
config = Config()

# Configure LangChain tracing if enabled
if config.langchain_tracing_v2:
    import langchain
    langchain.tracing_enabled = True
    langchain.tracing_v2_enabled = True
    langchain.endpoint = config.langchain_endpoint
    langchain.api_key = config.langchain_api_key
    langchain.project = config.langchain_project

# Define the JSON schema for validation
EXTRACTED_DATA_SCHEMA = {
    "type": "object",
    "properties": {
        "url": {"type": "string"},
        "extracted_info": {"type": "object"}
    },
    "required": ["url", "extracted_info"]
}

# URL Lookup Agent
def url_lookup_agent(state: Dict) -> Dict:
    """
    URL Lookup Agent

    Role:
    - Fetches top news article URLs based on provided search terms using Google News.

    Tasks:
    - For each search term, scrapes the Google News search results page.
    - Extracts article URLs from the scraped HTML content.
    - Collects and aggregates URLs from all search terms.
    - Updates the shared state with the list of URLs to be processed.
    - Logs the progress and results of the URL fetching process.

    Anticipated Input:
    - state['search_terms']: List of search terms provided by the user.

    Anticipated Output:
    - Updates state['urls_to_be_processed'] with a list of article URLs.
    - Appends log messages to state['log_messages'].
    - Updates state['messages'] with a completion message.
    - Sets state['sender'] to "URLLookupAgent".

    Note:
    - Uses BeautifulSoup to parse Google News search results.
    - May be subject to rate limiting or blocking by Google if used excessively.
    """
    logger = config.get_logger('URLLookupAgent')

    # Attach custom handler
    state_log_handler = StateLogHandler(state)
    state_log_handler.setLevel(logging.DEBUG)  # or the level you prefer
    formatter = logging.Formatter('%(levelname)s:%(name)s:%(message)s')
    state_log_handler.setFormatter(formatter)
    logger.addHandler(state_log_handler)

    logger.info("Starting URL Lookup Agent")
    search_terms = state.get('search_terms', [])
    urls = []

    logger.info(f"Starting URL Lookup Agent with search terms: {search_terms}")
    state['log_messages'].append(f"URLLookupAgent Input - search_terms: {search_terms}")

    for term in search_terms:
        term_urls = get_top_google_news_urls(term, logger)
        urls.extend(term_urls)
        logger.info(f"Fetched URLs for '{term}': {term_urls}")
        state['log_messages'].append(f"Fetched URLs for '{term}': {term_urls}")

    state['urls_to_be_processed'] = urls
    logger.info(f"Found {len(urls)} URLs")

    # Remove the custom handler to avoid duplicate logs in future calls
    logger.removeHandler(state_log_handler)

    return state

def get_top_google_news_urls(query: str, logger, num_results: int = 3) -> List[str]:
    """
    Fetches the top news article URLs from Google News based on the search query.
    """
    logger.debug(f"Fetching top {num_results} Google News URLs for query: {query}")
    query = quote(query)
    url = f'https://news.google.com/search?q={query}&hl=en-US&gl=US&ceid=US:en'

    headers = {
        'User-Agent': 'Mozilla/5.0'  # Mimic a browser user agent
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
    except requests.RequestException as e:
        logger.error(f'Failed to retrieve Google News results: {str(e)}')
        return []

    soup = BeautifulSoup(response.content, 'html.parser')
    articles = soup.find_all('article')[:num_results]

    urls = []
    for article in articles:
        # Find the link to the article
        link_tag = article.find('a', class_='VDXfz', href=True)
        if not link_tag:
            link_tag = article.find('a', class_='DY5T1d', href=True)
        if link_tag:
            relative_link = link_tag['href']
            if relative_link.startswith('.'):
                relative_link = relative_link[1:]
            news_url = 'https://news.google.com' + relative_link
            # Follow the redirect to get the actual article URL
            try:
                article_response = requests.get(news_url, headers=headers, allow_redirects=True)
                article_response.raise_for_status()
                article_url = article_response.url
                urls.append(article_url)
                logger.debug(f"Resolved {news_url} to {article_url}")
            except requests.RequestException as e:
                logger.error(f'Failed to retrieve article URL for {news_url}: {str(e)}')
        else:
            logger.warning(f"No link found in article: {article}")
    logger.info(f"Retrieved {len(urls)} URLs from Google News for query: {query}")
    return urls

# Article Extraction Agent
def article_extraction_agent(state: Dict) -> Dict:
    """
    Article Extraction Agent

    Role:
    - Extracts content from the URLs provided by the URL Lookup Agent.
    - Processes the extracted content to generate structured data.

    Tasks:
    - For each URL, scrapes the article content.
    - Uses an LLM to extract structured information from the article text.
    - Saves the extracted data as JSON files.
    - Updates the shared state with the list of JSON files to be processed.
    - Logs the progress and results of the extraction process.

    Anticipated Input:
    - state['urls_to_be_processed']: List of URLs to scrape and process.

    Anticipated Output:
    - Updates state['files_to_be_processed'] with a list of JSON file paths.
    - Appends log messages to state['log_messages'].
    - Updates state['messages'] with a completion message.
    - Sets state['sender'] to "ArticleExtractionAgent".

    Note:
    - Uses OpenAI's ChatGPT for content extraction and structuring.
    - Saves JSON files in a predefined directory.
    """
    logger = config.get_logger('ArticleExtractionAgent')
    llm = ChatOpenAI(
        model_name=config.openai_model_name,
        temperature=config.openai_temperature,
        max_tokens=config.openai_max_tokens,
        openai_api_key=config.openai_api_key
    )

    # Attach custom handler
    state_log_handler = StateLogHandler(state)
    state_log_handler.setLevel(logging.DEBUG)  # or the level you prefer
    formatter = logging.Formatter('%(levelname)s:%(name)s:%(message)s')
    state_log_handler.setFormatter(formatter)
    logger.addHandler(state_log_handler)

    urls = state.get('urls_to_be_processed', [])
    json_files = []
    output_dir = Path("my_agent/data/json_files_to_be_processed")
    output_dir.mkdir(parents=True, exist_ok=True)

    state['log_messages'].append(f"ArticleExtractionAgent Input - urls_to_be_processed: {urls}")

    for article_data in state['urls_to_be_processed']:
        logger.debug(f"Processing article data: {article_data}")
        if not isinstance(article_data, dict) or 'url' not in article_data or 'text' not in article_data:
            logger.error(f"Invalid article data: {article_data}")
            continue
        
        extracted_data = extract_data(article_data, llm, ARTICLE_EXTRACTION_PROMPT, logger, state)
        state['log_messages'].append(f"Extracted data from {article_data['url']}: {extracted_data}")

        if extracted_data:
            file_name = f"{hash(article_data['url'])}.json"
            save_json(extracted_data, file_name, output_dir, logger)
            json_files.append(str(output_dir / file_name))
            logger.info(f"Processed and saved data from {article_data['url']}")
            state['log_messages'].append(f"Processed and saved data from {article_data['url']}")
        else:
            logger.error(f"Failed to extract data from {article_data['url']}")
            state['log_messages'].append(f"Failed to extract data from {article_data['url']}")

    state['files_to_be_processed'] = json_files
    state['log_messages'].append(f"ArticleExtractionAgent Output - files_to_be_processed: {json_files}")
    state['messages'].append(HumanMessage(content="Article Extraction Agent has completed its task.", name="ArticleExtractionAgent"))
    state['sender'] = "ArticleExtractionAgent"

    # Add this debug log at the end of the function, just before returning
    logger.debug(f"Article Extraction Agent completed. Extracted {len(state['files_to_be_processed'])} articles.")

    # Remove the custom handler to avoid duplicate logs in future calls
    logger.removeHandler(state_log_handler)

    return state

def scrape_article(url: str, config: Config, logger: logging.Logger) -> Optional[Dict]:
    logger.debug(f"Attempting to scrape article from URL: {url}")
    try:
        response = requests.get(url, headers=config.headers, timeout=10)
        response.raise_for_status()
        logger.debug(f"Successfully fetched URL: {url}")
        
        soup = BeautifulSoup(response.text, 'html.parser')
        logger.debug(f"Created BeautifulSoup object for URL: {url}")
        
        # Your existing extraction logic here
        # ...

        logger.debug(f"Extracted title: {title[:50]}...")
        logger.debug(f"Extracted text (first 100 chars): {text[:100]}...")
        
        return {"url": url, "title": title, "text": text}
    except Exception as e:
        logger.error(f"Error scraping article from {url}: {str(e)}")
        return None

def scrape_nytimes_article(url: str, config, logger) -> Optional[Dict]:
    """
    Scrape NYTimes Article

    Role:
    - Scrapes article content from NYTimes using their API.

    Anticipated Input:
    - url: The NYTimes article URL.

    Anticipated Output:
    - A dictionary with article details or None if scraping fails.
    """
    try:
        params = {
            'api-key': config.nytimes_api_key,
            'fq': f'web_url:"{url}"'
        }
        api_url = f'https://api.nytimes.com/svc/search/v2/articlesearch.json?{urlencode(params)}'
        logger.debug(f"Fetching NYTimes article from API: {api_url}")
        response = requests.get(api_url)
        response.raise_for_status()
        data = response.json()

        docs = data.get('response', {}).get('docs', [])
        if not docs:
            logger.warning(f"No article found in NYTimes API for URL: {url}")
            return None

        article_data = docs[0]
        headline = article_data.get('headline', {}).get('main', '')
        lead_paragraph = article_data.get('lead_paragraph', '')
        abstract = article_data.get('abstract', '')
        pub_date = article_data.get('pub_date', '')

        article_text = f"{lead_paragraph}\n{abstract}".strip()

        if not article_text:
            logger.warning(f"No article text found for NYTimes URL: {url}")
            return None

        logger.info(f"Fetched NYTimes article from API for URL: {url}")
        return {
            'title': headline or 'No Title',
            'text': article_text,
            'url': url,
            'pub_date': pub_date
        }
    except requests.exceptions.RequestException as e:
        logger.error(f"NYTimes API request error for {url}: {e}")
        return None
    except json.JSONDecodeError as e:
        logger.error(f"JSON decoding error for {url}: {e}")
        return None
    except Exception as e:
        logger.exception(f"Unexpected error processing NYTimes article {url}: {e}")
        return None

def scrape_with_jina(url: str, config, logger) -> Optional[Dict]:
    """
    Scrape with Jina.ai

    Role:
    - Scrapes article content using the Jina.ai API.

    Anticipated Input:
    - url: The article URL.

    Anticipated Output:
    - A dictionary with article details or None if scraping fails.
    """
    try:
        jina_url = f"https://r.jina.ai/{url}"
        headers = {
            "Authorization": f"Bearer {config.jina_api_key}",
            "X-Locale": config.locale,
            "Accept": "application/json",
            "X-Return-Format": config.return_format
        }
        logger.debug(f"Fetching article using Jina.ai Reader API: {jina_url}")

        response = requests.get(jina_url, headers=headers, timeout=30)
        response.raise_for_status()
        data = response.json()

        if data.get('code') != 200:
            logger.error(f"Jina.ai API error for {url}: {data.get('message', 'Unknown error')}")
            return None

        article_text = data.get('data', {}).get('text', '').strip()

        if not article_text:
            logger.warning(f"No article text found for URL: {url}")
            return None

        logger.info(f"Scraped article text from {url} (first 500 chars): {article_text[:500]}")
        return {
            'title': data.get('data', {}).get('title', 'No Title'),
            'text': article_text,
            'url': url
        }
    except requests.exceptions.RequestException as e:
        logger.error(f"Request error for {url}: {e}")
        return None
    except json.JSONDecodeError as e:
        logger.error(f"JSON decoding error for {url}: {e}")
        return None
    except Exception as e:
        logger.exception(f"Unexpected error scraping {url}: {e}")
        return None

def extract_data(article_data: Dict, llm, prompt_template, logger, state) -> Optional[Dict]:
    """
    Extracts structured data from article content using an LLM.

    Args:
        article_data (Dict): The article data including URL and text.
        llm: The language model to use for extraction.
        prompt_template: The prompt template for the LLM.
        logger: The logger object for logging messages.
        state (AgentState): The current state of the agent.

    Returns:
        Optional[Dict]: The extracted and validated data, or None if extraction fails.
    """
    logger.debug(f"Article data keys: {article_data.keys()}")
    logger.debug(f"URL: {article_data.get('url', 'Not found')}")
    logger.debug(f"Text (first 100 chars): {article_data.get('text', 'Not found')[:100]}")
    
    logger.debug(f"Prompt template: {prompt_template}")
    logger.debug(f"Prompt template messages: {prompt_template.messages}")
    
    messages = prompt_template.format_messages(url=article_data['url'], article_text=article_data['text'])
    logger.debug(f"Formatted messages: {messages}")
    logger.debug(f"LLM input messages: {messages}")
    state['log_messages'].append(f"LLM Input Messages: {messages}")

    try:
        response = llm(messages)
        logger.debug(f"LLM response: {response.content}")
        state['log_messages'].append(f"LLM Output: {response.content}")

        # Ensure the response is valid JSON
        extracted_info = json.loads(response.content)

        # Prepare the data to validate
        extracted_data = {
            "url": article_data['url'],
            "extracted_info": extracted_info
        }

        # Validate the data against the schema
        jsonschema.validate(instance=extracted_data, schema=EXTRACTED_DATA_SCHEMA)
        return extracted_data
    except json.JSONDecodeError as e:
        logger.error(f"Error parsing LLM response as JSON: {e}")
        state['log_messages'].append(f"Error parsing LLM response as JSON: {e}")
        return None
    except jsonschema.ValidationError as e:
        logger.error(f"Extracted data validation error: {e}")
        state['log_messages'].append(f"Extracted data validation error: {e}")
        return None
    except Exception as e:
        logger.exception(f"Unexpected error during data extraction: {e}")
        state['log_messages'].append(f"Unexpected error during data extraction: {e}")
        return None

def save_json(data: Dict, file_name: str, output_dir: Path, logger):
    """
    Saves the extracted data to a JSON file.

    Args:
        data (Dict): The data to save.
        file_name (str): The name of the JSON file.
        output_dir (Path): The directory where the file will be saved.
        logger: The logger object for logging messages.
    """
    try:
        with open(output_dir / file_name, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logger.info(f"Saved JSON file: {file_name}")
    except Exception as e:
        logger.error(f"Error saving JSON file {file_name}: {e}")

# Knowledge Graph Uploader Agent
def knowledge_graph_uploader_agent(state: Dict) -> Dict:
    """
    Knowledge Graph Uploader Agent

    Role:
    - Uploads the extracted and structured data to a Neo4j knowledge graph.

    Tasks:
    - Reads the JSON files produced by the Article Extraction Agent.
    - Creates nodes and relationships in the Neo4j database based on the extracted data.
    - Updates the shared state to indicate completion of the upload process.
    - Logs the progress and results of the upload process.

    Anticipated Input:
    - state['files_to_be_processed']: List of JSON file paths to be uploaded.

    Anticipated Output:
    - Appends log messages to state['log_messages'].
    - Updates state['messages'] with a completion message.
    - Sets state['sender'] to "KnowledgeGraphUploaderAgent".

    Note:
    - Uses Neo4j as the graph database.
    - Requires proper configuration of Neo4j connection details.
    """
    logger = config.get_logger('KnowledgeGraphUploaderAgent')
    driver = GraphDatabase.driver(
        config.neo4j_uri,
        auth=(config.neo4j_username, config.neo4j_password)
    )

    # Attach custom handler
    state_log_handler = StateLogHandler(state)
    state_log_handler.setLevel(logging.DEBUG)  # or the level you prefer
    formatter = logging.Formatter('%(levelname)s:%(name)s:%(message)s')
    state_log_handler.setFormatter(formatter)
    logger.addHandler(state_log_handler)

    json_files = state.get('files_to_be_processed', [])
    state['log_messages'].append(f"KnowledgeGraphUploaderAgent Input - files_to_be_processed: {json_files}")

    for file_path in json_files:
        with open(file_path, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
        state['log_messages'].append(f"Uploading data from {file_path}: {json_data}")
        try:
            with driver.session() as session:
                session.write_transaction(create_nodes_and_relationships, json_data)
            logger.info(f"Uploaded data from {file_path} to the knowledge graph.")
            state['log_messages'].append(f"Uploaded data from {file_path} to the knowledge graph.")
        except Exception as e:
            logger.error(f"Error uploading {file_path}: {e}")
            state['log_messages'].append(f"Error uploading {file_path}: {e}")

    driver.close()
    state['messages'].append(HumanMessage(content="Knowledge Graph Uploader Agent has completed its task.", name="KnowledgeGraphUploaderAgent"))
    state['sender'] = "KnowledgeGraphUploaderAgent"

    # Remove the custom handler to avoid duplicate logs in future calls
    logger.removeHandler(state_log_handler)

    return state

def create_nodes_and_relationships(tx, json_data):
    """
    Create Nodes and Relationships

    Role:
    - Executes Cypher queries to create nodes and relationships in Neo4j based on extracted data.

    Anticipated Input:
    - tx: Neo4j transaction.
    - json_data: Extracted data from the article.

    Anticipated Output:
    - Nodes and relationships are created in the Neo4j database.
    """
    # Implementation of create_nodes_and_relationships function
    # You can include the detailed implementation as per previous discussions
    pass  # Replace with actual implementation

# Router Agent
def router_agent(state: Dict) -> str:
    """
    Router Agent

    Role:
    - Determines the next agent to be executed based on the current state.

    Tasks:
    - Checks the current state to decide which agent should run next.
    - Returns the name of the next agent to be executed.

    Anticipated Input:
    - The current AgentState object.

    Anticipated Output:
    - A string indicating the next agent to run or "FINISH" if the workflow is complete.

    Note:
    - This function implements the logic for the state machine transitions.
    """
    if not state.get('urls_to_be_processed'):
        return "URL Lookup"
    elif not state.get('files_to_be_processed'):
        return "Article Extraction"
    elif not state.get('completed_upload', False):
        return "Knowledge Graph Upload"
    else:
        return END  # Indicate that the workflow is complete