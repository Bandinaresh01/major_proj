from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from agent.langchain_agent import get_agent_response
import asyncio

router = APIRouter()

class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    query: str
    history: list[Message] = []

class ChatResponse(BaseModel):
    response: str
    tools_used: list[str] = []

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    try:
        if not request.query.strip():
            raise HTTPException(status_code=400, detail="Query cannot be empty.")
            
        # Function to run the synchronous agent in a background thread
        def run_sync_agent():
            history_dicts = [{"role": msg.role, "content": msg.content} for msg in request.history]
            return get_agent_response(request.query, history_dicts)

        try:
            # Extended heavily to 45.0 seconds. Multi-tool sequential reasoning chains (Search -> Scrape -> Synthesize) take time.
            loop = asyncio.get_event_loop()
            task = loop.run_in_executor(None, run_sync_agent)
            result = await asyncio.wait_for(task, timeout=45.0)
        except asyncio.TimeoutError:
            # If the LLM takes longer than 1 second, cancel and return the exact message
            return ChatResponse(response="Sorry, we will get back to you.", tools_used=[])
        
        if isinstance(result, dict):
            return ChatResponse(
                response=result.get("response", ""),
                tools_used=result.get("tools_used", [])
            )
            
        return ChatResponse(response=str(result), tools_used=[])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
