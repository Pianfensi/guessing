#/usr/bin/python
from API import *

class TMDB(API):
	def __init__(self):
		self._categories = {
			"movies" : {
				"method" : self.__getMovie,
				"questionTypes" : {
					"release" : self.__getMovieRelease,
					"budget" : self.__getMovieBudget,
					"box-office" : self.__getMovieBoxOffice,
					"duration" : self.__getMovieDuration,
					"score" : self.__getMovieScore
				}
			},
			"series" : {
				"method" : self.__getSeries,
				"questionTypes" : {
					"start" : self.__getSeriesStart,
					"last_episode" : self.__getSeriesLastEpisode,
					"episodes" : self.__getSeriesEpisodes,
					"seasons" : self.__getSeriesSeasons
				}
			},
			"celebs" : {
				"method" : self.__getCeleb,
				"questionTypes" : {
					"age" : self.__getCelebAge
				}
			}
		}
		API.__init__(self)
	def __getMovie(self):
		src = random.choice(["popular", "top_rated"])
		url = f"https://api.themoviedb.org/3/movie/{src}?"
		params = {"api_key" : TMDBKEY, "language" : "de", "page" : random.randint(1,100)}
		movies = reqToDict(url, params=params)
		if movies == None or "results" not in movies or len(movies["results"]) == 0:
			return 0
		movies = movies["results"]
		movie = random.choice(movies)
		movie_url = f'https://api.themoviedb.org/3/movie/{movie["id"]}?'
		movie_params = {"api_key" : TMDBKEY, "language" : "de"}
		movie_data = reqToDict(movie_url, params=movie_params)
		if movie_data == None:
			return 0
		self._success = True
		self._data = {
			"id" : movie["id"], "name" : movie["title"], "release" : int(movie["release_date"][:4]),
			"budget" : None, "box-office" : None, "duration" : movie_data["runtime"],
			"score" : None
		}
		if movie_data["budget"] > 0:
			self._data["budget"] = movie_data["budget"]
		if movie_data["revenue"] > 0:
			self._data["box-office"] = movie_data["revenue"]
		if movie_data["vote_average"] > 0:
			self._data["score"] = int(movie_data["vote_average"]*10)
	def __getMovieRelease(self):
		self._question = f'In welchem Jahr erschien der Film "{self._data["name"]}"?'
		ans = self._data["release"]
		self._answer = {
			"value" : ans, "fmt" : "\d{4}",
			"text" : f'{ans} erschien "{self._data["name"]}" https://www.themoviedb.org/movie/{self._data["id"]}',
			"reaction" : "{} {} um {} Jahr/e vom richtigen Wert ab."
		}
	def __getMovieBudget(self):
		self._question = f'Wie hoch war das Budget (in USD) für den Film "{self._data["name"]}"?'
		ans = self._data["budget"]
		self._answer = {
			"value" : ans, "fmt" : "\d+",
			"text" : f'{ans} USD kostete "{self._data["name"]}" https://www.themoviedb.org/movie/{self._data["id"]}',
			"reaction" : "{} {} um {} USD vom richtigen Wert ab."
		}
	def __getMovieBoxOffice(self):
		self._question = f'Wie hoch war das Box-Office-Ergebnis (in USD) für den Film "{self._data["name"]}"?'
		self._answer = {
			"value" : self._data["box-office"], "fmt" : "\d+",
			"text" : f'{numWithSeps(self._data["box-office"])} USD brachte "{self._data["name"]}" https://www.themoviedb.org/movie/{self._data["id"]} ein.',
			"reaction" : "{} {} um {} USD vom richtigen Wert ab."
		}
	def __getMovieDuration(self):
		self._question = f'Wie viele Minuten geht der Film "{self._data["name"]}"?'
		self._answer = {
			"value" : self._data["duration"], "fmt" : "\d+",
			"text" : f'{self._data["duration"]} Minuten läuft "{self._data["name"]}" https://www.themoviedb.org/movie/{self._data["id"]}',
			"reaction" : "{} {} um {} Minute/n vom richtigen Wert ab."
		}
	def __getMovieScore(self):
		self._question = f'Wie hoch ist die Benutzerwertung vom Film "{self._data["name"]}" ({self._data["release"]}) auf tmdb (in Prozent)?'
		self._answer = {
			"value" : self._data["score"], "fmt" : "(0|[1-9]\d|100)",
			"text" : f'{self._data["score"]} % erhielt "{self._data["name"]}" https://www.themoviedb.org/movie/{self._data["id"]}',
			"reaction" : "{} {} um {} Prozentpunkt/e vom richtigen Wert ab."
		}
	def __getSeries(self):
		src = random.choice(["popular", "top_rated"])
		url = f"https://api.themoviedb.org/3/tv/{src}?"
		params = {"api_key" : TMDBKEY, "language" : "de", "page" : random.randint(1,100)}
		shows = reqToDict(url, params=params)
		if shows == None or "results" not in shows or len(shows["results"]) == 0:
			return 0
		shows = shows["results"]
		show = random.choice(shows)
		show_url = f'https://api.themoviedb.org/3/tv/{show["id"]}?'
		show_params = {"api_key" : TMDBKEY, "language" : "de"}
		show_data = reqToDict(show_url, params=show_params)
		if show_data == None:
			return 0
		self._success = True
		self._data = {
			"id" : show["id"], "name" : show["name"], "start" : int(show_data["first_air_date"][:4]),
			"last_episode" : int(show_data["last_air_date"][:4]), "seasons" : show_data["number_of_seasons"],
			"episodes" : show_data["number_of_episodes"]
		}
	def __getSeriesStart(self):
		self._question = f'In welchem Jahr lief erstmals die Serie/Show "{self._data["name"]}"?'
		self._answer = {
			"value" : self._data["start"], "fmt" : "\d{4}",
			"text" : f'{self._data["start"]} lief erstmals "{self._data["name"]}" https://www.themoviedb.org/tv/{self._data["id"]}',
			"reaction" : "{} {} um {} Jahr/e vom richtigen Wert ab."
		}
	def __getSeriesLastEpisode(self):
		self._question = f'In welchem Jahr lief zuletzt die Serie/Show "{self._data["name"]}"?'
		self._answer = {
			"value" : self._data["last_episode"], "fmt" : "\d{4}",
			"text" : f'{self._data["last_episode"]} lief zuletzt "{self._data["name"]}" https://www.themoviedb.org/tv/{self._data["id"]}',
			"reaction" : "{} {} um {} Jahr/e vom richtigen Wert ab."
		}
	def __getSeriesEpisodes(self):
		self._question = f'Wie viele Episoden hat die Serie/Show "{self._data["name"]}"?'
		self._answer = {
			"value" : self._data["episodes"], "fmt" : "\d+",
			"text" : f'{self._data["episodes"]} Episode{"n" if self._data["episodes"] > 1 else ""} gibt es von "{self._data["name"]}" https://www.themoviedb.org/tv/{self._data["id"]}',
			"reaction" : "{} {} um {} vom richtigen Wert ab."
		}
	def __getSeriesSeasons(self):
		self._question = f'Wie viele Staffeln hat die Serie/Show "{self._data["name"]}"?'
		self._answer = {
			"value" : self._data["seasons"], "fmt" : "\d+",
			"text" : f'{self._data["seasons"]} Staffel{"" if self._data["seasons"] == 1 else "n"} gibt es von "{self._data["name"]}" https://www.themoviedb.org/tv/{self._data["id"]}',
			"reaction" : "{} {} um {} vom richtigen Wert ab."
		}
	def __getCeleb(self):
		url = 'https://api.themoviedb.org/3/person/popular?'
		params = {"api_key" : TMDBKEY, "language" : "en", "page" : random.randint(1,20)}
		persons = reqToDict(f'https://api.themoviedb.org/3/person/popular?', {"api_key" : TMDBKEY, "language" : "en", "page" : random.randint(1,20)})
		if persons == None or "results" not in persons:
			return 0
		persons = persons["results"]
		person = random.choice(persons)
		person_url = f'https://api.themoviedb.org/3/person/{person["id"]}?'
		person_params = {"api_key" : TMDBKEY, "language" : "en"}
		person_data = reqToDict(person_url, params=person_params)
		if person_data == None:
			return 0
		self._success = True
		self._data = {
			"id" : person["id"], "name" : person_data["name"], "birthPlace" : person_data["place_of_birth"], "age" : None
		}
		if "birthday" in person_data and re.match("^\d{4}-\d{2}-\d{2}$", person_data["birthday"]):
			self._data["age"] = calcAge(person_data["birthday"])
	def __getCelebAge(self):
		self._question = f'Wie alt ist {self._data["name"]} (* {self._data["birthPlace"]})?'
		ans = self._data["age"]
		self._answer = {
			"value" : ans, "fmt" : "\d+",
			"text" : f'{ans} Jahre ist {self._data["name"]} https://www.themoviedb.org/person/{self._data["id"]} alt.',
			"reaction" : "{} {} um {} Jahr/e vom richtigen Alter ab."
		}
	def test(self):
		self.__getMovie()

t = TMDB()
t.test()