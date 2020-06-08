# /usr/bin/python
import glob
import importlib.util
from pathlib import Path

from APIHelpers import *


def generate_weighted_api_list(apis: dict) -> list:
    """ takes the weighted APIs and returns a list with the APIs in the given amount """
    api_weighted = []
    for api in apis:
        for i in range(apis[api]):
            api_weighted.append(api)
    return api_weighted


base_path = str(Path(__file__).parent)


class APILoader:
    def __init__(self, testing=False):
        # loading every class file _not_ beginning with API
        apis = [x for x in glob.glob(os.path.join(base_path, "*.py")) if "API" not in x]
        self._api_and_weight = {}
        # init the classes and get their weights
        for api in apis:
            module_name = api[len(base_path) + 1:]
            spec = importlib.util.spec_from_file_location(module_name, api)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            api_loader = getattr(module, module_name[:-3])
            self._api_and_weight[api_loader] = api_loader().get_weight()
            if testing:
                api = api_loader()
                api.test_api()
        self._apis_weighted = []

    def __call__(self):
        if len(self._apis_weighted) == 0:
            # init a dict with new weighted APIs
            self._apis_weighted = generate_weighted_api_list(self._api_and_weight)
        # get a random API and remove it from the list
        random_api = random.randint(0, len(self._apis_weighted) - 1)
        print("Category:", str(self._apis_weighted[random_api]).split(".")[-1][:-2])
        api_instance = self._apis_weighted[random_api]()
        api_instance.set_random_qa()
        del self._apis_weighted[random_api]
        qa = False
        while not qa:
            qa = api_instance()
        return qa
