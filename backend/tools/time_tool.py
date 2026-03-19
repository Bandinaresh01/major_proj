from langchain.tools import tool
import datetime

@tool
def time_tool() -> str:
    """
    Returns the exact current date and time.
    Use this tool when the user asks for the current time, date, or day of the week.
    """
    now = datetime.datetime.now()
    return f"The current date and time is {now.strftime('%A, %B %d, %Y - %I:%M:%S %p')}."
