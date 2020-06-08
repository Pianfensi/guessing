# /usr/bin/python
import musicbrainzngs

from API import *


class MusicBrainz(API):
    def __init__(self):
        self._categories = {
            "albums": {
                "method": self._get_album,
                "questionTypes": {
                    "tracks": self._get_album_tracks,
                    "duration": self._get_album_duration,
                    "releaseyear": self._get_album_release
                }
            },
            "artists": {
                "method": self._get_artist,
                "questionTypes": {
                    "founded": self._get_group_founded,
                    "ended": self._get_group_ended,
                    "birthyear": self._get_artist_birthyear,
                    "deathyear": self._get_artist_deathyear
                }
            }
        }
        self._country_field = ["DE", "ES", "GB", "US", "IT", "FR", "DK", "SE", "FI", "CZ", "NL", "CA", "NO", "PL", "RU",
                               "AT", "CH", "JP"]
        API.__init__(self)

    def _get_album(self):
        random_country = random.choice(self._country_field)
        musicbrainzngs.set_useragent(
            PROJECTNAME,
            "1.a",
            CONTACT
        )
        try:
            results = musicbrainzngs.search_releases(query="", limit=10, offset=None, strict=False,
                                                     country=random_country, mediums="CD", type="Album")
            offset = random.randint(0, results["release-count"] - 100)
            result = musicbrainzngs.search_releases(query="", limit=100, offset=offset, strict=False,
                                                    country=random_country, mediums="CD", type="Album",
                                                    reid="1ec09df8-aef8-48f1-91a9-92a982bf0dfe")
        except:
            return None
        releases = result["release-list"]
        releases_with_tracks = [x for x in releases if "medium-track-count" in x and x["medium-track-count"] > 4]
        while True:
            release = random.choice(releases_with_tracks)
            release_id = release["id"]
            try:
                tracks = musicbrainzngs.browse_recordings(release=release_id)
                self._success = True
            except:
                return None
            try:
                release_length = sum([int(int(x["length"]) / 1000) for x in tracks["recording-list"]])
                break
            except:
                pass
        self._data = {
            "title": release["title"], "id": release_id, "country": countries[random_country][0], "releaseyear": None,
            "artist": release["artist-credit"][0]["name"], "tracks": tracks["recording-count"],
            "duration": release_length
        }
        if "date" in release:
            self._data["releaseyear"] = int(release["date"][:4])

    def _get_album_tracks(self):
        self._question = f'Wie viele Tracks sind auf dem Album "{self._data["title"]}" von {self._data["artist"]}, {self._data["country"]}?'
        ans = self._data["tracks"]
        self._answer = {
            "value": ans, "fmt": "\d+",
            "text": f'{ans} Tracks sind auf dem Album {self._data["title"]} https://musicbrainz.org/release/{self._data["id"]}',
            "reaction": "{} {} um {} von der richtigen Anzahl ab."
        }

    def _get_album_duration(self):
        self._question = f'Wie ist die Laufzeit ([M]M:SS) vom Album "{self._data["title"]}" von {self._data["artist"]}, {self._data["country"]}?'
        ans = f'{self._data["duration"] // 60:02}:{self._data["duration"] % 60:02}'
        self._answer = {
            'value': ans, 'fmt': "\d{1,2}:[0-5]\d",
            'text': f'{ans} ist die Laufzeit von "{self._data["title"]}" https://musicbrainz.org/release/{self._data["id"]} ',
            'reaction': '{} {} um {} Sekunde/n vom richtigen Wert ab.'
        }

    def _get_album_release(self):
        self._question = f'In welchem Jahr erschien das Album "{self._data["title"]}" von {self._data["artist"]}, {self._data["country"]}?'
        ans = self._data["releaseyear"]
        self._answer = {
            "value": ans, "fmt": "\d+",
            "text": f'{ans} erschien "{self._data["title"]}" https://musicbrainz.org/release/{self._data["id"]}',
            "reaction": "{} {} um {} Jahr/e vom richtigen Jahr ab."
        }

    def _get_artist(self):
        random_country = random.choice(self._country_field)
        musicbrainzngs.set_useragent(
            PROJECTNAME,
            "1.a",
            CONTACT
        )
        try:
            results = musicbrainzngs.search_artists(query="", limit=10, offset=None, strict=False,
                                                    country=random_country)
            offset = random.randint(0, results["artist-count"] - 100)
            result = musicbrainzngs.search_artists(query="", limit=100, offset=offset, strict=False,
                                                   country=random_country)
            self._success = True
        except:
            return None
        interesting_artist = False
        while not interesting_artist:
            artist_data = random.choice(result["artist-list"])
            self._data = {
                "artistId": artist_data["id"],
                "artist": artist_data["name"], "country": countries[random_country][0],
                "founded": None, "ended": None, "group": ("type" in artist_data and artist_data["type"] == "Group"),
                "person": ("type" in artist_data and artist_data["type"] == "Person"), "birthyear": None,
                "deathyear": None, "gender": None, "website": f'https://musicbrainz.org/artist/' + artist_data["id"]
            }
            if "life-span" in artist_data:
                life_span = artist_data["life-span"]
                if "begin" in life_span and life_span["begin"] != "false":
                    if self._data["person"]:
                        self._data["birthyear"] = int(life_span["begin"][:4])
                    else:
                        self._data["founded"] = int(life_span["begin"][:4])
                    interesting_artist = True
                if "end" in life_span:
                    if self._data["person"]:
                        self._data["deathyear"] = int(life_span["end"][:4])
                    else:
                        self._data["ended"] = int(life_span["end"][:4])
                    interesting_artist = True
            if "gender" in artist_data:
                self._data["gender"] = artist_data["gender"]

    def _get_group_founded(self):
        self._question = f'In welchem Jahr wurde die Gruppe "{self._data["artist"]}", {self._data["country"]} gegründet?'
        ans = self._data["founded"]
        self._answer = {
            "value": ans, "fmt": "\d{4}",
            "text": f'{ans} wurde die Gruppe "{self._data["artist"]}" gegründet {self._data["website"]}',
            "reaction": "{} {} um {} Jahr/e vom richtigen Jahr ab."
        }

    def _get_group_ended(self):
        self._question = f'In welchem Jahr hat sich die Gruppe "{self._data["artist"]}", {self._data["country"]} aufgelöst?'
        ans = self._data["ended"]
        self._answer = {
            "value": ans, "fmt": "\d{4}",
            "text": f'{ans} löste sich "{self._data["artist"]}" auf {self._data["website"]}',
            "reaction": "{} {} um {} Jahr/e vom richtigen Jahr ab."
        }

    def _get_artist_birthyear(self):
        address = "die Interpretin" if self._data["gender"] == "female" else "der Interpret"
        self._question = f'In welchem Jahr wurde {address} {self._data["artist"]} aus {self._data["country"]} geboren?'
        ans = self._data["birthyear"]
        self._answer = {
            "value": ans, "fmt": "\d{4}",
            "text": f'{ans} wurde {self._data["artist"]} geboren {self._data["website"]}',
            "reaction": "{} {} um {} Jahr/e vom richtigen Jahr ab."
        }

    def _get_artist_deathyear(self):
        address = "die Interpretin" if self._data["gender"] == "female" else "der Interpret"
        self._question = f'In welchem Jahr starb {address} {self._data["artist"]} aus {self._data["country"]}?'
        ans = self._data["deathyear"]
        self._answer = {
            "value": ans, "fmt": "\d{4}",
            "text": f'{ans} starb {self._data["artist"]} {self._data["website"]}',
            "reaction": "{} {} um {} Jahr/e vom richtigen Jahr ab."
        }
MusicBrainz().test_api()