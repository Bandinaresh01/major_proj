import pytest
from fastapi.testclient import TestClient
from app import app

client = TestClient(app)

def test_chat_endpoint_missing_body():
    # Sending empty body should trigger a 422 Unprocessable Entity due to Pydantic validation
    response = client.post("/api/chat", json={})
    assert response.status_code == 422
    assert "detail" in response.json()

def test_chat_endpoint_valid_schema_but_no_api_key(monkeypatch):
    """
    Test the behavior when GROQ_API_KEY is completely missing.
    The backend should elegantly fall back without crashing the server.
    """
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    
    response = client.post("/api/chat", json={
        "query": "Hello?",
        "history": []
    })
    
    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert "tools_used" in data
    assert "GROQ_API_KEY is not set" in data["response"]
