import pytest
from unittest.mock import patch
from agent.langchain_agent import get_agent_response

def test_agent_missing_api_key(monkeypatch):
    """If the API key is missing entirely, the agent should catch it immediately and not crash!"""
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    result = get_agent_response("Hello")
    assert isinstance(result, dict)
    assert "GROQ_API_KEY is not set" in result["response"]
    assert result["tools_used"] == []

@patch("agent.langchain_agent.AgentExecutor.invoke")
def test_agent_retry_loop_recovery(mock_invoke):
    """
    Test the robust retry loop for JSON parser crashes.
    If the agent crashes twice with NoneType, it should recover on the 3rd invoke.
    """
    # Throw an exception twice, then return a valid response dict
    mock_invoke.side_effect = [
        AttributeError("'NoneType' object has no attribute 'get'"),
        AttributeError("'NoneType' object has no attribute 'get'"),
        {"output": "I recovered!", "intermediate_steps": []}
    ]
    
    result = get_agent_response("Will you survive?")
    
    assert result["response"] == "I recovered!"
    assert result["tools_used"] == []
    assert mock_invoke.call_count == 3

@patch("agent.langchain_agent.AgentExecutor.invoke")
def test_agent_terminal_failure(mock_invoke):
    """If the LLM crashes 3 times in a row, the try-except should catch it gracefully and return an error string."""
    mock_invoke.side_effect = Exception("Catastrophic LLM Failure")
    
    result = get_agent_response("Crash test")
    
    assert "An error occurred while processing your request: Catastrophic LLM Failure" in result["response"]
    assert mock_invoke.call_count == 3
