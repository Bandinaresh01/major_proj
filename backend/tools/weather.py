import requests
from langchain.tools import tool

@tool
def weather_tool(location: str) -> str:
    """
    Fetch the current weather for a given location. 
    Use this tool when the user asks about the weather in a specific city or place.
    Input should be a simple location name (e.g., 'London', 'Tokyo').
    """
    try:
        # Step 1: Geocoding to get lat/lon
        geocode_url = f"https://geocoding-api.open-meteo.com/v1/search?name={location}&count=1&language=en&format=json"
        geo_response = requests.get(geocode_url).json()
        
        if "results" not in geo_response or len(geo_response["results"]) == 0:
            return f"Could not find coordinates for {location}."
            
        lat = geo_response["results"][0]["latitude"]
        lon = geo_response["results"][0]["longitude"]
        name = geo_response["results"][0]["name"]
        
        # Step 2: Fetch weather data
        weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
        weather_response = requests.get(weather_url).json()
        
        if "current_weather" not in weather_response:
            return "Could not retrieve weather data."
            
        current = weather_response["current_weather"]
        temperature = current["temperature"]
        windspeed = current["windspeed"]
        
        return f"The current weather in {name} is {temperature}°C with a wind speed of {windspeed} km/h."
    except Exception as e:
        return f"Failed to fetch weather: {str(e)}"
