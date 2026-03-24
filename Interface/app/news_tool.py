import os
from dotenv import load_dotenv
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain.tools import Tool

# Load environment variables
load_dotenv()

# Get Tavily API Key
tavily_key = os.getenv("TAVILY_API_KEY")

if not tavily_key:
    # This will appear in Cloud Run logs
    print("WARNING: TAVILY_API_KEY is not set in environment variables.")

# Initialize Tavily search
search = TavilySearchResults(
    max_results=5,
    tavily_api_key=tavily_key
)


def search_news(query: str) -> str:
    """
    Executes a Tavily search for news and current events.
    This wrapper ensures the agent always receives a clean response.
    """
    try:
        results = search.run(query)

        if not results:
            return "No news results were found for this query."

        return results

    except Exception as e:
        return f"News search failed: {str(e)}"


# LangChain Tool used by the agent
news_search_tool = Tool(
    name="news_search",
    description="Search for the latest news and current events on the internet.",
    func=search_news,
)