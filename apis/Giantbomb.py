#/usr/bin/python
from API import *
class Giantbomb(API):
	def __init__(self, test=False):
		self._categories = {
			"companies" : {
				"method" : self.__getCompany,
				"questionTypes" : {
					"founded" : self.__getCompanyFounded,
					"developed" : self.__getCompanyDeveloped,
					"published" : self.__getCompanyPublished
				}
			}
		}
		API.__init__(self, test=test)
	def __getCompany(self):
		url = "https://www.giantbomb.com/api/companies/?"
		headers = {"User-Agent" : "https://webdebut.net"}
		params = {"api_key" : GIANTBOMBKEY, "format" : "json", "limit" : 1, "offset" : random.randint(0,100)}
		results = reqToDict(url, params=params, headers=headers)
		if results["status_code"] != 1:
			return 0
		result = results["results"][0]
		company_url = f'https://www.giantbomb.com/api/company/{result["guid"]}/?'
		company_params = {"api_key" : GIANTBOMBKEY, "format" : "json"}
		result = reqToDict(company_url, params=company_params, headers=headers)
		if result["status_code"] != 1:
			return 0
		self._success = True
		company_data = result["results"]
		self._data = {
			"name" : company_data["name"], "founded" : company_data["date_founded"],
			"developed" : len(company_data["developed_games"]), "published" : len(company_data["published_games"]),
			"website" : company_data["site_detail_url"]
		}
	def __getCompanyFounded(self):
		self._question = f'In welchem Jahr wurde das Spieleunternehmen {self._data["name"]} gegründet?'
		ans = int(self._data["founded"][:4])
		self._answer = {
			"value" : ans, "fmt" : "\d{4}",
			"text" : f'{ans} wurde {self._data["name"]} gegründet.',
			"reaction" : "{} {} um {} Jahr/e von richtigen Jahr ab."
		}
	def __getCompanyDeveloped(self):
		self._question = f'Wie viele Spiele hat das Spieleunternehmen {self._data["name"]} laut Giantbomb entwickelt?'
		ans = self._data["developed"]
		self._answer = {
			"value" : ans, "fmt" : "\d+",
			"text" : f'{ans} Spiel{"" if ans == 1 else "e"} hat {self._data["website"]} entwickelt.',
			"reaction" : "{} {} um {} vom richtigen Wert ab."
		}
	def __getCompanyPublished(self):
		self._question = f'Wie viele Spiele hat das Spieleunternehmen {self._data["name"]} laut Giantbomb veröffentlicht?'
		ans = self._data["published"]
		self._answer = {
			"value" : ans, "fmt" : "\d+",
			"text" : f'{ans} Spiel{"" if ans == 1 else "e"} hat {self._data["website"]} veröffentlicht.',
			"reaction" : "{} {} um {} vom richtigen Wert ab."
		}
