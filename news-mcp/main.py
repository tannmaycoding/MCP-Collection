from mcp.server.fastmcp import FastMCP
from newsapi import NewsApiClient
import os
from dotenv import load_dotenv

# --- Initialize MCP server
mcp = FastMCP("news-mcp")
load_dotenv()

# --- Initialize NewsAPI
API_KEY = os.environ.get("API_KEY")   # 🔑 replace with your actual key
newsapi = NewsApiClient(api_key=API_KEY)


@mcp.tool()
def top_headlines(query: str = None, sources: str = None, category: str = None,
                  language: str = "en", country: str = "us", page: int = 1):
    """
    Get the latest top headlines.
    - query: search keywords
    - sources: comma-separated source ids (e.g., 'bbc-news,the-verge')
    - category: news category (e.g., 'business', 'technology')
    - language: 2-letter code (default: 'en')
    - country: 2-letter country code (default: 'us')
    - page: pagination
    """
    return newsapi.get_top_headlines(q=query, sources=sources,
                                     category=category, language=language,
                                     country=country, page=page)


@mcp.tool()
def everything(query: str, sources: str = None, domains: str = None,
               from_date: str = None, to_date: str = None,
               language: str = "en", sort_by: str = "relevancy", page: int = 1):
    """
    Get all articles based on a query.
    - query: search keywords (required)
    - sources: comma-separated sources
    - domains: restrict to domains (comma-separated)
    - from_date: YYYY-MM-DD
    - to_date: YYYY-MM-DD
    - language: 2-letter code (default 'en')
    - sort_by: 'relevancy', 'popularity', 'publishedAt'
    - page: pagination
    """
    return newsapi.get_everything(q=query, sources=sources, domains=domains,
                                  from_param=from_date, to=to_date,
                                  language=language, sort_by=sort_by,
                                  page=page)


@mcp.tool()
def list_sources(category: str = None, language: str = "en", country: str = None):
    """
    List available news sources.
    - category: filter by category
    - language: filter by language (default 'en')
    - country: filter by country
    """
    return newsapi.get_sources(category=category, language=language, country=country)


if __name__ == "__main__":
    mcp.run()