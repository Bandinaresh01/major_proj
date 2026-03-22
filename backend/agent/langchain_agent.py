import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage
from langchain.agents import AgentExecutor
from langchain.agents.output_parsers.tools import ToolsAgentOutputParser
from langchain.agents.format_scratchpad.tools import format_to_tool_messages
from langchain_core.runnables import RunnablePassthrough

from tools.weather import weather_tool
from tools.news import news_tool
from tools.search import search_tool
from tools.time_tool import time_tool
from tools.scrape_tool import scrape_webpage
from tools.finance_tool import finance_tool
from tools.arxiv_tool import arxiv_tool
from tools.gmail_tool import create_read_emails_tool, create_send_email_tool

load_dotenv()

def get_agent_response(query: str, history: list = None, google_credentials: dict = None) -> dict:
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
        temperature=1.0
    )

    tools = [weather_tool, news_tool, search_tool, time_tool, scrape_webpage, finance_tool, arxiv_tool]
    
    if google_credentials:
        tools.append(create_read_emails_tool(google_credentials))
        tools.append(create_send_email_tool(google_credentials))

    SYSTEM_PROMPT = "You are EchoMind, an elite AI assistant with access to real-time tools: weather, news, search, time clock, webpage scraper, finance tracker, and ArXiv academic paper fetcher. " \
                    "If you have access to `read_recent_emails` and `send_email`, you are explicitly connected to the user's secure Gmail account. Use those tools to check their inbox or send emails on their behalf! " \
                    "CRITICAL: You are an advanced agent. For complex queries you MUST use MULTIPLE tools to gather deep context before answering. " \
                    "Synthesize the vast multi-tool data into a comprehensive, highly-detailed, and friendly Markdown response. Do not end your turn prematurely until you have all the facts!"

    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])

    # Resolving root cause: Llama-3 drops arguments objects entirely for 0-arg tools, returning None.
    # We intercept generating AIMessages and explicitly convert None arguments to empty dictionaries {}
    # so the ToolsAgentOutputParser doesn't crash throwing AttributeError.
    def fix_null_args(ai_message: AIMessage) -> AIMessage:
        if hasattr(ai_message, "tool_calls"):
            for tc in ai_message.tool_calls:
                if tc.get("args") is None:
                    tc["args"] = {}
        return ai_message

    llm_with_tools = llm.bind_tools(tools)
    
    # Constructing the exact create_tool_calling_agent chain, but embedding our null safety interceptor
    agent = (
        RunnablePassthrough.assign(
            agent_scratchpad=lambda x: format_to_tool_messages(x["intermediate_steps"])
        )
        | prompt
        | llm_with_tools
        | fix_null_args
        | ToolsAgentOutputParser()
    )

    # Set return_intermediate_steps to True to capture the exact tools the agent decided to use
    agent_executor = AgentExecutor(
        agent=agent, 
        tools=tools, 
        verbose=True,
        return_intermediate_steps=True,
        max_iterations=8,
        handle_parsing_errors=True
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
