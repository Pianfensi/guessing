# /usr/bin/python
from xml.etree import cElementTree as ElementTree

from API import *


class BGG(API):
    def __init__(self):
        self._categories = {
            "boardgames": {
                "method": self._get_boardgame,
                "questionTypes": {
                    "published": self._get_boardgame_published,
                    "minPlayers": self._get_boardgame_min_players,
                    "maxPlayers": self._get_boardgame_max_players,
                    "maxPlaytime": self._get_boardgame_max_playtime,
                    "minAge": self._get_boardgame_min_age
                }
            }
        }
        API.__init__(self)

    def _get_boardgame(self):
        id_range = 50
        while True:
            start_id = random.randint(1, 1166e2 - id_range)
            params = {"id": ",".join([str(x) for x in range(start_id, start_id + id_range)]), "type": "boardgame"}
            r = requests.get("https://api.geekdo.com/xmlapi2/thing?" + urllib.parse.urlencode(params))
            try:
                root = ElementTree.XML(r.text)
                results = XmlListConfig(root)
                self._success = True
            except:
                return None
            if len(results) > 0:
                break
        result = random.choice(results)
        title = None
        if isinstance(result["name"], list):
            for x in result["name"]:
                if x["type"] == "primary":
                    title = x["value"]
        else:
            title = result["name"]["value"]
        self._data = {
            "title": title, "minPlayers": int(result["minplayers"]["value"]),
            "maxPlayers": int(result["maxplayers"]["value"]),
            "minAge": int(result["minage"]["value"]), "published": int(result["yearpublished"]["value"]),
            "maxPlaytime": int(result["maxplaytime"]["value"]),
            "website": f'https://boardgamegeek.com/boardgame/{result["id"]}'
        }
        for k, v in self._data.items():
            if v == 0:
                self._data[k] = None

    def _get_boardgame_published(self):
        self._question = f'In welchem Jahr erschien das Gesellschaftsspiel "{self._data["title"]}"?'
        ans = self._data["published"]
        self._answer = {
            "value": ans, "fmt": "\d{4}",
            "text": f'{ans} erschien "{self._data["title"]}" {self._data["website"]}',
            "reaction": "{} {} um {} Jahr/e vom richtigen Jahr ab."
        }

    def _get_boardgame_min_players(self):
        self._question = f'Wie viele Spielende werden mindestens für das Gesellschaftsspiel "{self._data["title"]}" benötigt?'
        ans = self._data["minPlayers"]
        self._answer = {
            "value": ans, "fmt": "\d+",
            "text": f'{ans} ist das Minimum an Leuten für "{self._data["title"]}" {self._data["website"]}',
            "reaction": "{} {} um {} vom richtigen Wert ab."
        }

    def _get_boardgame_max_players(self):
        self._question = f'Wie viele Spielende können höchstens das Gesellschaftsspiel "{self._data["title"]}" spielen?'
        ans = self._data["maxPlayers"]
        self._answer = {
            "value": ans, "fmt": "\d+",
            "text": f'{ans} ist das Maximum an Leuten für "{self._data["title"]}" {self._data["website"]}',
            "reaction": "{} {} um {} vom richtigen Wert ab."
        }

    def _get_boardgame_min_age(self):
        self._question = f'Ab welchem Alter wird das Gesellschaftsspiel "{self._data["title"]}" empfohlen?'
        ans = self._data["minAge"]
        self._answer = {
            "value": ans, "fmt": "\d+",
            "text": f'{ans} ist das Mindestalter für "{self._data["title"]}" {self._data["website"]}',
            "reaction": "{} {} um {} vom richtigen Wert ab."
        }

    def _get_boardgame_max_playtime(self):
        self._question = f'Wie viele Minuten werden für das Gesellschaftsspiel "{self._data["title"]}" vom Hersteller als Höchstdauer angegeben?'
        ans = self._data["maxPlaytime"]
        self._answer = {
            "value": ans, "fmt": "\d+",
            "text": f'{ans} Minuten ist die Höchstdauer für "{self._data["title"]}" {self._data["website"]}',
            "reaction": "{} {} um {} Minute/n vom richtigen Wert ab."
        }
