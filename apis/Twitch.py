#/usr/bin/python
from API import *

class Twitch(API):
	def __init__(self, test=False):
		self.__headers = {
			'Client-ID' : TWITCHID,
			'Authorization' : 'OAuth %s' % TWITCHAUTH,
			'Accept' : 'application/vnd.twitchtv.v5+json'
		}
		self._categories = {
			"games" : {
				"method" : self.__getGame,
				"questionTypes" : {
					"channels" : self.__getChannelsWithGame,
					"viewers" : self.__getGameViewers
				}
			},
			"streams" : {
				"method" : self.__getStreams,
				"questionTypes" : {
					"language" : self.__getStreamsWithLanguage,
					"adult" : self.__getStreamsWithAdults,
					"created" : self.__getCreatedOfStream,
					"followers" : self.__getStreamFollowers,
					"livetime" : self.__getStreamLivetime,
					"views" : self.__getStreamViews,
					"viewers" : self.__getStreamViewers
				}
			}
		}	
		API.__init__(self, test=test)
	# Games
	def __getGame(self):
		url = "https://api.twitch.tv/kraken/games/top?"
		params = {"limit" : 100}
		top_games = reqToDict(url, params=params, headers=self.__headers)
		if top_games == None or "top" not in top_games: # successful
			return 0	
		self._success = True
		game = random.choice(top_games["top"])
		self._data = {
			"name" : game["game"]["name"], "channels" : game["channels"],
			"viewers" : game["viewers"]
		}
	def __getChannelsWithGame(self):
		self._question = f'Wie viele imGlitch Streamer spielen aktuell "{self._data["name"]}"?'
		ans = int(self._data["channels"])
		self._answer = {
			'value' : ans, 'fmt' : "\d+",
			'text' : f'{numWithSeps(ans)} Streamer spielen "{self._data["name"]}".',
			'reaction' : '{} {} um {} vom richtigen Wert ab.'
		}
	def __getGameViewers(self):
		self._question = f'Wie viele Zuschauende gucken aktuell {self._data["name"]}?'
		ans = int(self._data["viewers"])
		self._answer = {
			'value' : ans, 'fmt' : "\d+",
			'text' : f'{numWithSeps(ans)} Person{"en" if ans > 1 else ""} schauen "{self._data["name"]}".',
			'reaction' : '{} {} um {} vom richtigen Wert ab.'
		}
	# Streams
	def __getStreams(self):
		streams = []
		for i in range(5):
			rjson = reqToDict("https://api.twitch.tv/kraken/streams/?", {"limit" : 100, "offset" : i}, headers=self.__headers)
			if rjson == None or "streams" not in rjson:
				return 0
			streams += rjson["streams"]
		self._success = True
		stream = random.choice(streams)
		self._data = {
			"name" : stream["channel"]["display_name"], "created" : int(stream["channel"]["created_at"][:4]),
			"followers" : int(stream["channel"]["followers"]), "views" : int(stream["channel"]["views"]),
			"start" : strtotime(stream["created_at"]), "viewers" : int(stream["viewers"]),
			"game" : stream["channel"]["game"], "user" : stream["channel"]["name"],
		}
		self.__metadata = {
			"language" : {}, "adultContent" : [x["channel"]["mature"] for x in streams].count(True)//5
		}
		for lang in langs:
			self.__metadata["language"][lang] = [x["channel"]["broadcaster_language"][:2] for x in streams].count(lang)
	def __getStreamsWithLanguage(self):
		lang = randomKey(self.__metadata["language"])
		self._question = f'Wie viele der 🔴 Top-500-Twitch-Streamer streamen auf {langs[lang]}?'
		ans = self.__metadata["language"][lang]
		self._answer = {
			'value' : ans, 'fmt' : "\d+",
			'text' : f'{ans} streamen auf {langs[lang]}.',
			'reaction' : '{} {} um {} vom richtigen Wert ab.'
		}
	def __getStreamsWithAdults(self):
		self._question = 'Wie viel Prozent der 🔴 Top-500-Twitch-Streamer streamen Erwachseneninhalte?'
		ans = self.__metadata["adultContent"]
		self._answer = {
			'value' : ans, 'fmt' : "\d+",
			'text' : f'{ans} streamen 18+.',
			'reaction' : '{} {} um {} Prozentpunkt/e vom richtigen Wert ab.'
		}		
	def __getCreatedOfStream(self):
		self._question = f'In welchem Jahr wurde der imGlitch Kanal {self._data["name"]} erstellt?'
		ans = self._data["created"]
		self._answer = {
			'value' : ans, 'fmt' : "\d+",
			'text' : f'{ans} wurde https://twitch.tv/{self._data["user"]} erstellt.',
			'reaction' : '{} {} um {} Jahr/e vom richtigen Wert ab.'
		}
	def __getStreamFollowers(self):
		self._question = f'Wie viele Follower hat der imGlitch Kanal {self._data["name"]} mit aktuell {numWithSeps(self._data["viewers"])} Zuschauenden?'
		ans = self._data["followers"]
		self._answer = {
			'value' : ans, 'fmt' : "\d+",
			'text' : f'{numWithSeps(ans)} folgen https://twitch.tv/{self._data["user"]}',
			'reaction' : '{} {} um {} vom richtigen Wert ab.'
		}		
	def __getStreamLivetime(self):
		self._question = f'Wie viele Minuten ist der imGlitch Stream von {self._data["name"]} bereits live 🔴?'
		ans = int(time.time()-self._data["start"])//60
		self._answer = {
			'value' : ans, 'fmt' : "\d+",
			'text' : f'{numWithSeps(ans)} Minut{"en" if ans > 1 else ""} streamt https://twitch.tv/{self._data["user"]} schon.',
			'reaction' : '{} {} um {} Minute/n vom richtigen Wert ab.'
		}
	def __getStreamViews(self):
		self._question = f'Wie viele Aufrufe hat der imGlitch Kanal von {self._data["name"]}?'
		ans = self._data["views"]
		self._answer = {
			'value' : ans, 'fmt' : "\d+",
			'text' : f'{numWithSeps(ans)} Aufrufe hat der Kanal https://twitch.tv/{self._data["user"]}',
			'reaction' : '{} {} um {} vom richtigen Wert ab.'
		}
	def __getStreamViewers(self):
		self._question = f'Wie viele ZuschauerInnen hat der imGlitch Kanal {self._data["name"]} beim Streamen von "{self._data["game"]}"?'
		ans = self._data["viewers"]
		self._answer = {
			'value' : ans, 'fmt' : "\d+",
			'text' : f'{numWithSeps(ans)} Person{"" if ans == 1 else "en"} schauen https://twitch.tv/{self._data["user"]}',
			'reaction' : '{} {} um {} vom richtigen Wert ab.'
		}