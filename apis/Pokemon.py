#/usr/bin/python
from API import *

class Pokemon(API):
	def __init__(self, test=False):
		self._categories = {
			"pokemons" : {
				"method" : self.__getPokemon,
				"questionTypes" : {
					"height" : self.__getPokemonHeight,
					"weight" : self.__getPokemonWeight,
					"number" : self.__getPokemonNumber
				}
			}
		}
		API.__init__(self, test=test)
	def __getPokemon(self):
		poke_id = random.randint(1,251)
		species = reqToDict(f'https://pokeapi.co/api/v2/pokemon-species/{poke_id}')
		stats = reqToDict(f'https://pokeapi.co/api/v2/pokemon/{poke_id}')
		if species == None or stats == None:
			return 0
		self._success = True
		for lang in species["names"]:
			if lang["language"]["name"] == "de":
				name = lang["name"]
		self._data = {
			"no" : poke_id, "name" : name, "height" : stats["height"]/10, "weight" : stats["weight"]/10
		}
	def __getPokemonHeight(self):
		self._question = f'Wie viel Meter (auf eine Nachkommastelle genau) ist das Pokémon {self._data["name"]} groß?'
		ans = self._data["height"]
		self._answer = {
			"value" : ans, "fmt" : "\d+([,\.]\d)?",
			"text" : f'{floatChic(ans)} m ist {self._data["name"]} groß.',
			"reaction" : "{} {} um {} m von dem richtigen Wert ab."
		}
	def __getPokemonWeight(self):
		self._question = f'Wie viel Kilogramm (auf eine Nachkommastelle genau) wiegt das Pokémon {self._data["name"]}?'
		ans = self._data["weight"]
		self._answer = {
			"value" : ans, "fmt" : "\d+([,\.]\d)?",
			"text" : f'{floatChic(ans)} kg wiegt {self._data["name"]}.',
			"reaction" : "{} {} um {} kg von dem richtigen Wert ab."
		}
	def __getPokemonNumber(self):
		self._question = f'Welche Nummer hat das Pokémon {self._data["name"]} im NationalDex?'
		ans = self._data["no"]
		self._answer = {
			"value" : ans, "fmt" : "\d+",
			"text" : f'{ans} ist die Nummer von {self._data["name"]}.',
			"reaction" : "{} {} um {} von der richtigen Nummer ab."
		}