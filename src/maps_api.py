import requests
import os
import json
from typing import Literal

class MapsClient:
    url = "https://places.googleapis.com/v1/places:searchNearby"
    def __init__(self, config_path):
        self.api_key = self._load_api_key(config_path)

    def _load_api_key(self, config_path):
        with open(config_path, mode = "r") as f:
            self.config_data = json.load(f)
        return self.config_data.get("api_key")
    
    def search(self, lat: float, lon: float, type: Literal ["coffee_shop", "restaurant", "chick_fil_a"]):
        if type not in ["coffee_shop", "restaurant"]:
            raise Exception(f"Unknown type {type}")
        payload = {
            "includedPrimaryTypes": [type],
            "maxResultCount": 20,
            "locationRestriction": {
                "circle": {
                    "center": {
                        "latitude": lat,
                        "longitude": lon},
                "radius": 3000.0
                    }
                }
            }
        headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": self.api_key, # insert api key here
            "X-Goog-FieldMask": "places.displayName,places.formattedAddress,places.currentOpeningHours,places.websiteUri" # mask the data to return with the request here
        }
        response = requests.post(
            self.url,
            headers = headers,
            json = payload
        )
        if not response.status_code == 200:
            raise Exception(f"Maps API returned status code {response.status_code}, full response {response.text}")
        response = response.json()
        outcome = []
        for place in response.get("places"):
            result = {
                "name": "",
                "distance": 0,
                "address": "",
                "url": "",
                "closes_at": "",
                "lat": 0,
                "lon": 0
            }
            result["name"] = place.get("displayName").get("text")
            result["address"] = place.get("formattedAddress")
            result["url"] = place.get("websiteUri")
            outcome.append(result)

        return outcome

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
