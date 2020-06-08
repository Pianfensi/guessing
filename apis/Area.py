# /usr/bin/python
from API import *


class Area(API):
    def __init__(self):
        self._categories = {
            "areas": {
                "method": self._get_area,
                "questionTypes": {
                    "countries": self._get_area_of_country
                }
            }
        }
        API.__init__(self)

    def _get_area(self):
        self._data = countries[get_random_key(countries)]
        self._success = True

    def _get_area_of_country(self):
        self._question = f'Wie groß ist {self._data[0]} in km²?'
        ans = self._data[1]
        self._answer = {
            'value': ans, 'fmt': "\d+",
            'text': f'{seperate_in_thousands(ans)} km² ist {self._data[0]} groß.',
            'reaction': '{} {} um {} km² vom richtigen Wert ab.'
        }
