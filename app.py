# Lab 10(b): Flask application with routes and HTTP methods.
#
# Routes:
#   GET    /                       -> Home/Base
#   GET    /api/weather?city=XYZ   -> weather for a city
#   GET    /api/favorites          -> list saved favorite cities
#   POST   /api/favorites          -> add a favorite   (JSON body: {"city": "Delhi"})
#   DELETE /api/favorites/<city>   -> remove a favorite


import json
import os

from flask import Flask, jsonify, request

from weather_service import fetch_weather, WeatherError

#creates the web app
app = Flask(__name__)

#favorites are stored in a small JSON file.
FAVORITES_FILE = os.path.join(os.path.dirname(__file__), "favorites.json")


def load_favorites():
    if not os.path.exists(FAVORITES_FILE):
        return []
    with open(FAVORITES_FILE, "r") as f:
        return json.load(f)


def save_favorites(favorites):
    with open(FAVORITES_FILE, "w") as f:
        json.dump(favorites, f)


@app.route("/")
def home():
    return jsonify({"message": "Weather API is running"})


@app.route("/api/weather", methods=["GET"])
def get_weather():
    city = request.args.get("city", "")
    try:
        return jsonify(fetch_weather(city)), 200
    except WeatherError as error:
        return jsonify({"error": error.message}), error.status_code



@app.route("/api/favorites", methods=["GET"])
def list_favorites():
    return jsonify(load_favorites()), 200



@app.route("/api/favorites", methods=["POST"])
def add_favorite():
    body = request.get_json(silent=True) or {}
    city = body.get("city", "").strip()
    if not city:
        return jsonify({"error": "City is required."}), 400

    # Check the city is real by asking the weather service; use the official name it returns.
    try:
        city = fetch_weather(city)["city"]
    except WeatherError as error:
        return jsonify({"error": error.message}), error.status_code

    favorites = load_favorites()
    if city in favorites:
        return jsonify({"error": f"{city} is already in favorites."}), 409

    favorites.append(city)
    save_favorites(favorites)
    return jsonify({"message": f"{city} added.", "favorites": favorites}), 201


@app.route("/api/favorites/<city>", methods=["DELETE"])
def remove_favorite(city):
    favorites = load_favorites()
    if city not in favorites:
        return jsonify({"error": f"{city} is not in favorites."}), 404

    favorites.remove(city)
    save_favorites(favorites)
    return jsonify({"message": f"{city} removed.", "favorites": favorites}), 200


if __name__ == "__main__":
    # debug=True auto-reloads while developing. Turn it off when deploying.
    app.run(debug=False, port=5000)


