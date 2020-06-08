# /usr/bin/python
from math import *

from API import *

RADIUS = 6371  # km


def hav(phi: float):
    """ haversine function """
    return sin(phi / 2) ** 2


def earth_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """ calculates the beeline distance between to given points on the Earth in km """
    lat1 = radians(lat1)
    lon1 = radians(lon1)
    lat2 = radians(lat2)
    lon2 = radians(lon2)
    delta_lat = lat1 - lat2
    delta_lon = lon1 - lon2
    return 2 * RADIUS * asin(sqrt(hav(delta_lat) + cos(lat1) * cos(lat2) * hav(delta_lon)))


class Distance(API):
    def __init__(self):
        self._categories = {
            "routes": {
                "method": self._get_route,
                "questionTypes": {
                    "beeline": self._get_route_beeline,
                    "distance": self._get_route_distance,
                    "duration": self._get_route_duration
                }
            }
        }
        API.__init__(self)

    def _get_route(self):
        city1, city2 = random.choices(cities, k=2)
        self._available_modes = {"driving": "mit dem Auto", "walking": "zu Fuß", "bicycling": "mit dem Rad"}
        travel_mode = get_random_key(self._available_modes)
        url = "https://maps.googleapis.com/maps/api/distancematrix/json?"
        params = {"units": "metric", "language": "de", "key": GOOGLEKEY, "mode": travel_mode,
                  "origins": f'{city1["name"]},{city1["country"]}',
                  "destinations": f'{city2["name"]},{city2["country"]}'}
        result = get_dict_from_request(url, params=params)
        self._success = True
        self._data = {
            "start": f'{city1["name"]}, {countries[city1["country"]][0]}',
            "end": f'{city2["name"]}, {countries[city2["country"]][0]}',
            "beeline": earth_distance(
                city1["coord"]["lat"], city1["coord"]["lon"],
                city2["coord"]["lat"], city2["coord"]["lon"]),
            "travelMode": travel_mode,
            "distance": None, "duration": None,
            "website": f'https://www.google.com/maps/dir/{urllib.parse.quote_plus(params["origins"])}/{urllib.parse.quote_plus(params["destinations"])}'
        }
        if result["rows"][0]["elements"][0]["status"] == "OK":
            self._data["distance"] = result["rows"][0]["elements"][0]["distance"]["value"]
            self._data["duration"] = result["rows"][0]["elements"][0]["duration"]["value"]

    def _get_route_beeline(self):
        self._question = f'Wie viele Kilometer liegen {self._data["start"]} und {self._data["end"]} Luftlinie auseinander?'
        ans = int(self._data["beeline"])
        self._answer = {
            "value": ans, "fmt": "\d+",
            "text": f'{seperate_in_thousands(ans)} km liegen {self._data["start"]} und {self._data["end"]} auseinander.',
            "reaction": "{} {} um {} km vom richtigen Wert ab."
        }

    def _get_route_distance(self):
        self._question = f'Wie viele Kilometer muss man {self._available_modes[self._data["travelMode"]]} von {self._data["start"]} nach {self._data["end"]} laut Google Maps zurücklegen?'
        ans = round(self._data["distance"] / 1000)
        self._answer = {
            "value": ans, "fmt": "\d+",
            "text": f'{seperate_in_thousands(ans)} km legt man zurück {self._data["website"]}',
            "reaction": "{} {} um {} km vom richtigen Wert ab."
        }

    def _get_route_duration(self):
        days = round(self._data["duration"] / (24 * 3600))
        hours = round(self._data["duration"] / 3600)
        minutes = round(self._data["duration"] / 60)
        if hours > 99:
            unit = "Tage"
            ans = days
        elif hours < 3:
            unit = "Minuten"
            ans = minutes
        else:
            unit = "Stunden"
            ans = hours
        self._question = f'Wie viele {unit} braucht man laut Google Maps {self._available_modes[self._data["travelMode"]]} von {self._data["start"]} nach {self._data["end"]}?'
        self._answer = {
            "value": ans, "fmt": "\d+",
            "text": f'{ans} {unit} braucht man {self._data["website"]}',
            "reaction": "{} {} um {} " + unit[:-1] + '/' + unit[-1] + " vom richtigen Wert ab."
        }
