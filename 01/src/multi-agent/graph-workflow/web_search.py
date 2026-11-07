from tavily import TavilyClient
import json
import os
from strands import tool

client = TavilyClient(os.getenv("TAVILY_API_KEY"))




@tool()
def web_search(query: str, max_results: int = 8, topic: str = "general") -> str:
    """Search the public web for research. Returns ranked titles, URLs, snippets and scores.

    Args:
        query: Specific search query. Include date or region where relevant.
        max_results: Number of results, from 1 to 10.
        topic: 'general' or 'news'.
    """
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        return "Configuration error: TAVILY_API_KEY is not set."
    response = client.search(
        query=query,
        search_depth="advanced",
        time_range="month",
        include_raw_content="markdown"
        )

    return json.dumps(response)



