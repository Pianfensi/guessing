#/usr/bin/python
from API import *

class Steam(API):
	def __init__(self, test=False):
		self._categories = {
			"games" : {
				"method" : self.__getGame,
				"questionTypes" : {
					"achievements" : self.__getGameAchievements,
					"reviews" : self.__getGameReviews,
					"dlcs" : self.__getGameDLCs,
					"price" : self.__getGamePrice,
					"metacritic" : self.__getGameMetacritic,
					"release" : self.__getGameRelease
				}
			},
			"achievements" : {
				"method" : self.__getAchievement,
				"questionTypes" : {
					"least" : self.__getLeastAchievement,
					"most" : self.__getMostAchievement,
					"random" : self.__getRandomAchievement,
					"completion" : self.__getAchievementCompletion
				}
			}
		}
		API.__init__(self, test=test)
	def __getGame(self):
		params = {"key" : STEAMAPI, "format" : "json", "count" : 5}
		url = "https://store.steampowered.com/api/appdetails/?"
		while True:
			app = random.choice(steam_apps)
			params["appids"] = app["appid"]
			rjson = reqToDict(url, params)
			if rjson[str(params["appids"])]["success"]:
				app_dict = rjson[str(params["appids"])]["data"]
				if "Demo" not in app_dict["name"]: # ignore Demos
					break
			else:
				return 0
		self._success = True
		self._data = {
			"name" : app_dict["name"], "id" : app["appid"], "displayName" : app_dict["name"],
			"achievements" : None, "reviews" : None, "release" : None,
			"price" : None, "metacritic" : None, "dlcs" : None
		}
		if "fullgame" in app_dict:
			self._data["name"] = f'{self._data["name"]} (DLC)'
		if "developers" in app_dict:
			self._data["displayName"] = f'{self._data["name"]}" vom Entwickler "{app_dict["developers"][0]}'
		any_info = False
		if "achievements" in app_dict and app_dict["achievements"]["total"] > 0:
			self._data["achievements"] = app_dict["achievements"]["total"]
			any_info = True
		if "release_date" in app_dict and not app_dict["release_date"]["coming_soon"]:
			self._data["release"] = steamymd(app_dict["release_date"]["date"])
			any_info = True
		if "price_overview" in app_dict:
			self._data["price"] = app_dict["price_overview"]["final"]/100 # current price
			any_info = True
		if "metacritic" in app_dict:
			self._data["metacritic"] = app_dict["metacritic"]["score"]
			any_info = True
		if "recommendations" in app_dict:
			self._data["reviews"] = app_dict["recommendations"]["total"]
			any_info = True
		if "dlc" in app_dict:
			self._data["dlcs"] = len(app_dict["dlc"])
			any_info = True
		if not any_info:
			self._success = False
	def __getGameAchievements(self):
		self._question = f'Wie viele Steam-Errungenschaften hat "{self._data["displayName"]}"?'
		ans = self._data["achievements"]
		self._answer = {
			'value' : ans, 'fmt' : "\d+",
			'text' : f'{ans} Errungenschaft{"" if ans == 1 else "en"} hat "{self._data["name"]}" (https://store.steampowered.com/app/{self._data["id"]}).',
			'reaction' : '{} {} um {} vom richtigen Wert ab.'
		}
	def __getGameReviews(self):
		self._question = f'Wie viele Reviews besitzt "{self._data["displayName"]}" auf Steam?'
		ans = self._data["reviews"]
		self._answer = {
			'value' : ans, 'fmt' : "\d+",
			'text' : f'{ans} Review{"" if ans == 1 else "s"} besitzt "{self._data["name"]}" (https://store.steampowered.com/app/{self._data["id"]}).',
			'reaction' : '{} {} um {} vom richtigen Wert ab.'
		}
	def __getGameDLCs(self):
		self._question = f'Wie viele DLCs hat das Spiel "{self._data["displayName"]}" auf Steam?'
		ans = self._data["dlcs"]
		self._answer = {
			'value' : ans, 'fmt' : "\d+",
			'text' : f'{ans} DLC{"" if ans == 1 else "s"} besitzt "{self._data["name"]}" (https://store.steampowered.com/app/{self._data["id"]}).',
			'reaction' : '{} {} um {} vom richtigen Wert ab.'
		}
	def __getGamePrice(self):
		self._question = f'Wie viel Euro (auf den Cent genau) kostet aktuell "{self._data["displayName"]}" auf Steam?'
		ans = self._data["price"]
		self._answer = {
			'value' : ans, 'fmt' : "\d+[,\.]\d\d",
			'text' : f'{floatChic(ans)} kostet "{self._data["name"]}" (https://store.steampowered.com/app/{self._data["id"]}).',
			'reaction' : '{} {} um {} € vom richtigen Wert ab.'
		}
	def __getGameMetacritic(self):
		self._question = f'Welchen Metascore hat das Spiel "{self._data["displayName"]}"?'
		ans = self._data["metacritic"]
		self._answer = {
			'value' : ans, 'fmt' : "(0|[1-9]\d|100)",
			'text' : f'{ans} ist der Metascore von "{self._data["name"]}" (https://store.steampowered.com/app/{self._data["id"]}).',
			'reaction' : '{} {} um {} vom richtigen Wert ab.'
		}
	def __getGameRelease(self):
		self._question = f'An welchem Tag (TT.MM.JJJJ) erschien "{self._data["displayName"]}" auf Steam?'
		ans = dmy(self._data["release"])
		self._answer = {
			'value' : ans, 'fmt' : "\d\d\.\d\d\.\d\d\d\d",
			'text' : f'Am {ans} erschien "{self._data["name"]}" (https://store.steampowered.com/app/{self._data["id"]}).',
			'reaction' : '{} {} um {} Tag/e vom richtigen Datum ab.'
		}
	def __getAchievement(self):
		self._success = False
		params = {"key" : STEAMAPI, "format" : "json", "count" : 5, "l" : "german"}
		url_progress_achievements = 'https://api.steampowered.com/ISteamUserStats/GetGlobalAchievementPercentagesForApp/v0002/?'
		url_game_achievements = 'https://api.steampowered.com/ISteamUserStats/GetSchemaForGame/v2/?'
		while True:
			app = random.choice(steam_apps)
			params["gameid"] = app["appid"]
			achievement_progresses = reqToDict('https://api.steampowered.com/ISteamUserStats/GetGlobalAchievementPercentagesForApp/v0002/?', params)
			if achievement_progresses != None and "achievementpercentages" in achievement_progresses:
				break
		params["appid"] = app["appid"]
		achievement_datas = reqToDict('https://api.steampowered.com/ISteamUserStats/GetSchemaForGame/v2/?', params)
		if achievement_datas == None:
			return 0
		achievement_progresses = achievement_progresses["achievementpercentages"]["achievements"]
		game_name = achievement_datas["game"]["gameName"]
		achievement_datas = achievement_datas["game"]["availableGameStats"]["achievements"]
		self._success = True
		achievements = {}
		total_progress = 0
		max_percent, min_percent = -1, 101
		max_achievement, min_achievement = None, None
		for a in achievement_progresses:
			achievements[a["name"]] = {"percent" : a["percent"]}
			total_progress += a["percent"]
			if a["percent"] < min_percent:
				min_percent = a["percent"]
				min_achievement = a["name"]
			if a["percent"] > max_percent:
				max_percent = a["percent"]
				max_achievement = a["name"]
		for a in achievement_datas:
			if "description" in a:
				achievements[a["name"]]["name"] = f'{a["displayName"]} - {a["description"]}'
			else:
				achievements[a["name"]]["name"] = a["displayName"]
		total_completion = total_progress/len(achievements)
		rnd_achievement = randomKey(achievements)
		self._data = {
			"leastName" : achievements[min_achievement]["name"], "leastProgress" : round(min_percent),
			"mostName" : achievements[max_achievement]["name"], "mostProgress" : round(max_percent),
			"completion" : round(total_completion), "game" : game_name,
			"rndName" : achievements[rnd_achievement]["name"], "rndProgress" : round(achievements[rnd_achievement]["percent"])
		}
		self._answer = {
			"fmt" : "(0|[1-9]\d|100)",
			"reaction" : "{} {} um {} Prozentpunkt/e vom richtigen Wert ab."
		}
	def __getLeastAchievement(self):
		self._question = f'Wie viel Prozent (gerundet) der Spielenden von "{self._data["game"]}" haben die am seltesten erreichte Errungenschaft "{self._data["leastName"]}" im Spiel?'
		ans = round(self._data["leastProgress"])
		self._answer["text"] = f'{ans} % erreichten die Errungenschaft.'
		self._answer["value"] = ans
	def __getMostAchievement(self):
		self._question = f'Wie viel Prozent (gerundet) der Spielenden von "{self._data["game"]}" haben die am öftesten erreichte Errungenschaft "{self._data["mostName"]}" im Spiel?'
		ans = round(self._data["mostProgress"])
		self._answer["text"] = f'{ans} % erreichten die Errungenschaft.'
		self._answer["value"] = ans
	def __getRandomAchievement(self):
		self._question = f'Wie viel Prozent (gerundet) der Spielenden von "{self._data["game"]}" haben die Steam-Errungenschaft "{self._data["rndName"]}"?'
		ans = round(self._data["rndProgress"])
		self._answer["text"] = f'{ans} % erreichten "{self._data["rndName"]}".'
		self._answer["value"] = ans
	def __getAchievementCompletion(self):
		self._question = f'Wie hoch ist die durchschnittliche Komplettierungsquote (in Prozent, gerundet) der Errungenschaften von "{self._data["game"]}" wurden im Durchschnitt erreicht?'
		ans = round(self._data["completion"])
		self._answer["text"] = f'{ans} % aller Errungenschaften von "{self._data["game"]}" wurden erreicht.'
		self._answer["value"] = ans