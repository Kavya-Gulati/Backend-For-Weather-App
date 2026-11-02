# Lab 9(a): Backend logic written in plain Python.
# This file only knows how to talk to OpenWeatherMap. It knows nothing about Flask.
import os
import requests
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "https://api.openweathermap.org/data/2.5/weather"


class WeatherError(Exception):
    """Our own error type so the Flask app can send a proper message + status code."""

    def __init__(self, message, status_code=500):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


def get_weather_emoji(weather_id):
    # OpenWeatherMap gives a numeric "condition id". We map ranges of ids to emojis.
    if 200 <= weather_id <= 232:
        return "⛈️"
    elif 300 <= weather_id <= 321:
        return "🌦️"
    elif 500 <= weather_id <= 531:
        return "🌧️"
    elif 600 <= weather_id <= 622:
        return "🌨️"
    elif 701 <= weather_id <= 741:
        return "🌁"
    elif weather_id == 762:
        return "🌋"
    elif weather_id == 771:
        return "💨"
    elif weather_id == 781:
        return "🌪️"
    elif weather_id == 800:
        return "☀️"
    elif 801 <= weather_id <= 804:
        return "☁️"
    return "🌡️"  # fallback so the emoji is never empty


def fetch_weather(city):
    """Get weather for a city and return a clean dictionary.
    Raises WeatherError if anything goes wrong."""
    api_key = os.environ.get("API_KEY")
    if not api_key:
        raise WeatherError("Server has no API key configured.", 500)

    city = city.strip()
    if not city:
        raise WeatherError("Please enter a city name.", 400)

    try:
        response = requests.get(
            BASE_URL,
            params={"q": city, "appid": api_key, "units": "metric"},
            timeout=10,
        )
    except requests.exceptions.Timeout:
        raise WeatherError("The weather service timed out.", 504)
    except requests.exceptions.ConnectionError:
        raise WeatherError("Could not connect to the weather service.", 503)
    except requests.exceptions.RequestException as error:
        raise WeatherError(f"Request error: {error}", 500)

    if response.status_code == 404:
        raise WeatherError("City not found.", 404)
    if response.status_code == 401:
        raise WeatherError("Invalid API key on the server.", 500)
    if response.status_code != 200:
        raise WeatherError(f"Weather service error ({response.status_code}).", 502)

    data = response.json()
    print(data)
    weather = data["weather"][0]

    return {
        "city": data["name"],
        "country": data["sys"].get("country", ""),
        "temp": round(data["main"]["temp"]),        # already in °C because of units=metric
        "feels_like": round(data["main"]["feels_like"]),
        "humidity": data["main"]["humidity"],
        "description": weather["description"],
        "emoji": get_weather_emoji(weather["id"]),
    }
fetch_weather('delhi')