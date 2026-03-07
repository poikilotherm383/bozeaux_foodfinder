import requests
import os
import json
from typing import Literal
from math import pi, cos, sqrt
import time

class MapsClient:
    url = "https://places.googleapis.com/v1/places:searchNearby"
    def __init__(self, config_path):
        self.api_key = self._load_api_key(config_path)

    def _load_api_key(self, config_path):
        with open(config_path, mode = "r") as f:
            self.config_data = json.load(f)
        return self.config_data.get("api_key")
    
    def _calculate_distance(self, lat: float, lon: float, userlat: float, userlon: float):
        if lat is None or lon is None:
            return None
        dlat = abs(lat - userlat) * pi / 180
        dlon = abs(lon - userlon) * pi / 180
        d = 3858.8 * sqrt(dlat ** 2 + (cos(userlat * pi / 180) * dlon) ** 2)
        return d
    
    def _find_next_closing(self, hours: dict):
        ctime = time.localtime().tm_mday + time.localtime().tm_hour / 24 + time.localtime().tm_min / (24 * 60)
        closings = [
            {
                "hour": period["close"]["hour"],
                "minute": period["close"]["minute"],
                "timedelta": period["close"]["date"]["day"] + period["close"]["hour"] / 24 + period["close"]["minute"] / (24 * 60) - ctime
            }
            for period in hours
        ]
        closings.sort(key = lambda x: x["timedelta"])
        hour = closings[0]["hour"]
        minute = closings[0]["minute"]
        return f"""{hour - 12 if hour > 12 else hour}:{minute} {'PM' if hour // 12 == 1 else 'AM'}"""
    
    def _parse_results(self, results: dict, userlat: float, userlon: float):
        open_results = [result for result in results if (result.get("currentOpeningHours") and result["currentOpeningHours"].get("openNow"))]
        parsed_results = []
        for result in open_results:
            lat = result["location"].get("latitude") if result.get("location") is not None else None
            lon = result["location"].get("longitude") if result.get("location")is not None else None
            distance = self._calculate_distance(lat, lon, userlat, userlon)
            parsed_results.append({
                "name": result.get("displayName").get("text") if result.get("displayName") else None,
                "distance": distance,
                "address": result.get("formattedAddress"),
                "url": result.get("websiteUri"),
                "closes_at": self._find_next_closing(result.get("currentOpeningHours").get("periods")),
                "lat": lat,
                "lon": lon
                })
        return parsed_results
    
    def search(self, lat: float, lon: float, type: Literal ["coffee_shop", "restaurant", "chick_fil_a"]):
        if type not in ["coffee_shop", "restaurant"]:
            raise Exception(f"Unknown type {type}")
        payload = {
            "includedPrimaryTypes": [type],
            "maxResultCount": 20,
            "rankPreference": "DISTANCE",
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
            "X-Goog-FieldMask": "places.displayName,places.formattedAddress,places.currentOpeningHours,places.websiteUri,places.location" # mask the data to return with the request here
        }
        response = requests.post(
            self.url,
            headers = headers,
            json = payload
        )
        if not response.status_code == 200:
            raise Exception(f"Maps API returned status code {response.status_code}, full response {response.text}")
        response = response.json()
        parsed_response = self._parse_results(response.get("places", []), lat, lon)
        return parsed_response
