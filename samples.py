from datetime import datetime

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

    results = places_client.search(lat, lon, place_type)

    return jsonify(results)