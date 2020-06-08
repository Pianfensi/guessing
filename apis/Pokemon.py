# /usr/bin/python
from API import *


class Pokemon(API):
    def __init__(self):
        self._categories = {
            "pokemons": {
                "method": self._get_pokemon,
                "questionTypes": {
                    "height": self._get_pokemon_height,
                    "weight": self._get_pokemon_weight,
                    "number": self._get_pokemon_number
                }
            }
        }
        API.__init__(self)

    def _get_pokemon(self):
        poke_id = random.randint(1, 251)  # first and second generations
        species = get_dict_from_request(f'https://pokeapi.co/api/v2/pokemon-species/{poke_id}')
        stats = get_dict_from_request(f'https://pokeapi.co/api/v2/pokemon/{poke_id}')
        if species is None or stats is None:
            return None
        self._success = True
        for lang in species["names"]:
            if lang["language"]["name"] == "de":
                name = lang["name"]
        self._data = {
            "no": poke_id, "name": name, "height": stats["height"] / 10, "weight": stats["weight"] / 10
        }

    def _get_pokemon_height(self):
        self._question = f'Wie viel Meter (auf eine Nachkommastelle genau) ist das Pokémon {self._data["name"]} groß?'
        ans = self._data["height"]
        self._answer = {
            "value": ans, "fmt": "\d+([,\.]\d)?",
            "text": f'{germanize_number(ans)} m ist {self._data["name"]} groß.',
            "reaction": "{} {} um {} m von dem richtigen Wert ab."
        }

    def _get_pokemon_weight(self):
        self._question = f'Wie viel Kilogramm (auf eine Nachkommastelle genau) wiegt das Pokémon {self._data["name"]}?'
        ans = self._data["weight"]
        self._answer = {
            "value": ans, "fmt": "\d+([,\.]\d)?",
            "text": f'{germanize_number(ans)} kg wiegt {self._data["name"]}.',
            "reaction": "{} {} um {} kg von dem richtigen Wert ab."
        }

    def _get_pokemon_number(self):
        self._question = f'Welche Nummer hat das Pokémon {self._data["name"]} im NationalDex?'
        ans = self._data["no"]
        self._answer = {
            "value": ans, "fmt": "\d+",
            "text": f'{ans} ist die Nummer von {self._data["name"]}.',
            "reaction": "{} {} um {} von der richtigen Nummer ab."
        }
