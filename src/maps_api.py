import requests
import json
from typing import Literal
from math import pi, cos, sqrt
import time

def miles_to_m(miles: float):
    return round(miles * 1.60934e3)
def m_to_miles(m: float):
    return round(m / 1.60934e3)

class MapsClient:
    url = "https://places.googleapis.com/v1/places"
    day_dict = {
        0: "Sunday",
        1: "Monday",
        2: "Tuesday",
        3: "Wednesday",
        4: "Thursday",
        5: "Friday",
        6: "Saturday"
    }
    def __init__(self, config_path):
        self.api_key = self._load_api_key(config_path)

    def _load_api_key(self, config_path):
        with open(config_path, mode = "r") as f:
            self.config_data = json.load(f)
        return self.config_data.get("api_key")
    
    def _calculate_distance(self, lat: float, lon: float, userlat: float, userlon: float):
        if (lat is None) or (lon is None):
            return None
        dlat = abs(lat - userlat) * pi / 180
        dlon = abs(lon - userlon) * pi / 180
        d = 3858.8 * sqrt(dlat ** 2 + (cos(userlat * pi / 180) * dlon) ** 2)
        return d
    
    def _find_next_closing(self, hours: list):
        if not isinstance(hours, list):
            return None
        ctime = time.localtime().tm_mday + time.localtime().tm_hour / 24 + time.localtime().tm_min / (24 * 60)
        today = time.localtime().tm_mday
        try:
            closings = [
                {
                    "hour": period["close"]["hour"],
                    "minute": period["close"]["minute"],
                    "day": period["close"]["date"]["day"],
                    "weekday": period["close"]["day"],
                    "timedelta": period["close"]["date"]["day"] + period["close"]["hour"] / 24 + period["close"]["minute"] / (24 * 60) - ctime
                }
                # ensure only positive timedeltas are captured (i.e. only closings in the future)
                for period in hours if (period["close"]["date"]["day"] + period["close"]["hour"] / 24 + period["close"]["minute"] / (24 * 60) - ctime) > 0
            ]
        except KeyError as e:
            return None
        closings.sort(key = lambda x: x["timedelta"])
        hour = closings[0]["hour"]
        minute = closings[0]["minute"]
        day = closings[0]["day"]
        match (day - today):
            case 0:
                weekday = "today"
            case 1:
                weekday = "tomorrow"
            case _:
                weekday = self.day_dict[closings[0]["weekday"]]
        return f"""{hour - 12 if hour > 12 else hour}:{minute:02d} {'PM' if hour // 12 == 1 else 'AM'} {weekday}"""
    
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
                "closes_at": self._find_next_closing(result.get("currentOpeningHours").get("periods")) if result.get("currentOpeningHours") else None,
                "lat": lat,
                "lon": lon
                })
        return parsed_results
    
    def search(self, lat: float, lon: float, type: Literal ["coffee_shop", "restaurant", "chick_fil_a"], radius : float = miles_to_m(1)):
        if type in ["coffee_shop", "restaurant"]:
            payload = {
                "includedPrimaryTypes": [type],
                "maxResultCount": 20,
                "rankPreference": "DISTANCE",
                "locationRestriction": {
                    "circle": {
                        "center": {
                            "latitude": lat,
                            "longitude": lon
                        },
                    "radius": radius
                    }
                }
            }
            url = f"{self.url}:searchNearby"
        elif type in ["chick_fil_a"]:
            payload = {
                "textQuery": "Chick-Fil-A",
                "includedType": "restaurant",
                "pageSize": 5,
                "strictTypeFiltering": True,
                "openNow": True,
                "rankPreference": "DISTANCE",
                "locationBias": {
                    "circle": {
                        "center": {
                            "latitude": lat,
                            "longitude": lon,
                        },
                        "radius": radius
                    }
                }
            }
            url = f"{self.url}:searchText"
        else:
            raise Exception(f"Unsupported type {type}")
        headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": self.api_key, # insert api key here
            "X-Goog-FieldMask": "places.displayName,places.formattedAddress,places.currentOpeningHours,places.websiteUri,places.location" # mask the data to return with the request here
        }
        response = requests.post(
            url,
            headers = headers,
            json = payload
        )
        if response.status_code != 200:
            raise Exception(f"Maps API returned status code {response.status_code}, full response {response.text}")
        response = response.json()
        parsed_response = self._parse_results(response.get("places", []), lat, lon)
        return (parsed_response, m_to_miles(radius))
    # searches with an expanding radius 
    def search_expand(self, lat: float, lon: float, type: Literal ["coffee_shop", "restaurant", "chick_fil_a"]):
        search_radii = [miles_to_m(2), miles_to_m(5), miles_to_m(10), miles_to_m(20)]
        for radius in search_radii:
            results = self.search(lat, lon, type, radius = radius)
            if len(results) >= 5:
                break
        return (results, m_to_miles(radius))