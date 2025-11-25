from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.tools import tool
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import warnings

load_dotenv()
# For suppressing LangChain deprecation warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

# Tavily returns a list of dicts: [{'url': '...', 'content': '...'}]
search = TavilySearchResults(max_results=3)

@tool
def web_search(query: str) -> list:
    """Search the web for fitness exercises and tutorials. Returns a list of results with URLs."""
    return search.invoke(query)

@tool
def scrape_content(url: str) -> str:
    """Scrape text content from a given URL for RAG processing."""
    try:
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            return f"Error: Status code {response.status_code}"
        soup = BeautifulSoup(response.content, 'html.parser')
        # Extract paragraphs and headers
        text = ' '.join([p.get_text() for p in soup.find_all(['p', 'h1', 'h2', 'h3'])])
        return text[:5000] # Limit context size
    except Exception as e:
        return f"Error scraping {url}: {str(e)}"


@tool
def save_workout_plan(content: str, filename: str = "workout_plan.md") -> str:
    """Save the generated workout plan to a local file."""
    try:
        with open(filename, "w", encoding="utf-8") as f:
            f.write(content)
        return f"Successfully saved plan to {filename}"
    except Exception as e:
        return f"Error saving file: {str(e)}"
