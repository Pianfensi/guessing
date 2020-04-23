#/usr/bin/python
import glob, importlib.util
from pathlib import Path

from APIHelpers import *

base_path = str(Path(__file__).parent)
class APILoader:
	def __init__(self):
		apis = [x for x in glob.glob(os.path.join(base_path, "*.py")) if "API" not in x]
		self.__api_and_weight = {}
		for api in apis:
			module_name = api[len(base_path)+1:]
			spec = importlib.util.spec_from_file_location(module_name, api)
			module = importlib.util.module_from_spec(spec)
			spec.loader.exec_module(module)
			api_loader = getattr(module, module_name[:-3])
			self.__api_and_weight[api_loader] = api_loader().getWeight()
		self.__apis_weighted = []
	def getQA(self):
		if len(self.__apis_weighted) == 0:
			self.__apis_weighted = apisWeighted(self.__api_and_weight)
		random_api = random.randint(0, len(self.__apis_weighted)-1)
		print("Category:", self.__apis_weighted[random_api])
		api_instance = self.__apis_weighted[random_api]()
		api_instance.generate()
		del self.__apis_weighted[random_api]
		qa = False
		while not qa:
			qa = api_instance.getQA()
		return qa