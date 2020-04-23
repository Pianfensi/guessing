#/usr/bin/python
from APIHelpers import *

class API:
	def __init__(self, test=False):
		self._success = False
		self._data = None
		self._test = test
		self._weight = None
		self._weight = self.getWeight()
	def generate(self):
		if self._test:
			self._testAPI()
		else:
			self._randomQA()
	def getQA(self):
		if self._success:
			return self._question, self._answer
		return False
	def getWeight(self):
		if self._weight == None:
			self._weight = 0
			for category in self._categories.keys():
				if "questionTypes" in self._categories[category]:
					for question_type in self._categories[category]["questionTypes"].keys():
						self._weight += 1
				else:
					self._weight += 1
		return self._weight
	def _randomQA(self):
		category = randomKey(self._categories)
		while not self._success:
			self._categories[category]["method"]()
		while True:
			if len(self._categories[category]["questionTypes"]) == 0:
				self._success = False
				return 0
			question_type = randomKey(self._categories[category]["questionTypes"])
			if question_type in self._data and self._data[question_type] == None:
				del self._categories[category]["questionTypes"][question_type]
				continue
			break
		self._categories[category]["questionTypes"][question_type]()
	def _testAPI(self):
		for category, methods in self._categories.items():
			methods["method"]()
			if self._success:
				for question_type, method in methods["questionTypes"].items():
					if question_type not in self._data or self._data[question_type] != None:
						method()
						q, a = self.getQA()
						print(q)
						printdict(a)
				self._success = False