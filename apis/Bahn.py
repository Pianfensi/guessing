# /usr/bin/pianfensi
from API import *


class Bahn(API):
    def __init__(self):
        self._categories = {
            "arrivals": {
                "method": self._get_arrival,
                "questionTypes": {
                    "time": self._get_arrival_time,
                    "track": self._get_arrival_track,
                    "train": self._get_arrival_train
                }
            }
        }
        API.__init__(self)

    def _get_station(self):
        self._headers = {"Accept": "application/json", "Authorization": "Bearer " + BAHNTOKEN}
        while True:
            while True:
                url = "https://api.deutschebahn.com/fahrplan-plus/v1/location/"
                results = get_dict_from_request(url + chr(random.randint(65, 91)), headers=self._headers)
                if "error" not in results:
                    break
            station = random.choice(results)
            self._data = {
                "id": station["id"]
            }
            url = "https://api.deutschebahn.com/fahrplan-plus/v1/arrivalBoard/" + str(self._data["id"]) + "?"
            params = {"date": time_to_string(time.time())[:-1]}
            arrivals = get_dict_from_request(url, params=params, headers=self._headers)
            if len(arrivals) > 0 and "error" not in arrivals:
                break
        self._data["arrivals"] = arrivals
        self._success = True

    def _get_arrival(self):
        self._get_station()
        train = random.choice(self._data["arrivals"])
        timestamp = string_to_time(train["dateTime"] + ":00Z")
        train_date, train_time = train["dateTime"].split("T")
        train_date = germanize_date_string(train_date)
        past = (time.time() > timestamp)
        self._data.update({
            "name": train["name"], "origin": train["origin"], "stopName": train["stopName"],
            "date": train_date, "time": train_time, "past": past, "track": None,
            "type": train["type"]
        })
        if "track" in train:
            self._data["track"] = int(re.sub(" [\w\/]+", "", train["track"]))

    def _get_arrival_time(self):
        self._question = f'Um welche Uhrzeit ([H]H:MM) {"fuhr" if self._data["past"] else "fährt"} der {self._data["name"]} von {self._data["origin"]} in {self._data["stopName"]} am {self._data["date"]} ein?'
        ans = self._data["time"]
        self._answer = {
            "value": ans, "fmt": "(\d|[01]\d|2[0-3]):[0-5]\d",
            "text": f'{ans} Uhr {"fuhr" if self._data["past"] else "fährt"} er ein.',
            "reaction": "{} {} um {} Minute/n von der richtigen Zeit ab."
        }

    def _get_arrival_track(self):
        self._question = f'Auf welchem Gleis {"fuhr" if self._data["past"] else "fährt"} der {self._data["name"]} von {self._data["origin"]} in {self._data["stopName"]} am {self._data["date"]} ein?'
        ans = self._data["track"]
        self._answer = {
            "value": ans, "fmt": "\d+",
            "text": f'Auf Gleis {ans} {"fuhr" if self._data["past"] else "fährt"} er ein.',
            "reaction": "{} {} um {} vom richtigen Wert ab."
        }

    def _get_arrival_train(self):
        self._question = f'Welche Nummer hat der {self._data["type"]} aus {self._data["origin"]}, der am {self._data["date"]} um {self._data["time"]} Uhr {self._data["stopName"]} erreicht{"e" if self._data["past"] else ""}?'
        ans = int(re.sub("^[\w/]+ ", "", self._data["name"]))
        self._answer = {
            "value": ans, "fmt": "\d+",
            "text": f'{self._data["name"]} heißt der Zug.',
            "reaction": "{} {} um {} vom richtigen Wert ab."
        }
