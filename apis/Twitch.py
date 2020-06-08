# /usr/bin/python
from API import *


class Twitch(API):
    def __init__(self):
        self._headers = {
            'Client-ID': TWITCHID,
            'Authorization': 'OAuth %s' % TWITCHAUTH,
            'Accept': 'application/vnd.twitchtv.v5+json'
        }
        self._categories = {
            "games": {
                "method": self._get_game,
                "questionTypes": {
                    "channels": self._get_channels_with_game,
                    "viewers": self._get_game_viewers
                }
            },
            "streams": {
                "method": self._get_streams,
                "questionTypes": {
                    "language": self._get_streams_with_language,
                    "adult": self._get_streams_with_adults,
                    "created": self._get_created_of_stream,
                    "followers": self._get_stream_followers,
                    "livetime": self._get_stream_livetime,
                    "views": self._get_stream_views,
                    "viewers": self._get_stream_viewers
                }
            }
        }
        API.__init__(self)

    # Games
    def _get_game(self):
        url = "https://api.twitch.tv/kraken/games/top?"
        params = {"limit": 100}
        top_games = get_dict_from_request(url, params=params, headers=self._headers)
        if top_games is None or "top" not in top_games:  # successful
            return None
        self._success = True
        game = random.choice(top_games["top"])
        self._data = {
            "name": game["game"]["name"], "channels": game["channels"],
            "viewers": game["viewers"]
        }

    def _get_channels_with_game(self):
        self._question = f'Wie viele imGlitch Streamer spielen aktuell "{self._data["name"]}"?'
        ans = int(self._data["channels"])
        self._answer = {
            'value': ans, 'fmt': "\d+",
            'text': f'{seperate_in_thousands(ans)} Streamer spielen "{self._data["name"]}".',
            'reaction': '{} {} um {} vom richtigen Wert ab.'
        }

    def _get_game_viewers(self):
        self._question = f'Wie viele Leute gucken aktuell {self._data["name"]}?'
        ans = int(self._data["viewers"])
        self._answer = {
            'value': ans, 'fmt': "\d+",
            'text': f'{seperate_in_thousands(ans)} Person{"en" if ans > 1 else ""} schauen "{self._data["name"]}".',
            'reaction': '{} {} um {} vom richtigen Wert ab.'
        }

    # Streams
    def _get_streams(self):
        streams = []
        for i in range(5):
            rjson = get_dict_from_request("https://api.twitch.tv/kraken/streams/?", {"limit": 100, "offset": i},
                                       headers=self._headers)
            if rjson is None or "streams" not in rjson:
                return None
            streams += rjson["streams"]
        self._success = True
        stream = random.choice(streams)
        self._data = {
            "name": stream["channel"]["display_name"], "created": int(stream["channel"]["created_at"][:4]),
            "followers": int(stream["channel"]["followers"]), "views": int(stream["channel"]["views"]),
            "start": string_to_time(stream["created_at"]), "viewers": int(stream["viewers"]),
            "game": stream["channel"]["game"], "user": stream["channel"]["name"],
        }
        self._metadata = {
            "language": {}, "adultContent": [x["channel"]["mature"] for x in streams].count(True) // 5
        }
        for lang in langs:
            self._metadata["language"][lang] = [x["channel"]["broadcaster_language"][:2] for x in streams].count(lang)

    def _get_streams_with_language(self):
        lang = get_random_key(self._metadata["language"])
        self._question = f'Wie viele der 🔴 Top-500-Twitch-Streamer streamen auf {langs[lang]}?'
        ans = self._metadata["language"][lang]
        self._answer = {
            'value': ans, 'fmt': "\d+",
            'text': f'{ans} streamen auf {langs[lang]}.',
            'reaction': '{} {} um {} vom richtigen Wert ab.'
        }

    def _get_streams_with_adults(self):
        self._question = 'Wie viel Prozent der 🔴 Top-500-Twitch-Streamer streamen Erwachseneninhalte?'
        ans = self._metadata["adultContent"]
        self._answer = {
            'value': ans, 'fmt': "\d+",
            'text': f'{ans} streamen 18+.',
            'reaction': '{} {} um {} Prozentpunkt/e vom richtigen Wert ab.'
        }

    def _get_created_of_stream(self):
        self._question = f'In welchem Jahr wurde der imGlitch Kanal {self._data["name"]} erstellt?'
        ans = self._data["created"]
        self._answer = {
            'value': ans, 'fmt': "\d+",
            'text': f'{ans} wurde https://twitch.tv/{self._data["user"]} erstellt.',
            'reaction': '{} {} um {} Jahr/e vom richtigen Wert ab.'
        }

    def _get_stream_followers(self):
        self._question = f'Wie viele Follower hat der imGlitch Kanal {self._data["name"]} mit aktuell {seperate_in_thousands(self._data["viewers"])} Zuschauenden?'
        ans = self._data["followers"]
        self._answer = {
            'value': ans, 'fmt': "\d+",
            'text': f'{seperate_in_thousands(ans)} folgen https://twitch.tv/{self._data["user"]}',
            'reaction': '{} {} um {} vom richtigen Wert ab.'
        }

    def _get_stream_livetime(self):
        self._question = f'Wie viele Minuten ist der imGlitch Stream von {self._data["name"]} bereits live 🔴?'
        ans = int(time.time() - self._data["start"]) // 60
        self._answer = {
            'value': ans, 'fmt': "\d+",
            'text': f'{seperate_in_thousands(ans)} Minut{"en" if ans > 1 else ""} streamt https://twitch.tv/{self._data["user"]} schon.',
            'reaction': '{} {} um {} Minute/n vom richtigen Wert ab.'
        }

    def _get_stream_views(self):
        self._question = f'Wie viele Aufrufe hat der imGlitch Kanal von {self._data["name"]}?'
        ans = self._data["views"]
        self._answer = {
            'value': ans, 'fmt': "\d+",
            'text': f'{seperate_in_thousands(ans)} Aufrufe hat der Kanal https://twitch.tv/{self._data["user"]}',
            'reaction': '{} {} um {} vom richtigen Wert ab.'
        }

    def _get_stream_viewers(self):
        self._question = f'Wie viele ZuschauerInnen hat der imGlitch Kanal {self._data["name"]} beim Streamen von "{self._data["game"]}"?'
        ans = self._data["viewers"]
        self._answer = {
            'value': ans, 'fmt': "\d+",
            'text': f'{seperate_in_thousands(ans)} Person{"" if ans == 1 else "en"} schauen https://twitch.tv/{self._data["user"]}',
            'reaction': '{} {} um {} vom richtigen Wert ab.'
        }
