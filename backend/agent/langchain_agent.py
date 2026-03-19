import os
from langchain_groq import ChatGroq
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage
from dotenv import load_dotenv

from tools.weather import weather_tool
from tools.news import news_tool
from tools.search import search_tool
from tools.time_tool import time_tool
from tools.scrape_tool import scrape_webpage
from tools.finance_tool import finance_tool
from tools.arxiv_tool import arxiv_tool

load_dotenv()

def get_agent_response(query: str, history: list = None) -> dict:
    """
    Initializes the agent with the Groq model and available tools,
    then executes the query using robust tool calling.
    Returns a dictionary with the final 'response' and a list of 'tools_used'.
    """
    groq_api_key = os.getenv("GROQ_API_KEY")
    if not groq_api_key or groq_api_key == "your_groq_api_key_here":
        return {"response": "Error: GROQ_API_KEY is not set or is invalid in the environment variables.", "tools_used": []}

    llm = ChatGroq(
        groq_api_key=groq_api_key, 
        model_name="llama-3.1-8b-instant",  
        temperature=0.0
    )

    tools = [weather_tool, news_tool, search_tool, time_tool, scrape_webpage, finance_tool, arxiv_tool]

    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are EchoMind, an elite AI assistant with access to real-time tools: weather, news, search, time clock, webpage scraper, finance tracker, and ArXiv academic paper fetcher. "
                   "Always use the tools to answer questions about current events, local conditions, exact time, or specific facts. "
                   "CRITICAL: You are an advanced agent. For complex queries you MUST use MULTIPLE tools to gather deep context before answering. "
                   "For example, use 'finance_tool' for crypto/stock prices, use 'search_tool' to find details, use 'news_tool' for market reactions, "
                   "use 'arxiv_tool' to fetch research papers, and use 'scrape_webpage' to physically read an official link. "
                   "Synthesize the vast multi-tool data into a comprehensive, highly-detailed, and friendly Markdown response. Do not end your turn prematurely until you have all the facts!"),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}"),
        ("placeholder", "{agent_scratchpad}"),
    ])

    agent = create_tool_calling_agent(llm, tools, prompt)

    # Set return_intermediate_steps to True to capture the exact tools the agent decided to use
    agent_executor = AgentExecutor(
        agent=agent, 
        tools=tools, 
        verbose=True,
        return_intermediate_steps=True,
        max_iterations=8
    )

    # Convert history dicts into LangChain Message objects
    formatted_history = []
    if history:
        for msg in history:
            if msg.get("role") == "user":
                formatted_history.append(HumanMessage(content=msg.get("content", "")))
            elif msg.get("role") == "assistant":
                formatted_history.append(AIMessage(content=msg.get("content", "")))

    try:
        response_data = None
        # Robust 3-attempt retry loop to handle transient LLM JSON parsing crashes (e.g. NoneType object has no attribute 'get' deep in LangChain).
        for attempt in range(3):
            try:
                response_data = agent_executor.invoke({
                    "input": query,
                    "chat_history": formatted_history
                })
                if response_data:
                    break
            except Exception as e:
                if attempt == 2:
                    raise e
                
        if not response_data:
            response_data = {}
            
        output = response_data.get("output", "No response generated.") if isinstance(response_data, dict) else str(response_data)
        
        # Extract tools used from intermediate steps
        intermediate_steps = response_data.get("intermediate_steps", []) if isinstance(response_data, dict) else []
        tools_used = []
        for action, observation in intermediate_steps:
            if hasattr(action, "tool"):
                tools_used.append(action.tool)
                
        # Deduplicate tools
        tools_used = list(dict.fromkeys(tools_used))
        
        return {"response": output, "tools_used": tools_used}
    except Exception as e:
        return {"response": f"An error occurred while processing your request: {e}", "tools_used": []}
