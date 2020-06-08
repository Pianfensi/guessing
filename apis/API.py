# /usr/bin/python
from APIHelpers import *


class API:
    def __init__(self):
        self._success = False
        self._data = None
        self._weight = None
        self._weight = self.get_weight()

    def __call__(self):
        if self._success:
            return self._question, self._answer
        return False

    def get_weight(self):
        if self._weight is None:
            self._weight = 0
            for category in self._categories.keys():
                if "questionTypes" in self._categories[category]:
                    for question_type in self._categories[category]["questionTypes"].keys():
                        self._weight += 1
                else:
                    self._weight += 1
        return self._weight

    def set_random_qa(self):
        category = get_random_key(self._categories)
        while not self._success:
            self._categories[category]["method"]()
        while True:
            if len(self._categories[category]["questionTypes"]) == 0:
                self._success = False
                return None
            question_type = get_random_key(self._categories[category]["questionTypes"])
            if question_type in self._data and self._data[question_type] is None:
                del self._categories[category]["questionTypes"][question_type]
                continue
            break
        self._categories[category]["questionTypes"][question_type]()

    def test_api(self):
        for category, methods in self._categories.items():
            methods["method"]()
            if self._success:
                for question_type, method in methods["questionTypes"].items():
                    if question_type not in self._data or self._data[question_type] != None:
                        method()
                        q, a = self()
                        print(q)
                        print_dict(a)
                self._success = False
