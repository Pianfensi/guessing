#/usr/bin/python
from API import *

class Worldbank(API):
	def __init__(self):
		self._categories = {
			"population" : {
				"method" : self.__getPopulation,
				"questionTypes" : {
					"country" : self.__getPopulationNational
				}
			}
		}
		API.__init__(self)
	def __getPopulation(self):
		year = random.randint(1960, time.localtime(time.time())[0]-2)
		url = 'https://api.worldbank.org/v2/de/country/all/indicator/SP.POP.TOTL?'
		params = {"date" : year, "format" : "json", "per_page" : 270}
		data = reqToDict(url, params=params)
		if data == None:
			return 0
		self._success = True
		country_data = {}
		for c in data[1]:
			if c["country"]["id"] in countries:
				country_data[c["country"]["id"]] = c["value"]
		country = randomKey(country_data)
		self._data = {
			"year" : year, "country" : countries[country][0], "population" : country_data[country]
		}
	def __getPopulationNational(self):
		self._question = f'Wie hoch ist die Bevölkerung in {self._data["country"]} {self._data["year"]} gewesen?'
		ans = self._data["population"]
		self._answer = {
			'value' : ans, 'fmt' : "\d+",
			'text' : f'{numWithSeps(ans)} EinwohnerInnen hatte {self._data["country"]}.',
			'reaction' : '{} {} um {} vom richtigen Wert ab.'
		}