#/usr/bin/python
import math

from API import *

class Distance(API):
	def __init__(self):
		self._categories = {
			"routes" : {
				"method" : self.__getRoute,
				"questionTypes" : {
					"beeline" : self.__getRouteBeeline,
					"distance" : self.__getRouteDistance,
					"duration" : self.__getRouteDuration
				}
			}
		}
		API.__init__(self)
	def __getRoute(self):
		city1, city2 = random.choices(cities, k=2)
		self.__available_modes = {"driving" : "mit dem Auto", "walking" : "zu Fuß", "bicycling" : "mit dem Rad"}
		travel_mode = randomKey(self.__available_modes)
		url = "https://maps.googleapis.com/maps/api/distancematrix/json?"
		params = {"units" : "metric", "language" : "de", "key" : GOOGLEKEY, "mode" : travel_mode,
			"origins" : f'{city1["name"]},{city1["country"]}',
			"destinations" : f'{city2["name"]},{city2["country"]}'}
		result = reqToDict(url, params=params)
		self._success = True
		self._data = {
			"start" : f'{city1["name"]}, {countries[city1["country"]][0]}',
			"end" : f'{city2["name"]}, {countries[city2["country"]][0]}',
			"beeline" : earthDistance(
				city1["coord"]["lat"], city1["coord"]["lon"],
				city2["coord"]["lat"], city2["coord"]["lon"]),
			"travelMode" : travel_mode,
			"distance" : None, "duration" : None,
			"website" : f'https://www.google.com/maps/dir/{urllib.parse.quote_plus(params["origins"])}/{urllib.parse.quote_plus(params["destinations"])}'
		}
		if result["rows"][0]["elements"][0]["status"] == "OK":
			self._data["distance"] = result["rows"][0]["elements"][0]["distance"]["value"]
			self._data["duration"] = result["rows"][0]["elements"][0]["duration"]["value"]
	def __getRouteBeeline(self):
		self._question = f'Wie viele Kilometer liegen {self._data["start"]} und {self._data["end"]} Luftlinie auseinander?'
		ans = int(self._data["beeline"])
		self._answer = {
			"value" : ans, "fmt" : "\d+",
			"text" : f'{numWithSeps(ans)} km liegen {self._data["start"]} und {self._data["end"]} auseinander.',
			"reaction" : "{} {} um {} km vom richtigen Wert ab."
		}
	def __getRouteDistance(self):
		self._question = f'Wie viele Kilometer muss man {self.__available_modes[self._data["travelMode"]]} von {self._data["start"]} nach {self._data["end"]} laut Google Maps zurücklegen?'
		ans = round(self._data["distance"]/1000)
		self._answer = {
			"value" : ans, "fmt" : "\d+",
			"text" : f'{numWithSeps(ans)} km legt man zurück {self._data["website"]}',
			"reaction" : "{} {} um {} km vom richtigen Wert ab."
		}
	def __getRouteDuration(self):
		days = round(self._data["duration"]/(24*3600))
		hours = round(self._data["duration"]/3600)
		minutes = round(self._data["duration"]/60)
		if hours > 99:
			unit = "Tage"
			ans = days
		elif hours < 3:
			unit = "Minuten"
			ans = minutes
		else:
			unit = "Stunden"
			ans = hours
		self._question = f'Wie viele {unit} braucht man laut Google Maps {self.__available_modes[self._data["travelMode"]]} von {self._data["start"]} nach {self._data["end"]}?'
		self._answer = {
			"value" : ans, "fmt" : "\d+",
			"text" : f'{ans} {unit} braucht man {self._data["website"]}',
			"reaction" : "{} {} um {} " + unit[:-1] + '/' + unit[-1] + " vom richtigen Wert ab."
		}