# /usr/bin/python
from API import *


def get_ymd_from_steam(s: str) -> str:
    """ converts steam's convention for dates to YYYY-MM-DD

    i.e.: 16 May, 2020 -> 2020-05-16"""
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    month_dict = {}
    date_list = s.split(" ")
    for i in range(len(months)):
        month_dict[months[i] + ","] = f'{i + 1:02}'
    try:
        return f'{date_list[2]}-{month_dict[date_list[1]]}-{int(date_list[0]):02}'
    except:
        return None


class Steam(API):
    def __init__(self):
        self._categories = {
            "games": {
                "method": self._get_game,
                "questionTypes": {
                    "achievements": self._get_game_achievements,
                    "reviews": self._get_game_reviews,
                    "dlcs": self._get_game_dlcs,
                    "price": self._get_game_price,
                    "metacritic": self._get_game_metacritic,
                    "release": self._get_game_release
                }
            },
            "achievements": {
                "method": self._get_achievement,
                "questionTypes": {
                    "least": self._get_least_achievement,
                    "most": self._get_most_achievement,
                    "random": self._get_random_achievement,
                    "completion": self._get_achievement_completion
                }
            }
        }
        API.__init__(self)

    def _get_game(self):
        params = {"key": STEAMAPI, "format": "json", "count": 5}
        url = "https://store.steampowered.com/api/appdetails/?"
        while True:
            app = random.choice(steam_apps)
            params["appids"] = app["appid"]
            json = get_dict_from_request(url, params)
            if json[str(params["appids"])]["success"]:
                app_dict = json[str(params["appids"])]["data"]
                if "Demo" not in app_dict["name"]:  # ignore Demos
                    break
            else:
                return None
        self._success = True
        self._data = {
            "name": app_dict["name"], "id": app["appid"], "displayName": app_dict["name"],
            "achievements": None, "reviews": None, "release": None,
            "price": None, "metacritic": None, "dlcs": None
        }
        if "fullgame" in app_dict:
            self._data["name"] = f'{self._data["name"]} (DLC)'
        if "developers" in app_dict:
            self._data["displayName"] = f'{self._data["name"]}" vom Entwickler "{app_dict["developers"][0]}'
        any_info = False
        # looks for any information
        if "achievements" in app_dict and app_dict["achievements"]["total"] > 0:
            self._data["achievements"] = app_dict["achievements"]["total"]
            any_info = True
        if "release_date" in app_dict and not app_dict["release_date"]["coming_soon"]:
            self._data["release"] = get_ymd_from_steam(app_dict["release_date"]["date"])
            any_info = True
        if "price_overview" in app_dict:
            self._data["price"] = app_dict["price_overview"]["final"] / 100  # current price
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

    def _get_game_achievements(self):
        self._question = f'Wie viele Steam-Errungenschaften hat "{self._data["displayName"]}"?'
        ans = self._data["achievements"]
        self._answer = {
            'value': ans, 'fmt': "\d+",
            'text': f'{ans} Errungenschaft{"" if ans == 1 else "en"} hat "{self._data["name"]}" https://store.steampowered.com/app/{self._data["id"]}',
            'reaction': '{} {} um {} vom richtigen Wert ab.'
        }

    def _get_game_reviews(self):
        self._question = f'Wie viele Reviews besitzt "{self._data["displayName"]}" auf Steam?'
        ans = self._data["reviews"]
        self._answer = {
            'value': ans, 'fmt': "\d+",
            'text': f'{ans} Review{"" if ans == 1 else "s"} besitzt "{self._data["name"]}" https://store.steampowered.com/app/{self._data["id"]}',
            'reaction': '{} {} um {} vom richtigen Wert ab.'
        }

    def _get_game_dlcs(self):
        self._question = f'Wie viele DLCs hat das Spiel "{self._data["displayName"]}" auf Steam?'
        ans = self._data["dlcs"]
        self._answer = {
            'value': ans, 'fmt': "\d+",
            'text': f'{ans} DLC{"" if ans == 1 else "s"} besitzt "{self._data["name"]}" https://store.steampowered.com/app/{self._data["id"]}',
            'reaction': '{} {} um {} vom richtigen Wert ab.'
        }

    def _get_game_price(self):
        self._question = f'Wie viel Euro (auf den Cent genau) kostet aktuell "{self._data["displayName"]}" auf Steam?'
        ans = self._data["price"]
        self._answer = {
            'value': ans, 'fmt': "\d+[,\.]\d\d",
            'text': f'{germanize_number(ans)} kostet "{self._data["name"]}" https://store.steampowered.com/app/{self._data["id"]}',
            'reaction': '{} {} um {} € vom richtigen Wert ab.'
        }

    def _get_game_metacritic(self):
        self._question = f'Welchen Metascore hat das Spiel "{self._data["displayName"]}"?'
        ans = self._data["metacritic"]
        self._answer = {
            'value': ans, 'fmt': "(0|[1-9]\d|100)",
            'text': f'{ans} ist der Metascore von "{self._data["name"]}" https://store.steampowered.com/app/{self._data["id"]}',
            'reaction': '{} {} um {} vom richtigen Wert ab.'
        }

    def _get_game_release(self):
        self._question = f'An welchem Tag (TT.MM.JJJJ) erschien "{self._data["displayName"]}" auf Steam?'
        ans = germanize_date_string(self._data["release"])
        self._answer = {
            'value': ans, 'fmt': "\d\d\.\d\d\.\d\d\d\d",
            'text': f'Am {ans} erschien "{self._data["name"]}" https://store.steampowered.com/app/{self._data["id"]}',
            'reaction': '{} {} um {} Tag/e vom richtigen Datum ab.'
        }

    def _get_achievement(self):
        self._success = False
        params = {"key": STEAMAPI, "format": "json", "count": 5, "l": "german"}
        url_progress_achievements = 'https://api.steampowered.com/ISteamUserStats/GetGlobalAchievementPercentagesForApp/v0002/?'
        url_game_achievements = 'https://api.steampowered.com/ISteamUserStats/GetSchemaForGame/v2/?'
        while True:
            app = random.choice(steam_apps)
            params["gameid"] = app["appid"]
            achievement_progresses = get_dict_from_request(
                'https://api.steampowered.com/ISteamUserStats/GetGlobalAchievementPercentagesForApp/v0002/?', params)
            if achievement_progresses != None and "achievementpercentages" in achievement_progresses:
                break
        params["appid"] = app["appid"]
        achievement_datas = get_dict_from_request('https://api.steampowered.com/ISteamUserStats/GetSchemaForGame/v2/?',
                                               params)
        if achievement_datas is None:
            return None
        achievement_progresses = achievement_progresses["achievementpercentages"]["achievements"]
        game_name = achievement_datas["game"]["gameName"]
        try:
            achievement_datas = achievement_datas["game"]["availableGameStats"]["achievements"]
        except:
            return None
        self._success = True
        achievements = {}
        total_progress = 0
        max_percent, min_percent = -1, 101
        max_achievement, min_achievement = None, None
        for a in achievement_progresses:
            achievements[a["name"]] = {"percent": a["percent"]}
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
        total_completion = total_progress / len(achievements)
        rnd_achievement = get_random_key(achievements)
        self._data = {
            "leastName": achievements[min_achievement]["name"], "leastProgress": round(min_percent),
            "mostName": achievements[max_achievement]["name"], "mostProgress": round(max_percent),
            "completion": round(total_completion), "game": game_name,
            "rndName": achievements[rnd_achievement]["name"],
            "rndProgress": round(achievements[rnd_achievement]["percent"])
        }
        self._answer = {
            "fmt": "(0|[1-9]\d|100)",
            "reaction": "{} {} um {} Prozentpunkt/e vom richtigen Wert ab."
        }

    def _get_least_achievement(self):
        self._question = f'Wie viel Prozent (gerundet) der Spielenden von "{self._data["game"]}" haben die am seltesten erreichte Errungenschaft "{self._data["leastName"]}" im Spiel?'
        ans = round(self._data["leastProgress"])
        self._answer["text"] = f'{ans} % erreichten die Errungenschaft.'
        self._answer["value"] = ans

    def _get_most_achievement(self):
        self._question = f'Wie viel Prozent (gerundet) der Spielenden von "{self._data["game"]}" haben die am öftesten erreichte Errungenschaft "{self._data["mostName"]}" im Spiel?'
        ans = round(self._data["mostProgress"])
        self._answer["text"] = f'{ans} % erreichten die Errungenschaft.'
        self._answer["value"] = ans

    def _get_random_achievement(self):
        self._question = f'Wie viel Prozent (gerundet) der Spielenden von "{self._data["game"]}" haben die Steam-Errungenschaft "{self._data["rndName"]}"?'
        ans = round(self._data["rndProgress"])
        self._answer["text"] = f'{ans} % erreichten "{self._data["rndName"]}".'
        self._answer["value"] = ans

    def _get_achievement_completion(self):
        self._question = f'Wie hoch ist die durchschnittliche Komplettierungsquote (in Prozent, gerundet) der Errungenschaften von "{self._data["game"]}" wurden im Durchschnitt erreicht?'
        ans = round(self._data["completion"])
        self._answer["text"] = f'{ans} % aller Errungenschaften von "{self._data["game"]}" wurden erreicht.'
        self._answer["value"] = ans
