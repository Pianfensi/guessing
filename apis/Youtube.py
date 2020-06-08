# /usr/bin/python
from API import *


class Youtube(API):
    def __init__(self):
        self._categories = {
            "channels": {
                "method": self._get_channel,
                "questionTypes": {
                    "created": self._get_created_of_channel,
                    "subs": self._get_channel_subs,
                    "videos": self._get_channel_videos,
                    "views": self._get_channel_views
                }
            },
            "videos": {
                "method": self._get_video,
                "questionTypes": {
                    "age": self._get_video_age,
                    "duration": self._get_video_duration,
                    "comments": self._get_video_comments,
                    "dislikes": self._get_video_dislikes,
                    "likes": self._get_video_likes,
                    "views": self._get_video_views
                }
            }
        }
        API.__init__(self)

    def _get_channel(self):
        url = "https://www.googleapis.com/youtube/v3/search?"
        params = {
            "channelType": "any", "maxResults": 50,
            "order": "relevance", "regionCode": "de",
            "safeSearch": "none", "type": "channel",
            "part": "snippet", "key": GOOGLEKEY,
            "publishedBefore": time_to_string(random.randint(string_to_time("2016-01-01T00:00:00Z"), int(time.time())))}
        results = get_dict_from_request(url, params=params)
        if results is None or "items" not in results:
            return None
        channel = random.choice(results["items"])
        channel_id = channel["id"]["channelId"]
        channel_api = "https://www.googleapis.com/youtube/v3/channels?"
        channel_params = {"id": channel_id, "part": "snippet,statistics,id", "key": GOOGLEKEY}
        stats = get_dict_from_request(channel_api, params=channel_params)
        if stats is None or "items" not in stats:
            return None
        self._success = True
        channel_stats = stats["items"][0]
        self._data = {
            "id": channel_id,
            "name": channel_stats["snippet"]["localized"]["title"], "country": None,
            "published": int(channel_stats["snippet"]["publishedAt"][:4]),
            "subs": int(channel_stats["statistics"]["subscriberCount"]),
            "videos": int(channel_stats["statistics"]["videoCount"]),
            "views": int(channel_stats["statistics"]["viewCount"])
        }
        self._data["longName"] = self._data["name"]
        if "country" in channel_stats["snippet"]:
            self._data["country"] = countries[channel_stats["snippet"]["country"]][0]
            self._data["longName"] = f'{self._data["name"]} ({self._data["country"]})'

    def _get_created_of_channel(self):
        self._question = f'In welchem Jahr wurde der YouTube-Kanal {self._data["longName"]} mit {self._data["videos"]:n} Video{"" if self._data["videos"] == 1 else "s"} erstellt?'
        ans = self._data["published"]

        self._answer = {
            'value': ans, 'fmt': "\d+",
            'text': f'{ans} wurde {self._data["name"]} https://www.youtube.com/channel/{self._data["id"]} erstellt.',
            'reaction': '{} {} um {} Jahr/e vom richtigen Wert ab.'
        }

    def _get_channel_subs(self):
        self._question = f'Wie viele Abonnenten hat der YouTube-Kanal {self._data["longName"]} aus dem Jahr {self._data["published"]}?'
        ans = self._data["subs"]
        self._answer = {
            'value': ans, 'fmt': "\d+",
            'text': f'{seperate_in_thousands(ans)} Abonnenten hat {self._data["name"]} https://www.youtube.com/channel/{self._data["id"]}',
            'reaction': '{} {} um {} vom richtigen Wert ab.'
        }

    def _get_channel_videos(self):
        self._question = f'Wie viele Videos hat der YouTube-Kanal {self._data["longName"]} mit {seperate_in_thousands(self._data["subs"])} Abonnenten?'
        ans = self._data["videos"]
        self._answer = {
            'value': ans, 'fmt': "\d+",
            'text': f'{seperate_in_thousands(ans)} Video{"" if ans == 1 else "s"} hat {self._data["name"]} https://www.youtube.com/channel/{self._data["id"]}',
            'reaction': '{} {} um {} vom richtigen Wert ab.'
        }

    def _get_channel_views(self):
        self._question = f'Wie viele Videoaufrufe hat der YouTube-Kanal {self._data["longName"]} mit {self._data["videos"]} Videos?'
        ans = self._data["views"]
        self._answer = {
            'value': ans, 'fmt': "\d+",
            'text': f'{seperate_in_thousands(ans)} Videoaufrufe hat {self._data["name"]} https://www.youtube.com/channel/{self._data["id"]}',
            'reaction': '{} {} um {} vom richtigen Wert ab.'
        }

    def _get_video(self):
        url = "https://www.googleapis.com/youtube/v3/search?"
        params = {"maxResults": 50, "order": "relevance",
                  "regionCode": "de", "safeSearch": "none",
                  "type": "video", "part": "snippet", "key": GOOGLEKEY,
                  "publishedBefore": time_to_string(random.randint(string_to_time("2016-01-01T00:00:00Z"), int(time.time())))}
        results = get_dict_from_request(url, params=params)
        if results is None or "items" not in results:
            return None
        video = random.choice(results["items"])
        video_id = video["id"]["videoId"]
        video_api = "https://www.googleapis.com/youtube/v3/videos?"
        video_params = {"id": video_id, "part": "contentDetails,snippet,statistics,id", "key": GOOGLEKEY}
        stats = get_dict_from_request(video_api, params=video_params)
        if stats is None or "items" not in stats:
            return None
        self._success = True
        video_stats = stats["items"][0]
        self._data = {
            "id": video_id,
            "title": f'"{video_stats["snippet"]["localized"]["title"]}"',
            "channelname": video_stats["snippet"]["channelTitle"],
            "age": get_age_in_days(video_stats["snippet"]["publishedAt"]),
            "comments": None, "dislikes": None, "likes": None, "views": None,
            "duration": convert_YT_time_to_seconds(video_stats["contentDetails"]["duration"]),
            "published": germanize_date_string(video_stats["snippet"]["publishedAt"])
        }
        self._data["years"] = round(self._data["age"] / 365)
        for stat in ["comment", "dislike", "like", "view"]:
            if f'{stat}Count' in video_stats["statistics"]:
                self._data[f'{stat}s'] = int(video_stats["statistics"][f'{stat}Count'])

    def _get_video_age(self):
        if self._data["years"] > 1:
            unit = "Jahr"
            ans = self._data["years"]
        else:
            unit = "Tag"
            ans = self._data["age"]
        self._question = f'Wie viele {unit}e ist das Video {self._data["title"]} vom Kanal {self._data["channelname"]} bereits online?'
        self._answer = {
            'value': ans, 'fmt': "\d+",
            'text': f'{seperate_in_thousands(ans)} {unit}{"" if ans == 1 else "e"} ist https://youtu.be/{self._data["id"]} online.',
            'reaction': '{} {} um {} ' + unit + '/e vom richtigen Wert ab.'
        }

    def _get_video_duration(self):
        self._question = f'Wie lange ([M]M:SS) dauert das Video {self._data["title"]} vom Kanal {self._data["channelname"]}?'
        duration = self._data["duration"]
        ans = f'{duration // 60:02}:{duration % 60:02}'
        self._answer = {
            'value': ans, 'fmt': "\d{1,2}:[0-5]\d",
            'text': f'{ans} dauert https://youtu.be/{self._data["id"]}',
            'reaction': '{} {} um {} Sekunde/n vom richtigen Wert ab.'
        }

    def _get_video_comments(self):
        self._question = f'Wie viele Kommentare hat das Video {self._data["title"]} vom Kanal {self._data["channelname"]} mit {seperate_in_thousands(self._data["views"])} Aufrufen?'
        ans = self._data["comments"]
        self._answer = {
            'value': ans, 'fmt': "\d+",
            'text': f'{seperate_in_thousands(ans)} Kommentar{"" if ans == 1 else "e"} hat https://youtu.be/{self._data["id"]}',
            'reaction': '{} {} um {} vom richtigen Wert ab.'
        }

    def _get_video_dislikes(self):
        self._question = f'Wie oft bekam das Video {self._data["title"]} vom Kanal {self._data["channelname"]} ein 👎 bei {seperate_in_thousands(self._data["likes"])} 👍?'
        ans = self._data["dislikes"]
        self._answer = {
            'value': ans, 'fmt': "\d+",
            'text': f'{seperate_in_thousands(ans)} 👎 hat https://youtu.be/{self._data["id"]}',
            'reaction': '{} {} um {} vom richtigen Wert ab.'
        }

    def _get_video_likes(self):
        self._question = f'Wie oft bekam das Video {self._data["title"]} vom Kanal {self._data["channelname"]} ein 👍 bei {seperate_in_thousands(self._data["dislikes"])} 👎?'
        ans = self._data["likes"]
        self._answer = {
            'value': ans, 'fmt': "\d+",
            'text': f'{seperate_in_thousands(ans)} 👍 hat https://youtu.be/{self._data["id"]}',
            'reaction': '{} {} um {} vom richtigen Wert ab.'
        }

    def _get_video_views(self):
        self._question = f'Wie oft wurde das am {self._data["published"]} hochgeladene Video {self._data["title"]} vom Kanal {self._data["channelname"]} angeschaut?'
        ans = self._data["views"]
        self._answer = {
            'value': ans, 'fmt': "\d+",
            'text': f'{seperate_in_thousands(ans)} Aufrufe hat https://youtu.be/{self._data["id"]}',
            'reaction': '{} {} um {} vom richtigen Wert ab.'
        }
