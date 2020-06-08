# /usr/bin/python
import hashlib

from API import *


class Marvel(API):
    def __init__(self):
        self._categories = {
            "characters": {
                "method": self._get_character,
                "questionTypes": {
                    "comics": self._get_character_comics
                }
            },
            "comics": {
                "method": self._get_comic,
                "questionTypes": {
                    "published": self._get_comic_published,
                    "pages": self._get_comic_pages,
                    "total": self._get_comics_total
                }
            },
            "series": {
                "method": self._get_series,
                "questionTypes": {
                    "comics": self._get_series_comics,
                    "start": self._get_series_start,
                    "end": self._get_series_end
                }
            }
        }
        self._private_key = MARVELPRIVATEKEY
        self._public_key = MARVELPUBLICKEY
        API.__init__(self)

    def _hash(self):
        timestamp = generate_token()
        return timestamp, hashlib.md5((timestamp + self._private_key + self._public_key).encode("utf-8")).hexdigest()

    def _get_character(self):
        url = "https://gateway.marvel.com/v1/public/characters?"
        ts, hash_value = self._hash()
        params = {"limit": 100, "apikey": self._public_key, "hash": hash_value, "ts": ts, "modifiedSince": "2010-01-01"}
        result = get_dict_from_request(url, params=params)
        totals = result["data"]["total"]
        params["offset"] = random.randint(0, totals // 100) * 100
        result = get_dict_from_request(url, params=params)
        if result is None or result["status"] != "Ok":
            return None
        self._success = True
        result = [x for x in result["data"]["results"] if x["comics"]["available"] > 0]
        character = random.choice(result)
        self._data = {
            "name": character["name"], "comics": character["comics"]["available"],
            "website": f'https://www.marvel.com/characters/{re.sub("[()]", "", character["name"].lower().replace(" ", "-"))}'
        }

    def _get_character_comics(self):
        self._question = f'In wie vielen Comics taucht der Marvel-Charakter {self._data["name"]} auf?'
        ans = self._data["comics"]
        self._answer = {
            "value": ans, "fmt": "\d+",
            "text": f'In {seperate_in_thousands(ans)} Comic{"" if ans == 1 else "s"} taucht {self._data["name"]} auf.',
            "reaction": "{} {} um {} von der richtigen Anzahl ab."
        }

    def _get_comic(self):
        url = "https://gateway.marvel.com/v1/public/comics?"
        ts, hash_value = self._hash()
        year = random.randint(1970, time.localtime()[0] - 1)
        params = {"limit": 100, "apikey": self._public_key, "hash": hash_value,
                  "ts": ts, "dateRange": f'{year}-01-01,{year}-12-31', "format": "comic", "formatType": "comic"}
        result = get_dict_from_request(url, params=params)
        totals = result["data"]["total"]
        params["offset"] = random.randint(0, totals // 100) * 100
        result = get_dict_from_request(url, params=params)
        if result is None or result["status"] != "Ok":
            return None
        self._success = True
        comic = random.choice(result["data"]["results"])
        self._data = {
            "id": comic["id"], "title": comic["title"], "published": None,
            "website": comic["urls"][0]["url"], "pages": comic["pageCount"] if comic["pageCount"] > 0 else None,
            "comicYear": year, "comicsTotal": totals
        }
        for date in comic["dates"]:
            if date["type"] == "onsaleDate":
                self._data["published"] = germanize_date_string(date["date"])

    def _get_comic_published(self):
        self._question = f'An welchem Tag (TT.MM.JJJJ) erschien der Comic "{self._data["title"]}"?'
        ans = self._data["published"]
        self._answer = {
            'value': ans, 'fmt': "\d\d\.\d\d\.\d\d\d\d",
            "text": f'Am {ans} erschien "{self._data["title"]}" {self._data["website"]}',
            "reaction": "{} {} um {} Tag/e vom richtigen Datum ab."
        }

    def _get_comic_pages(self):
        self._question = f'Wie viele Seiten hat der Comic "{self._data["title"]}"?'
        ans = self._data["pages"]
        self._answer = {
            "value": ans, "fmt": "\d+",
            "text": f'{ans} Seiten hat "{self._data["title"]}" {self._data["website"]}',
            "reaction": "{} {} um {} Seite/n vom richtigen Wert ab."
        }

    def _get_comics_total(self):
        self._question = f'Wie viele Marvel-Comics erschienen {self._data["comicYear"]}?'
        ans = self._data["comicsTotal"]
        self._answer = {
            "value": ans, "fmt": "\d+",
            "text": f'{seperate_in_thousands(ans)} Comics erschienen {self._data["comicYear"]}.',
            "reaction": "{} {} um {} vom richtigen Wert ab."
        }

    def _get_series(self):
        url = "https://gateway.marvel.com/v1/public/series?"
        ts, hash_value = self._hash()
        params = {"limit": 100, "apikey": self._public_key, "hash": hash_value, "ts": ts, "contains": "comic"}
        result = get_dict_from_request(url, params=params)
        totals = result["data"]["total"]
        params["offset"] = random.randint(0, totals // 100) * 100
        result = get_dict_from_request(url, params=params)
        if result is None or result["status"] != "Ok":
            return None
        self._success = True
        series = random.choice(result["data"]["results"])
        self._data = {
            "title": re.sub(" \([^)]+\)", "", series["title"]), "comics": series["comics"]["returned"],
            "start": series["startYear"],
            "end": (None if series["endYear"] == 2099 else series["endYear"]),
            "website": f'https://www.marvel.com/comics/series/{series["id"]}/{re.sub("[()/]", "", series["title"].lower().replace(" ", "_"))}'
        }

    def _get_series_comics(self):
        self._question = f'Wie viele Comics umfasst die Serie "{self._data["title"]}"?'
        ans = self._data["comics"]
        self._answer = {
            "value": ans, "fmt": "\d+",
            "text": f'{ans} Comic{"" if ans == 1 else "s"} hat die Serie "{self._data["title"]}" {self._data["website"]}',
            "reaction": "{} {} um {} vom richtigen Wert ab."
        }

    def _get_series_start(self):
        self._question = f'In welchem Jahr startete die Comicserie "{self._data["title"]}"?'
        ans = self._data["start"]
        self._answer = {
            "value": ans, "fmt": "\d{4}",
            "text": f'{ans} startete "{self._data["title"]}" {self._data["website"]}',
            "reaction": "{} {} um {} Jahr/e vom richtigen Jahr ab."
        }

    def _get_series_end(self):
        self._question = f'In welchem Jahr endete die Comicserie "{self._data["title"]}"?'
        ans = self._data["end"]
        self._answer = {
            "value": ans, "fmt": "\d{4}",
            "text": f'{ans} endete "{self._data["title"]}" {self._data["website"]}',
            "reaction": "{} {} um {} Jahr/e vom richtigen Jahr ab."
        }
