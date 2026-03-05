import requests
import os
import json

def load_api_key(config_path):
    with open(config_path, mode = "r") as f:
        config_data = json.load(f)
    return config_data.get("api_key")

def search_nearby(api_key):
    url = "https://places.googleapis.com/v1/places:searchNearby"
    payload = {
        "includedPrimaryTypes": ["coffee_shop"],
        "maxResultCount": 20,
        "locationRestriction": {
            "circle": {
                "center": {
                    "latitude": 30.2132,
                    "longitude": -81.6049},
            "radius": 3000.0
                }
            }
        }
    header = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": api_key, # insert api key here
        "X-Goog-FieldMask": "places.displayName,places.formattedAddress,places.currentOpeningHours" # mask the data to return with the request here
    }
    response = requests.post(
        url,
        headers = header,
        json = payload
    )
    return response

if __name__ == "__main__":
    config_path = os.path.join(os.path.dirname(__file__), "config", "config.json")
    api_key = load_api_key(config_path)
    response = search_nearby(api_key)
    if response.status_code == 200:
        result = response.json()
        places = result.get("places", [])
        for place in places:
            display_name = place.get('displayName').get('text')
            formatted_address = place.get('formattedAddress')
            hours = place.get('currentOpeningHours')
            if hours is not None:
                open_now = hours.get("openNow")
            else:
                open_now = None
            print(f"""{display_name} at {formatted_address}{"" if open_now is None else f", currently {'open' if open_now else 'closed'}"}""")
