# /usr/bin/python
from API import *


class Fixer(API):
    def __init__(self):
        self._categories = {
            "rates": {
                "method": self._get_rate,
                "questionTypes": {
                    "eurrate": self._get_rate_to_Euro
                }
            }
        }
        API.__init__(self)

    def _get_rate(self):
        target_currency = get_random_key(exchange_rates)
        self._data = {
            "rate": exchange_rates[target_currency], "name": currencies[target_currency][0],
            "symbol": currencies[target_currency][1]
        }
        self._success = True

    def _get_rate_to_Euro(self):
        self._question = f'Wie viel sind 100 € in {self._data["name"]} {self._data["symbol"]} (abgerundet auf ganze) wert?'
        ans = int(self._data["rate"] * 100)
        self._answer = {
            "value": ans, "fmt": "\d+",
            "text": f'{germanize_number(ans)} {self._data["symbol"]} gibt es für 100 €.',
            "reaction": '{} {} um {} ' + self._data["symbol"] + ' vom richtigen Wert ab.'
        }
