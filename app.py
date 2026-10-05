import os
import requests
import streamlit as st
from dotenv import load_dotenv
from google import genai

load_dotenv()

WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

st.set_page_config(
    page_title="Weather AI Chatbot",
    page_icon="🌤️",
    layout="centered"
)

st.title("🌤️ Weather AI Chatbot")
st.write("Get current weather information using Weather API and Gemini AI.")

if not WEATHER_API_KEY:
    st.error("WEATHER_API_KEY is missing in the .env file.")
    st.stop()

if not GEMINI_API_KEY:
    st.error("GEMINI_API_KEY is missing in the .env file.")
    st.stop()

try:
    gemini_client = genai.Client(api_key=GEMINI_API_KEY)
except Exception as e:
    st.error(f"Gemini configuration error: {e}")
    st.stop()


def get_weather(city):
    url = "https://api.openweathermap.org/data/2.5/weather"

    params = {
        "q": city,
        "appid": WEATHER_API_KEY,
        "units": "metric"
    }

    try:
        response = requests.get(url, params=params, timeout=10)

        if response.status_code == 404:
            return None, "City not found. Please enter a valid city name."

        if response.status_code == 401:
            return None, "Invalid Weather API key."

        response.raise_for_status()

        return response.json(), None

    except requests.exceptions.RequestException as e:
        return None, f"Weather API error: {e}"


def generate_ai_response(weather):
    city = weather["name"]
    country = weather["sys"]["country"]
    temperature = weather["main"]["temp"]
    feels_like = weather["main"]["feels_like"]
    humidity = weather["main"]["humidity"]
    pressure = weather["main"]["pressure"]
    wind_speed = weather["wind"]["speed"]
    description = weather["weather"][0]["description"]

    prompt = f"""
You are a helpful weather assistant.

Give a simple weather explanation using these current weather details:

City: {city}, {country}
Temperature: {temperature} °C
Feels like: {feels_like} °C
Weather: {description}
Humidity: {humidity}%
Pressure: {pressure} hPa
Wind Speed: {wind_speed} m/s

Explain:
1. Current weather
2. How the temperature feels
3. Humidity and wind
4. Simple advice for the user

Keep the answer short and easy to understand.
"""

    try:
        response = gemini_client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        return response.text

    except Exception as e:
        return f"Gemini error: {e}"


city = st.text_input(
    "Enter city name",
    placeholder="Example: Hyderabad"
)

if st.button("Get Weather", type="primary"):

    if not city.strip():
        st.warning("Please enter a city name.")
        st.stop()

    with st.spinner("Getting weather information..."):
        weather, error = get_weather(city.strip())

    if error:
        st.error(error)
        st.stop()

    st.success(f"Weather information for {weather['name']}, {weather['sys']['country']}")

    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            "Temperature",
            f"{weather['main']['temp']} °C"
        )

        st.metric(
            "Feels Like",
            f"{weather['main']['feels_like']} °C"
        )

        st.metric(
            "Humidity",
            f"{weather['main']['humidity']}%"
        )

    with col2:
        st.metric(
            "Wind Speed",
            f"{weather['wind']['speed']} m/s"
        )

        st.metric(
            "Pressure",
            f"{weather['main']['pressure']} hPa"
        )

        st.write(
            f"**Condition:** {weather['weather'][0]['description'].title()}"
        )

    st.divider()

    st.subheader("🤖 Gemini AI Weather Analysis")

    with st.spinner("Gemini is analyzing the weather..."):
        ai_response = generate_ai_response(weather)

    st.write(ai_response)