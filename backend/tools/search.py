from langchain_community.tools.ddg_search.tool import DuckDuckGoSearchRun
from langchain.tools import tool

ddg_search = DuckDuckGoSearchRun()

@tool
def search_tool(query: str) -> str:
    """
    A search engine for general queries. 
    Use this when you need general information, facts, or to answer questions about topics other than current news or weather.
    Input should be a search query.
    """
    try:
        return ddg_search.run(query)
    except Exception as e:
        return f"General search failed: {str(e)}"
