from langchain_community.tools.ddg_search.tool import DuckDuckGoSearchRun
from langchain.tools import tool

ddg_search = DuckDuckGoSearchRun()

@tool
def news_tool(query: str) -> str:
    """
    A tool to find recent news articles.
    Use this when the user asks for news, recent events, or what is happening right now regarding a topic.
    Input should be a search query summarizing the news topic.
    """
    try:
        # Append "news" to the query to guide DuckDuckGo specifically towards news items
        news_query = f"{query} news"
        return ddg_search.run(news_query)
    except Exception as e:
        return f"News search failed: {str(e)}"
