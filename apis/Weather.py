#/usr/bin/python
from API import *

class Weather(API):
	def __init__(self):
		self._categories = {
			"weather" : {
				"method" : self.__getWeather,
				"questionTypes" : {
					"temp" : self.__getTemperature,
					"windspeed" : self.__getWindSpeed,
					"sunrise" : self.__getSunrise,
					"sunset" : self.__getSunset
				}
			}
		}
		API.__init__(self)
	def __getWeather(self):
		random_city = random.choice(cities)
		city_id = random_city["id"]
		url = "https://api.openweathermap.org/data/2.5/weather?"
		params = {"id" : city_id, "units" : "metric", "lang" : "de", "appid" : OPENWEATHERKEY}
		city_data = reqToDict(url, params=params)
		if city_data == None:
			return 0
		self._success = True
		self._data = {
			"name" : city_data["name"], "country" : countries[city_data["sys"]["country"]][0],
			"sunrise" : city_data["sys"]["sunrise"]+city_data["timezone"]-7200, "sunset" : city_data["sys"]["sunset"]+city_data["timezone"]-7200,
			"temp" : city_data["main"]["temp"], "windspeed" : city_data["wind"]["speed"]	
		}
	def __getTemperature(self):
		self._question = f'Wie viel Grad Celsius (gerundet) sind es aktuell in {self._data["name"]}, {self._data["country"]}?'
		ans = round(self._data["temp"])
		self._answer = {
			'value' : ans, 'fmt' : "-?\d+",
			'text' : f'{ans} °C sind es aktuell in {self._data["name"]}.',
			'reaction' : '{} {} um {} °C vom richtigen Wert ab.'
		}
	def __getWindSpeed(self):
		self._question = f'Wie schnell bläst der Wind (m/s) in {self._data["name"]}, {self._data["country"]}?'
		ans = round(self._data["windspeed"])
		self._answer = {
			'value' : ans, 'fmt' : "\d+",
			'text' : f'Mit {ans} m/s fegt der Wind aktuell in {self._data["name"]}.',
			'reaction' : '{} {} um {} vom richtigen Wert ab.'
		}
	def __getSunrise(self):
		past = False
		if self._data["sunrise"] < time.time():
			past = True
		self._question = "Wann ([H]H:MM, 24h, Ortszeit) %s die Sonne heute in %s, %s auf?" % (
			"ging" if past else "geht", self._data["name"], self._data["country"])
		timetuple = time.localtime(self._data["sunrise"])
		ans = "%02d:%02d" % (timetuple[3], timetuple[4])
		self._answer = {
			'value' : ans, 'fmt' : "(\d|[01]\d|2[0-3]):[0-5]\d",
			'text' : f'Um {ans} {"ging" if past else "geht"} die Sonne auf. 🌞',
			'reaction' : '{} {} um {} Minute/n vom richtigen Wert ab.'
		}
	def __getSunset(self):
		past = False
		if self._data["sunset"] < time.time():
			past = True
		self._question = "Wann ([H]H:MM, 24h, Ortzeit) %s die Sonne heute in %s, %s unter?" % (
			"ging" if past else "geht", self._data["name"], self._data["country"])
		timetuple = time.localtime(self._data["sunset"])
		ans = "%02d:%02d" % (timetuple[3], timetuple[4])
		self._answer = {
			'value' : ans, 'fmt' : "(\d|[01]\d|2[0-3]):[0-5]\d",
			'text' : f'Um {ans} {"ging" if past else "geht"} die Sonne unter. 🌇',
			'reaction' : '{} {} um {} Minute/n vom richtigen Wert ab.'
		}