# /usr/bin/python
from API import *


class Artsy(API):
    def __init__(self):
        self._categories = {
            "artists": {
                "method": self._get_artist,
                "questionTypes": {
                    "birth": self._get_artist_birth,
                    "death": self._get_artist_death
                }
            },
            "artworks": {
                "method": self._get_artwork,
                "questionTypes": {
                    "year": self._get_artwork_year,
                    "height": self._get_artwork_height,
                    "width": self._get_artwork_width
                }
            }
        }
        API.__init__(self)
        # retrieve token
        url = "https://api.artsy.net/api/tokens/xapp_token?"
        params = {"client_id": ARTSYID, "client_secret": ARTSYSECRET}
        r = requests.post(url, params=params)
        self._headers = {"X-Xapp-Token": json.loads(r.text)["token"]}

    def _get_artist(self):
        url = "https://api.artsy.net/api/artists?"
        params = {"size": 100, "offset": random.randint(0, 10) * 100, "artworks": True}
        results = get_dict_from_request(url, params=params, headers=self._headers)
        if results is None:
            return None
        self._success = True
        filtered = [x for x in results["_embedded"]["artists"] if
                    re.match("^.{5,}$", x["name"]) and x["birthday"] != ""]
        result = random.choice(filtered)
        self._data = {
            "id": result["id"], "name": result["name"], "birth": None, "death": None,
            "gender": "male" if result["gender"] == "" else result["gender"]
        }
        if result["deathday"]:
            self._data["death"] = extract_year(result["deathday"])
        if result["birthday"]:
            self._data["birth"] = extract_year(result["birthday"])

    def _get_artist_birth(self):
        self._question = f'In welchem Jahr wurde {"der Künstler" if self._data["gender"] == "male" else "die Künstlerin"} {self._data["name"]} geboren?'
        ans = self._data["birth"]
        self._answer = {
            "value": ans, "fmt": "\d{4}",
            "text": f'{ans} wurde {self._data["name"]} https://artsy.net/artist/{self._data["id"]} geboren.',
            "reaction": "{} {} um {} Jahr/e vom richtigen Geburtsjahr ab."
        }

    def _get_artist_death(self):
        self._question = f'In welchem Jahr starb {"der Künstler" if self._data["gender"] == "male" else "die Künstlerin"} {self._data["name"]}?'
        ans = self._data["death"]
        self._answer = {
            "value": ans, "fmt": "\d{4}",
            "text": f'{ans} ist {self._data["name"]} https://artsy.net/artist/{self._data["id"]} gestorben.',
            "reaction": "{} {} um {} Jahr/e vom richtigen Sterbejahr ab."
        }

    def _get_artwork(self):
        while True:
            self._get_artist()
            self._success = False
            url = "https://api.artsy.net/api/artworks?"
            params = {"artist_id": self._data["id"], "size": 100}
            results = get_dict_from_request(url, params=params, headers=self._headers)
            if results is None:
                return None
            filtered = [x for x in results["_embedded"]["artworks"] if re.match("^.*\d{4}.*$", x["date"])]
            if len(filtered) > 0:
                break
        self._success = True
        result = random.choice(filtered)
        year_compiler = re.compile("\d{4}")
        years = year_compiler.findall(result["date"])
        self._data = {
            "id": result["id"], "artist": self._data["name"], "title": result["title"],
            "height": None, "width": None, "year": None,
            "preview": ""
        }
        try:
            self._data["preview"] = " " + result["_links"]["thumbnail"]["href"]
        except:
            pass
        if result["dimensions"]["cm"]["height"]:
            self._data["height"] = int(result["dimensions"]["cm"]["height"] * 10)
        if result["dimensions"]["cm"]["width"]:
            self._data["height"] = int(result["dimensions"]["cm"]["width"] * 10)
        if len(years) > 0:
            self._data["year"] = int(years[0])

    def _get_artwork_year(self):
        self._question = f'Aus welchem Jahr ist {self._data["artist"]}s Kunstwerk "{self._data["title"]}"?'
        ans = self._data["year"]
        self._answer = {
            "value": ans, "fmt": "\d{4}",
            "text": f'{ans} wurde "{self._data["title"]}"{self._data["preview"]} erstellt.',
            "reaction": "{} {} um {} Jahr/e vom richtigen Jahr ab."
        }

    def _get_artwork_height(self):
        apos = "'"
        self._question = f'Wie viele Millimeter ist {self._data["artist"]}{apos if self._data["artist"][-1] == "s" else "s"} Kunstwerk "{self._data["title"]}" hoch?'
        ans = self._data["height"]
        self._answer = {
            "value": ans, "fmt": "\d+",
            "text": f'{ans} mm ist "{self._data["title"]}"{self._data["preview"]} hoch.',
            "reaction": "{} {} um {} mm vom richtigen Wert ab."
        }

    def _get_artwork_width(self):
        apos = "'"
        self._question = f'Wie viele Millimeter ist {self._data["artist"]}{apos if self._data["artist"][-1] == "s" else "s"} Kunstwerk "{self._data["title"]}" breit?'
        ans = self._data["width"]
        self._answer = {
            "value": ans, "fmt": "\d+",
            "text": f'{ans} mm ist "{self._data["title"]}"{self._data["preview"]} breit.',
            "reaction": "{} {} um {} mm vom richtigen Wert ab."
        }
