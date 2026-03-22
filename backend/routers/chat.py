from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional, Any
from agent.langchain_agent import get_agent_response
import asyncio

router = APIRouter()

class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    query: str
    history: List[Dict[str, str]] = []
    google_credentials: Optional[Dict[str, Any]] = None

class ChatResponse(BaseModel):
    response: str
    tools_used: list[str] = []

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    try:
        if not request.query.strip():
            raise HTTPException(status_code=400, detail="Query cannot be empty.")

        try:
            # Run agent executor synchronously inside a threadpool to not block the asyncio event loop
            loop = asyncio.get_running_loop()
            task = loop.run_in_executor(
                None,
                lambda: get_agent_response(request.query, request.history, request.google_credentials)
            )
            # Extended heavily to 45.0 seconds. Multi-tool sequential reasoning chains (Search -> Scrape -> Synthesize) take time.
            result = await asyncio.wait_for(task, timeout=45.0)
        except asyncio.TimeoutError:
            # If the LLM takes longer than 45 seconds, cancel and return the exact message
            return ChatResponse(response="Sorry, we will get back to you.", tools_used=[])
        
        if isinstance(result, dict):
            return ChatResponse(
                response=result.get("response", ""),
                tools_used=result.get("tools_used", [])
            )
            
        return ChatResponse(response=str(result), tools_used=[])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
