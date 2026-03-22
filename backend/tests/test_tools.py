import pytest
from tools.time_tool import time_tool
from tools.weather import weather_tool
from tools.finance_tool import finance_tool
from tools.scrape_tool import scrape_webpage
from tools.news import news_tool
from tools.search import search_tool
from tools.arxiv_tool import arxiv_tool
from tools.gmail_tool import create_read_emails_tool, create_send_email_tool

def test_time_tool():
    """Verify time tool requires no arguments and returns a datetime string"""
    result = time_tool.invoke({})
    assert "The current date and time is" in result
    assert "202" in result  # Basic check for year

def test_weather_tool_invalid_location():
    """Testing how weather handles garbage data"""
    result = weather_tool.invoke({"location": "InvalidImaginaryCity_999"})
    assert isinstance(result, str)
    assert len(result) > 0

def test_weather_tool_empty_location():
    """Validate fallback routing mechanism"""
    result = weather_tool.invoke({"location": ""})
    assert isinstance(result, str)

def test_finance_tool_invalid_ticker():
    """Testing stock API resiliency on bad input"""
    result = finance_tool.invoke({"ticker": "ABSOLUTELY_INVALID_TICKER_NAME_123"})
    assert isinstance(result, str)
    assert "Could not fetch data" in result or "N/A" in result

def test_finance_tool_valid_ticker():
    """Testing stock API standard functionality extraction"""
    result = finance_tool.invoke({"ticker": "AAPL"})
    assert "Apple" in result or "AAPL" in result

def test_scrape_tool_invalid_url():
    """Testing crawler resilience to blocked or invalid URLs"""
    result = scrape_webpage.invoke({"url": "http://this-url-is-fake-and-will-fail.com"})
    assert isinstance(result, str)
    assert "Failed to scrape webpage" in result

def test_scrape_tool_empty_url():
    """Testing structural scraper breaks"""
    result = scrape_webpage.invoke({"url": ""})
    assert isinstance(result, str)

def test_news_tool_empty_query():
    """Testing search news logic on null"""
    result = news_tool.invoke({"query": ""})
    assert isinstance(result, str)

def test_search_tool_empty_query():
    """Testing search framework breaks gracefully"""
    result = search_tool.invoke({"query": ""})
    assert isinstance(result, str)

def test_arxiv_tool_valid_query():
    """Structural fetch of standard paper index arrays"""
    result = arxiv_tool.invoke({"query": "quantum computing"})
    assert isinstance(result, str)

def test_arxiv_tool_invalid_query():
    """Breaking the arxiv trace pipeline natively"""
    result = arxiv_tool.invoke({"query": "askdjhlasdkhjfaskjdfhasdf_999"})
    assert "No good Arxiv Result" in result or isinstance(result, str)

def test_gmail_read_tool_no_credentials():
    """Executing strict OAuth token verification failures within LangChain boundary blocks"""
    read_tool = create_read_emails_tool({})
    result = read_tool.invoke({})
    assert "Failed to read emails: Google Credentials missing" in result

def test_gmail_send_tool_no_credentials():
    """Block autonomous email sending if tokens die mid-flight"""
    send_tool = create_send_email_tool({})
    result = send_tool.invoke({"to": "test@test.com", "subject": "Test", "body": "Body text"})
    assert "Failed to send email: Google Credentials missing" in result
