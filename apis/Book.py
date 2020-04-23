#/usr/bin/python
from API import *

class Book(API):
	def __init__(self, test=False):
		self._categories = {
			"books" : {
				"method" : self.__getBook,
				"questionTypes" : {
					"pages" : self.__getBookPages,
					"published" : self.__getPublishedOfBook
				}
			}
		}
		API.__init__(self, test=test)
	def __getBook(self):
		categories = ["erotic", "manga", "anime", "cats", "dogs", "animals", "computer", "science", "math", "history", "sports", "biology", "politics", "magic", "games", "chemistry", "physics", "drama", "comedy", "fiction", "fantasy", "horror", "crime", "people", "flower"]
		url = "https://www.googleapis.com/books/v1/volumes?"
		while True:
			params = {"key" : GOOGLEKEY, "langRestrict" : "de", "orderBy" : "relevance", "printType": "books", "q" : f"subject:{random.choice(categories)}", "maxResults" : 40}
			books = reqToDict(url, params=params)
			if books == None:
				return 0
			if "items" in books:
				break
			else:
				print("No success on category: ", params["q"])
		self._success = True
		book = random.choice(books["items"])["volumeInfo"]
		self._data = {
			"name" : book["title"] + ("" if "subtitle" not in book else f' - {book["subtitle"]}'),
			"pages" : None, "published" : int(book["publishedDate"][:4]),
			"author" : None
		}
		if "pageCount" in book:
			self._data["pages"] = book["pageCount"]
		if "authors" in book:
			self._data["author"] = book["authors"][0]
	def __getBookPages(self):
		self._question = f'Wie viele Seiten hat das Buch "{self._data["name"]}"{" von " + self._data["author"] if self._data["author"] != None else ""}?'
		ans = self._data["pages"]
		self._answer = {
			"value" : ans, "fmt" : "\d+",
			"text" : f'{numWithSeps(ans)} Seiten hat das Buch {self._data["name"]}.',
			"reaction" : "{} {} um {} Seite/n vom richtigen Wert ab."
		}
	def __getPublishedOfBook(self):
		self._question = f'In welchem Jahr erschien das Buch "{self._data["name"]}"{" von " + self._data["author"] if self._data["author"] != None else ""}?'
		ans = self._data["published"]
		self._answer = {
			"value" : ans, "fmt" : "\d+",
			"text" : f'{ans} erschien das Buch {self._data["name"]}.',
			"reaction" : "{} {} um {} Jahr/e vom richtigen Wert ab."
		}
