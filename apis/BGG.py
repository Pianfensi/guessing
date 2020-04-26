#/usr/bin/python
from xml.etree import cElementTree as ElementTree

from API import *

class BGG(API):
	def __init__(self, test=False):
		self._categories = {
			"boardgames" : {
				"method" : self.__getBoardgame,
				"questionTypes" : {
					"published" : self.__getBoardgamePublished,
					"minPlayers" : self.__getBoardgameMinPlayers,
					"maxPlayers" : self.__getBoardgameMaxPlayers,
					"maxPlaytime" : self.__getBoardgameMaxPlaytime,
					"minAge" : self.__getBoardgameMinAge
				}
			}
		}
		API.__init__(self, test=test)
		self.__getBoardgame()
	def __getBoardgame(self):
		startid = random.randint(1,30000)
		params = {"id" : ",".join([str(x) for x in range(startid,startid+50)]), "type" : "boardgame"}
		r = requests.get("https://api.geekdo.com/xmlapi2/thing?" + urllib.parse.urlencode(params))
		try:
			root = ElementTree.XML(r.text)
			results = XmlListConfig(root)
			self._success = True
		except:
			return 0
		result = random.choice(results)
		title = None
		if isinstance(result["name"], list):
			for x in result["name"]:
				if x["type"] == "primary":
					title = x["value"]
		else:
			title = result["name"]["value"]
		self._data = {
			"title" : title, "minPlayers" : int(result["minplayers"]["value"]), "maxPlayers" : int(result["maxplayers"]["value"]),
			"minAge" : int(result["minage"]["value"]), "published" : int(result["yearpublished"]["value"]),
			"maxPlaytime" : int(result["maxplaytime"]["value"]), "website" : f'https://boardgamegeek.com/boardgame/{result["id"]}'
		}
		for k, v in self._data.items():
			if v == 0:
				self._data[k] = None
	def __getBoardgamePublished(self):
		self._question = f'In welchem Jahr erschien das Gesellschaftsspiel "{self._data["title"]}"?'
		ans = self._data["published"]
		self._answer = {
			"value" : ans, "fmt" : "\d{4}",
			"text" : f'{ans} erschien "{self._data["title"]}" {self._data["website"]}',
			"reaction" : "{} {} um {} Jahr/e vom richtigen Jahr ab."
		}
	def __getBoardgameMinPlayers(self):
		self._question = f'Wie viele Spielende werden mindestens für das Gesellschaftsspiel "{self._data["title"]}" benötigt?'
		ans = self._data["minPlayers"]
		self._answer = {
			"value" : ans, "fmt" : "\d+",
			"text" : f'{ans} ist das Minimum an Leuten für "{self._data["title"]}" {self._data["website"]}',
			"reaction" : "{} {} um {} vom richtigen Wert ab."
		}
	def __getBoardgameMaxPlayers(self):
		self._question = f'Wie viele Spielende können höchstens das Gesellschaftsspiel "{self._data["title"]}" spielen?'
		ans = self._data["maxPlayers"]
		self._answer = {
			"value" : ans, "fmt" : "\d+",
			"text" : f'{ans} ist das Maximum an Leuten für "{self._data["title"]}" {self._data["website"]}',
			"reaction" : "{} {} um {} vom richtigen Wert ab."
		}
	def __getBoardgameMinAge(self):
		self._question = f'Ab welchem Alter wird das Gesellschaftsspiel "{self._data["title"]}" empfohlen?'
		ans = self._data["minAge"]
		self._answer = {
			"value" : ans, "fmt" : "\d+",
			"text" : f'{ans} ist das Mindestalter für "{self._data["title"]}" {self._data["website"]}',
			"reaction" : "{} {} um {} vom richtigen Wert ab."
		}
	def __getBoardgameMaxPlaytime(self):
		self._question = f'Wie viele Minuten werden für das Gesellschaftsspiel "{self._data["title"]}" vom Hersteller als Höchstdauer angegeben?'
		ans = self._data["maxPlaytime"]
		self._answer = {
			"value" : ans, "fmt" : "\d+",
			"text" : f'{ans} Minuten ist die Höchstdauer für "{self._data["title"]}" {self._data["website"]}',
			"reaction" : "{} {} um {} Minute/n vom richtigen Wert ab."
		}
b = BGG(True)
b.generate()