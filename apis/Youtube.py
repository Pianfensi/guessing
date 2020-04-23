#/usr/bin/python
from API import *

class Youtube(API):
	def __init__(self, test=False):
		self._categories = {
			"channels" : {
				"method" : self.__getChannel,
				"questionTypes" : {
					"created" : self.__getCreatedOfChannel,
					"subs" : self.__getChannelSubs,
					"videos" : self.__getChannelVideos,
					"views" : self.__getChannelViews
				}
			},
			"videos" : {
				"method" : self.__getVideo,
				"questionTypes" : {
					"age" : self.__getVideoAge,
					"duration" : self.__getVideoDuration,
					"comments" : self.__getVideoComments,
					"dislikes" : self.__getVideoDislikes,
					"likes" : self.__getVideoLikes,
					"views" : self.__getVideoViews
				}
			}
		}
		API.__init__(self, test=test)
	def __getChannel(self):
		url = "https://www.googleapis.com/youtube/v3/search?"
		params = {
			"channelType" :"any", "maxResults" : 50,
			"order" : "relevance", "regionCode" : "de",
			"safeSearch" : "none", "type" : "channel",
			"part" : "snippet", "key" : YOUTUBEKEY, 
			"publishedBefore" : timetostr(random.randint(strtotime("2016-01-01T00:00:00Z"), int(time.time())))}
		results = reqToDict(url, params=params)
		if results == None or "items" not in results:
			return 0
		channel = random.choice(results["items"])
		channel_id = channel["id"]["channelId"]
		channel_api = "https://www.googleapis.com/youtube/v3/channels?"
		channel_params = {"id" : channel_id, "part" : "snippet,statistics,id", "key" : YOUTUBEKEY}
		stats = reqToDict(channel_api, params = channel_params)
		if stats == None or "items" not in stats:
			return 0
		self._success = True
		channel_stats = stats["items"][0]
		self._data = {
			"id" : channel_id,
			"name" : channel_stats["snippet"]["localized"]["title"], "country" : None,
			"published" : int(channel_stats["snippet"]["publishedAt"][:4]), "subs" : int(channel_stats["statistics"]["subscriberCount"]),
			"videos" : int(channel_stats["statistics"]["videoCount"]), "views" : int(channel_stats["statistics"]["viewCount"])
		}
		self._data["longName"] = self._data["name"]
		if "country" in channel_stats["snippet"]:
			self._data["country"] = countries[channel_stats["snippet"]["country"]][0]
			self._data["longName"] = f'{self._data["name"]} ({self._data["country"]})'
	def __getCreatedOfChannel(self):
		self._question = f'In welchem Jahr wurde der YouTube-Kanal {self._data["longName"]} mit {self._data["videos"]:n} Video{"" if self._data["videos"] == 1 else "s"} erstellt?'
		ans = self._data["published"]
		self._answer = {
			'value' : ans, 'fmt' : "\d+",
			'text' : f'{ans} wurde {self._data["name"]} https://www.youtube.com/channel/{self._data["id"]} erstellt.',
			'reaction' : '{} {} um {} Jahr/e vom richtigen Wert ab.'
		}
	def __getChannelSubs(self):
		self._question = f'Wie viele Abonnenten hat der YouTube-Kanal {self._data["longName"]} aus dem Jahr {self._data["published"]}?'
		ans = self._data["subs"]
		self._answer = {
			'value' : ans, 'fmt' : "\d+",
			'text' : f'{numWithSeps(ans)} Abonnenten hat {self._data["name"]} https://www.youtube.com/channel/{self._data["id"]}',
			'reaction' : '{} {} um {} vom richtigen Wert ab.'
		}
	def __getChannelVideos(self):
		self._question = f'Wie viele Videos hat der YouTube-Kanal {self._data["longName"]} mit {self._data["subs"]:n} Abonnenten?'
		ans = self._data["videos"]
		self._answer = {
			'value' : ans, 'fmt' : "\d+",
			'text' : f'{numWithSeps(ans)} Video{"" if ans == 1 else "s"} hat {self._data["name"]} https://www.youtube.com/channel/{self._data["id"]}',
			'reaction' : '{} {} um {} vom richtigen Wert ab.'
		}
	def __getChannelViews(self):
		self._question = f'Wie viele Videoaufrufe hat der YouTube-Kanal {self._data["longName"]} mit {self._data["videos"]} Videos?'
		ans = self._data["views"]
		self._answer = {
			'value' : ans, 'fmt' : "\d+",
			'text' : f'{numWithSeps(ans)} Videoaufrufe hat {self._data["name"]} https://www.youtube.com/channel/{self._data["id"]}',
			'reaction' : '{} {} um {} vom richtigen Wert ab.'
		}			
	def __getVideo(self):
		url = "https://www.googleapis.com/youtube/v3/search?"
		params = {"maxResults" : 50, "order" : "relevance",
			"regionCode" : "de", "safeSearch" : "none",
			"type" : "video", "part" : "snippet", "key" : YOUTUBEKEY, 
			"publishedBefore" : timetostr(random.randint(strtotime("2016-01-01T00:00:00Z"), int(time.time())))}
		results = reqToDict(url, params=params)
		if results == None or "items" not in results:
			return 0
		video = random.choice(results["items"])
		video_id = video["id"]["videoId"]
		video_api = "https://www.googleapis.com/youtube/v3/videos?"
		video_params = {"id" : video_id, "part" : "contentDetails,snippet,statistics,id", "key" : YTKEY}
		stats = reqToDict(video_api, params=video_params)
		if stats == None or "items" not in stats:
			return 0
		self._success = True
		video_stats = stats["items"][0]
		self._data = {
			"id" : video_id,
			"title" : f'"{video_stats["snippet"]["localized"]["title"]}"',
			"channelname" : video_stats["snippet"]["channelTitle"],
			"age" : ageindays(video_stats["snippet"]["publishedAt"]),
			"comments" : None, "dislikes" : None, "likes" : None, "views" : None,
			"duration" : yttosec(video_stats["contentDetails"]["duration"]),
			"published" : dmy(video_stats["snippet"]["publishedAt"])
		}
		for stat in ["comment", "dislike", "like", "view"]:
			if f'{stat}Count' in video_stats["statistics"]:
				self._data[f'{stat}s'] = int(video_stats["statistics"][f'{stat}Count'])
	def __getVideoAge(self):
		self._question = f'Wie viele Tage ist das Video {self._data["title"]} vom Kanal {self._data["channelname"]} bereits online?'
		ans = self._data["age"]
		self._answer = {
			'value' : ans, 'fmt' : "\d+",
			'text' : f'{numWithSeps(ans)} ist Tag{"" if ans == 1 else "e"} https://youtu.be/{self._data["id"]} online.',
			'reaction' : '{} {} um {} Tag/e vom richtigen Wert ab.'
		}
	def __getVideoDuration(self):
		self._question = f'Wie lange ([M]M:SS) dauert das Video {self._data["title"]} vom Kanal {self._data["channelname"]}?'
		duration = self._data["duration"]
		ans = f'{duration//60:02}:{duration%60:02}'
		self._answer = {
			'value' : ans, 'fmt' : "\d{1,2}:[0-5]\d",
			'text' : f'{ans} dauert https://youtu.be/{self._data["id"]}',
			'reaction' : '{} {} um {} Sekunde/n vom richtigen Wert ab.'
		}
	def __getVideoComments(self):
		self._question = f'Wie viele Kommentare hat das Video {self._data["title"]} vom Kanal {self._data["channelname"]} mit {self._data["views"]:n} Aufrufen?'
		ans = self._data["comments"]
		self._answer = {
			'value' : ans, 'fmt' : "\d+",
			'text' : f'{numWithSeps(ans)} Kommentar{"" if ans == 1 else "e"} hat https://youtu.be/{self._data["id"]}',
			'reaction' : '{} {} um {} vom richtigen Wert ab.'
		}
	def __getVideoDislikes(self):
		self._question = f'Wie oft bekam das Video {self._data["title"]} vom Kanal {self._data["channelname"]} ein 👎 bei {self._data["likes"]:n} 👍?'
		ans = self._data["dislikes"]
		self._answer = {
			'value' : ans, 'fmt' : "\d+",
			'text' : f'{numWithSeps(ans)} 👎 hat https://youtu.be/{self._data["id"]}',
			'reaction' : '{} {} um {} vom richtigen Wert ab.'
		}
	def __getVideoLikes(self):
		self._question = f'Wie oft bekam das Video {self._data["title"]} vom Kanal {self._data["channelname"]} ein 👍 bei {self._data["dislikes"]:n} 👎?'
		ans = self._data["likes"]
		self._answer = {
			'value' : ans, 'fmt' : "\d+",
			'text' : f'{numWithSeps(ans)} 👍 hat https://youtu.be/{self._data["id"]}',
			'reaction' : '{} {} um {} vom richtigen Wert ab.'
		}
	def __getVideoViews(self):
		self._question = f'Wie oft wurde das am {self._data["published"]} hochgeladene Video {self._data["title"]} vom Kanal {self._data["channelname"]} angeschaut?'
		ans = self._data["views"]
		self._answer = {
			'value' : ans, 'fmt' : "\d+",
			'text' : f'{numWithSeps(ans)} Aufrufe hat https://youtu.be/{self._data["id"]}',
			'reaction' : '{} {} um {} vom richtigen Wert ab.'
		}