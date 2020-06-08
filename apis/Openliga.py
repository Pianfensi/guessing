# /usr/bin/python
from API import *


class Openliga(API):
    def __init__(self):
        self._categories = {
            "clubs": {
                "method": self._get_club,
                "questionTypes": {
                    "rank": self._get_club_rank,
                    "won": self._get_club_won,
                    "lost": self._get_club_lost,
                    "draw": self._get_club_draw,
                    "goals": self._get_club_goals,
                    "opponentGoals": self._get_club_opponent_goals,
                    "points": self._get_club_points
                }
            }
        }
        API.__init__(self)

    def _get_club(self):
        while True:
            season = random.randint(2009, time.localtime()[0] - 1)
            url = f'https://www.openligadb.de/api/getbltable/bl1/{season}'
            results = get_dict_from_request(url)
            if len(results) > 0:
                break
        rank = random.randint(0, len(results))
        club = results[rank]
        self._success = True
        self._data = {
            "team": club["TeamName"], "rank": rank + 1, "season": f'{season}/{str(season + 1)[-2:]}',
            "won": club["Won"], "lost": club["Lost"], "draw": club["Draw"],
            "goals": club["Goals"], "opponentGoals": club["OpponentGoals"],
            "points": club["Points"]
        }

    def _get_club_rank(self):
        self._question = f'Auf welchem Tabellenplatz landete {self._data["team"]} am Ende der Saison {self._data["season"]} der 1. Bundesliga?'
        ans = self._data["rank"]
        self._answer = {
            "value": ans, "fmt": "\d+",
            "text": f'Der {ans}. Platz gehörte {self._data["team"]}.',
            "reaction": "{} {} um {} vom richtigen Platz ab."
        }

    def _get_club_won(self):
        self._question = f'Wie viele Spiele hat {self._data["team"]} in der Saison {self._data["season"]} der 1. Bundesliga gewonnen?'
        ans = self._data["won"]
        self._answer = {
            "value": ans, "fmt": "\d+",
            "text": f'{ans} Spiel{"" if ans == 1 else "e"} hat {self._data["team"]} gewonnen.',
            "reaction": "{} {} um {} vom richtigen Wert ab."
        }

    def _get_club_lost(self):
        self._question = f'Wie viele Spiele hat {self._data["team"]} in der Saison {self._data["season"]} der 1. Bundesliga verloren?'
        ans = self._data["lost"]
        self._answer = {
            "value": ans, "fmt": "\d+",
            "text": f'{ans} Spiel{"" if ans == 1 else "e"} hat {self._data["team"]} verloren.',
            "reaction": "{} {} um {} vom richtigen Wert ab."
        }

    def _get_club_draw(self):
        self._question = f'Wie viele Spiele endeten für {self._data["team"]} in der Saison {self._data["season"]} der 1. Bundesliga unentschieden?'
        ans = self._data["draw"]
        self._answer = {
            "value": ans, "fmt": "\d+",
            "text": f'{ans} Spiel{"" if ans == 1 else "e"} endeten für {self._data["team"]} unentschieden.',
            "reaction": "{} {} um {} vom richtigen Wert ab."
        }

    def _get_club_goals(self):
        self._question = f'Wie viele Tore erzielte {self._data["team"]} in der Saison {self._data["season"]} der 1. Bundesliga?'
        ans = self._data["goals"]
        self._answer = {
            "value": ans, "fmt": "\d+",
            "text": f'{ans} Tor{"" if ans == 1 else "e"} erzielte {self._data["team"]}.',
            "reaction": "{} {} um {} vom richtigen Wert ab."
        }

    def _get_club_opponent_goals(self):
        self._question = f'Wie viele Tore kassierte {self._data["team"]} in der Saison {self._data["season"]} der 1. Bundesliga?'
        ans = self._data["opponentGoals"]
        self._answer = {
            "value": ans, "fmt": "\d+",
            "text": f'{ans} Tor{"" if ans == 1 else "e"} kassierte {self._data["team"]}.',
            "reaction": "{} {} um {} vom richtigen Wert ab."
        }

    def _get_club_points(self):
        self._question = f'Wie viele Punkte sammelte {self._data["team"]} in der Saison {self._data["season"]} der 1. Bundesliga?'
        ans = self._data["points"]
        self._answer = {
            "value": ans, "fmt": "\d+",
            "text": f'{ans} Punkt{"" if ans == 1 else "e"} sammelte {self._data["team"]}.',
            "reaction": "{} {} um {} vom richtigen Wert ab."
        }
