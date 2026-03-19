import pytest
from tools.time_tool import time_tool
from tools.weather import weather_tool
from tools.finance_tool import finance_tool
from tools.scrape_tool import scrape_webpage

def test_time_tool():
    """Verify time tool requires no arguments and returns a datetime string"""
    result = time_tool.invoke({})
    assert "The current date and time is" in result
    assert "202" in result  # Basic check for year

def test_weather_tool_invalid_location():
    """Testing how weather handles garbage data"""
    result = weather_tool.invoke({"location": "InvalidImaginaryCity_999"})
    # Since it defaults to duckduckgo search or throws an error string, we ensure it's a string
    assert isinstance(result, str)
    assert len(result) > 0

def test_finance_tool_invalid_ticker():
    """Testing stock API resiliency on bad input"""
    result = finance_tool.invoke({"ticker": "ABSOLUTELY_INVALID_TICKER_NAME_123"})
    assert isinstance(result, str)
    assert "Could not fetch data" in result or "N/A" in result

def test_scrape_tool_invalid_url():
    """Testing crawler resilience to blocked or invalid URLs"""
    result = scrape_webpage.invoke({"url": "http://this-url-is-fake-and-will-fail.com"})
    assert isinstance(result, str)
    assert "Failed to scrape webpage" in result
