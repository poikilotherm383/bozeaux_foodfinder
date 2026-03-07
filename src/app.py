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

app = Flask(__name__, static_url_path = static_url_path)

config_path = os.path.join(os.path.dirname(__file__), "config", "config.json")

maps_client = MapsClient(config_path)

# flask theme selection: chooses light mode or dark mode
@app.route("/")
def home():

    hour = datetime.now().hour

    if 7 <= hour <= 19:
        theme = "light"
    else:
        theme = "dark"

    return render_template("index.html", theme=theme)

# flask search endpoint    
@app.route("/search", methods=["POST"])
def search():

    data = request.json

    place_type = data["type"]
    lat = data["lat"]
    lon = data["lon"]

    results = maps_client.search(lat, lon, place_type)

    return jsonify(results)

if __name__ == "__main__":
    app.run(host = "0.0.0.0")