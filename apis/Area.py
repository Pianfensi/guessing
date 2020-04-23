#/usr/bin/python
from API import *

class Area(API):
	def __init__(self, test=False):
		self._categories = {
			"areas" : {
				"method" : self.__getArea,
				"questionTypes" : {
					"countries" : self.__getAreaOfCountry
				}
			}
		}
		API.__init__(self, test=test)
	def __getArea(self):
		self._data = countries[randomKey(countries)]
		self._success = True
	def __getAreaOfCountry(self):
		self._question = f'Wie groß ist {self._data[0]} in km²?'
		ans = self._data[1]
		self._answer = {
			'value' : ans, 'fmt' : "\d+",
			'text' : f'{ans:n} km² ist {self._data[0]} groß.',
			'reaction' : '{} {} um {} km² vom richtigen Wert ab.'
		}