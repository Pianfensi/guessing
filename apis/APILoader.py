#/usr/bin/python
import glob, importlib.util
from pathlib import Path

from APIHelpers import *

base_path = str(Path(__file__).parent)
class APILoader:
	def __init__(self, testing=False):
		# loading every class file _not_ beginning with API
		apis = [x for x in glob.glob(os.path.join(base_path, "*.py")) if "API" not in x]
		self.__api_and_weight = {}
		# init the classes and get their weights
		for api in apis:
			module_name = api[len(base_path)+1:]
			spec = importlib.util.spec_from_file_location(module_name, api)
			module = importlib.util.module_from_spec(spec)
			spec.loader.exec_module(module)
			api_loader = getattr(module, module_name[:-3])
			self.__api_and_weight[api_loader] = api_loader().getWeight()
			if testing:
				api = api_loader()
				api.testAPI()
		self.__apis_weighted = []
	def getQA(self):
		if len(self.__apis_weighted) == 0:
			# init a dict with new weighted apis
			self.__apis_weighted = apisWeighted(self.__api_and_weight)
		# get a random api and remove it from the dict
		random_api = random.randint(0, len(self.__apis_weighted)-1)
		print("Category:", self.__apis_weighted[random_api])
		api_instance = self.__apis_weighted[random_api]()
		api_instance.setRandomQA()
		del self.__apis_weighted[random_api]
		
		qa = False
		while not qa:
			qa = api_instance.getQA()
		return qa