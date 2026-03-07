from datetime import datetime
from flask import Flask, render_template, request, jsonify
import os
import requests
from maps_api import MapsClient
import json

config_path = os.path.join(os.path.dirname(__file__), "config", "config.json")
with open(config_path, mode = "r") as file:
    config = json.load(file)
static_url_path = config.get("static_url_path")

app = Flask(__name__)
maps_client = MapsClient(config_path)

# flask theme selection: chooses light mode or dark mode
@app.route("/")
def home():
    hour = datetime.now().hour
    if 7 <= hour <= 19:
        theme = "light"
    else:
        theme = "dark"
    return render_template("index.html", theme = theme, url_root = static_url_path)

# flask search endpoint    
@app.route("/search", methods = ["POST"])
def search():
    data = request.json
    place_type = data.get("type")
    lat = data.get("lat")
    lon = data.get("lon")
    if any([val is None for val in [place_type, lat, lon]]):
        return jsonify({"message": "Bad request format"}), 400
    try:
        results, radius = maps_client.search(lat, lon, place_type)
    except Exception as e:
        return jsonify({"message": e}), 500
    if len(results) == 0:
        return jsonify({"message": f"No places found within {radius:.0f} miles", "empty": True}), 404
    return jsonify(results)

@app.route("/search_expand", methods = ["POST"])
def search_expand():
    data = request.json
    place_type = data.get("type")
    lat = data.get("lat")
    lon = data.get("lon")
    if any([val is None for val in [place_type, lat, lon]]):
        return jsonify({"message": "Bad request format"}), 400
    try:
        results, radius = maps_client.search_expand(lat, lon, place_type)
    except Exception as e:
        return jsonify({"message": e}), 500
    if len(results) == 0:
        return jsonify({"message": f"No places found within {radius:.0f} miles", "empty": True}), 404
    return jsonify(results)

if __name__ == "__main__":
    app.run(host = "127.0.0.1", port = 5050)