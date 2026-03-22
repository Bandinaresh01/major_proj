import pytest
from unittest.mock import patch
from langchain_core.messages import HumanMessage, AIMessage
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

@patch("agent.langchain_agent.AgentExecutor.invoke")
def test_agent_history_formatting(mock_invoke):
    """Ensure raw basic dicts convert perfectly into specialized Langchain Message variables."""
    mock_invoke.return_value = {"output": "History parsing works"}
    history = [
        {"role": "user", "content": "Who are you?"},
        {"role": "assistant", "content": "I am EchoMind"},
        {"role": "invalid_role", "content": "Should be ignored safely"}
    ]
    get_agent_response("Test", history)
    
    # Extract the args passed deeply to invoke
    invoke_args = mock_invoke.call_args[0][0]
    hist_objs = invoke_args.get("chat_history", [])
    assert len(hist_objs) == 2
    assert isinstance(hist_objs[0], HumanMessage)
    assert isinstance(hist_objs[1], AIMessage)

@patch("agent.langchain_agent.AgentExecutor.__init__")
def test_agent_no_credentials_no_gmail(mock_init):
    """If no Google tokens are assigned, Agent dynamically refuses to mount Gmail tooling."""
    mock_init.side_effect = Exception("Stop execution early")
    try:
        get_agent_response("Test")
    except Exception:
        pass
    # The tools list is passed to AgentExecutor as a kwarg or second arg
    # Signature: AgentExecutor(agent=agent, tools=tools, ...)
    tool_list = mock_init.call_args[1].get('tools', []) if mock_init.call_args else []
    tool_names = [t.name for t in tool_list]
    assert "read_recent_emails" not in tool_names
    assert "send_email" not in tool_names

@patch("agent.langchain_agent.AgentExecutor.__init__")
def test_agent_google_credentials_binding(mock_init):
    """If tokens are detected, the agent silently binds the Gmail integration."""
    mock_init.side_effect = Exception("Stop execution early")
    dummy_creds = {"access_token": "123", "refresh_token": "456", "token_uri": "", "client_id": "", "client_secret": "", "scopes": []}
    try:
        get_agent_response("Test", None, dummy_creds)
    except Exception:
        pass
    tool_list = mock_init.call_args[1].get('tools', []) if mock_init.call_args else []
    tool_names = [t.name for t in tool_list]
    assert "read_recent_emails" in tool_names
    assert "send_email" in tool_names

def test_agent_deduplicates_tools(monkeypatch):
    """Verifies that an agent reasoning loop chaining the exact same tool multiple times filters dynamically down to single uniqueness."""
    monkeypatch.setenv("GROQ_API_KEY", "dummy_key_to_bypass_early_rejection")
    
    class DummyTool:
        def __init__(self, name):
            self.name = name
            
    class DummyAction:
        def __init__(self, name):
            self.tool = name
            
    with patch("agent.langchain_agent.AgentExecutor.invoke") as mock_invoke:
        mock_invoke.return_value = {
            "output": "Test deduplication",
            "intermediate_steps": [
                (DummyAction("Search"), "obs1"),
                (DummyAction("Search"), "obs2"),
                (DummyAction("News"), "obs3")
            ]
        }
        result = get_agent_response("Deduplicate me")
        assert len(result["tools_used"]) == 2
        assert "Search" in result["tools_used"]
        assert "News" in result["tools_used"]
