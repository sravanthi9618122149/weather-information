import requests
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("WEATHER_API_KEY")


def get_weather(city):

    # Find city location
    geo_url = "https://api.openweathermap.org/geo/1.0/direct"

    geo_params = {
        "q": city + ",IN",
        "limit": 1,
        "appid": API_KEY
    }

    geo_response = requests.get(geo_url, params=geo_params)

    if geo_response.status_code != 200:
        return None

    locations = geo_response.json()

    if not locations:
        return None

    lat = locations[0]["lat"]
    lon = locations[0]["lon"]

    # Get weather
    weather_url = "https://api.openweathermap.org/data/2.5/weather"

    weather_params = {
        "lat": lat,
        "lon": lon,
        "appid": API_KEY,
        "units": "metric"
    }

    response = requests.get(weather_url, params=weather_params)

    if response.status_code != 200:
        return None

    data = response.json()

    return {
        "city": data["name"],
        "temperature": data["main"]["temp"],
        "feels_like": data["main"]["feels_like"],
        "humidity": data["main"]["humidity"],
        "description": data["weather"][0]["description"],
        "wind": data["wind"]["speed"]
    }