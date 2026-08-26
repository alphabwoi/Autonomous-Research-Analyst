"""
Web search tool — wraps the Tavily API so the agent graph can call it
as a simple "tool". Excludes low-trust domains (e.g. Reddit) by default.
"""

import os
from tavily import TavilyClient
from dotenv import load_dotenv

load_dotenv()

_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

# Domains excluded from all web searches by default. Add more here
# as needed — kept in one place so it's easy to edit without touching
# the search logic itself.
EXCLUDED_DOMAINS = [
    "reddit.com",
    "quora.com",
    "pinterest.com",
]


def web_search(query: str, max_results: int = 5) -> list[dict]:
    """
    Search the live web via Tavily, excluding low-trust domains.
    Returns a list of dicts with title, url, and content snippet.
    """
    response = _client.search(
        query=query,
        max_results=max_results,
        exclude_domains=EXCLUDED_DOMAINS,
    )

    results = []
    for item in response.get("results", []):
        results.append({
            "title": item.get("title", ""),
            "url": item.get("url", ""),
            "text": item.get("content", ""),
            "source_filename": item.get("url", "web"),  # keeps field name consistent with rag_tool output
        })

    return results


if __name__ == "__main__":
    # Quick manual test — requires TAVILY_API_KEY in .env
    results = web_search("latest EV battery technology 2026", max_results=3)
    print(f"Found {len(results)} results:")
    for r in results:
        print(f"  - {r['title']} ({r['url']})")
        print(f"    {r['text'][:150]}...")