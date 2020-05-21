#/usr/bin/python
import requests, datetime, time, json, urllib, re, random, os

from math import *
from pathlib import Path

from APIKeys import *

base_path = Path(__file__).parent

class XmlListConfig(list):
	def __init__(self, aList):
		for element in aList:
			if element:
				# treat like dict
				if len(element) == 1 or element[0].tag != element[1].tag:
					self.append(XmlDictConfig(element))
				# treat like list
				elif element[0].tag == element[1].tag:
					self.append(XmlListConfig(element))
			elif element.text:
				text = element.text.strip()
				if text:
					self.append(text)


class XmlDictConfig(dict):
	'''
	Example usage:

	>>> tree = ElementTree.parse('your_file.xml')
	>>> root = tree.getroot()
	>>> xmldict = XmlDictConfig(root)

	Or, if you want to use an XML string:

	>>> root = ElementTree.XML(xml_string)
	>>> xmldict = XmlDictConfig(root)

	And then use xmldict for what it is... a dict.
	'''
	def __init__(self, parent_element):
		if parent_element.items():
			self.update(dict(parent_element.items()))
		for element in parent_element:
			if element:
				# treat like dict - we assume that if the first two tags
				# in a series are different, then they are all different.
				if len(element) == 1 or element[0].tag != element[1].tag:
					aDict = XmlDictConfig(element)
				# treat like list - we assume that if the first two tags
				# in a series are the same, then the rest are the same.
				else:
					# here, we put the list in dictionary; the key is the
					# tag name the list elements all share in common, and
					# the value is the list itself 
					aDict = {element[0].tag: XmlListConfig(element)}
				# if the tag has attributes, add those to the dict
				if element.items():
					aDict.update(dict(element.items()))
				self.update({element.tag: aDict})
			# this assumes that if you've got an attribute in a tag,
			# you won't be having any text. This may or may not be a 
			# good idea -- time will tell. It works for the way we are
			# currently doing XML configuration files...
			elif element.items():
				if element.tag in self:
					if isinstance(self[element.tag], dict):
						self[element.tag] = [self[element.tag]]
					self[element.tag].append(dict(element.items()))
				else:
					self.update({element.tag: dict(element.items())})
			# finally, if there are no child tags and no attributes, extract
			# the text
			else:
				self.update({element.tag: element.text})

def reqToDict(url, params={}, o=False, headers={}):
	r = requests.get(f'{url}{urllib.parse.urlencode(params)}', headers=headers)
	try:
		rjson = json.loads(r.text)
		if o:
			printdict(rjson)
		return rjson
	except:
		return None
def calcAge(ymd):
	current_time = time.localtime(time.time())
	current_year = current_time[0]
	current_month = current_time[1]
	current_day = current_time[2]
	if re.match("^\d{4}-\d{2}-\d{2}$", ymd):
		target_year, target_month, target_day = tuple([int(x) for x in ymd.split("-")])
		age = current_year - target_year
		if (current_month < target_month) or (current_month == target_month and current_day < target_day):
			age -= 1
		return age
	return None
def printdict(d):
	print(json.dumps(d, indent=4, sort_keys=True))
def strtotime(s):
	timecode = datetime.datetime.strptime(s.replace(".000", ""), "%Y-%m-%dT%H:%M:%SZ")
	return int((timecode - datetime.datetime.utcfromtimestamp(0)).total_seconds())
def ageindays(s):
	age = time.time()-strtotime(s)
	conversion = 24*3600
	return int(age//conversion)
def dmy(s):
	return f'{s[8:10]}.{s[5:7]}.{s[:4]}'
def yttosec(s):
	l = re.split("[A-Z]+", s)
	l = l[::-1][1:-1]
	sec = sum([int(l[i])*60**i for i in range(len(l))])
	return sec
def numWithSeps(n):
	if n == None:
		return None
	return "{:,}".format(n).replace(",", ".")
def steamymd(s):
	months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
	monthdict = {}
	datelist = s.split(" ")
	for i in range(len(months)):
		monthdict[months[i] + ","] = f'{i+1:02}'
	try:
		return f'{datelist[2]}-{monthdict[datelist[1]]}-{int(datelist[0]):02}'
	except:
		return None
def floatChic(f):
	if isinstance(f, float):
		return "{:.2f}".format(f).replace(".", ",")
	return numWithSeps(f)
def timetostr(t):
	time_tuple = time.localtime(t)
	return f'{time_tuple[0]}-{time_tuple[1]:02}-{time_tuple[2]:02}T{time_tuple[3]:02}:{time_tuple[4]:02}:{time_tuple[5]:02}Z'
def apisWeighted(apis):
	api_weighted = []
	for api in apis:
		for i in range(apis[api]):
			api_weighted.append(api)
	return api_weighted
def randomToken():
	chars = [chr(i) for i in range(65,91)] + [str(i) for i in range(10)]
	token = ""
	for i in range(32):
		c = random.choice(chars)
		if random.randint(0,1):
			token += c.lower()
		else:
			token += c
	return token
def randomKey(d):
	return random.choice(list(d.keys()))
def hav(phi):
	return sin(phi/2)**2
def earthDistance(lat1, lon1, lat2, lon2):
	RADIUS = 6371
	lat1 = radians(lat1)
	lon1 = radians(lon1)
	lat2 = radians(lat2)
	lon2 = radians(lon2)
	delta_lat = lat1-lat2
	delta_lon = lon1-lon2
	return 2*RADIUS*asin(sqrt(hav(delta_lat)+cos(lat1)*cos(lat2)*hav(delta_lon)))


# daily save of an offline version of all steamapp ids
steamapps_path = os.path.join(base_path, "databases", "steamapps.json")
if os.path.getmtime(steamapps_path) < time.time()-24*3600:
	steam_apps = reqToDict('https://api.steampowered.com/ISteamApps/GetAppList/v2/?', {"key" : STEAMAPI, "format" : "json", "count" : 5})["applist"]["apps"]
	if len(steam_apps) > 0:
		with open(steamapps_path, "w") as f:
			f.write(json.dumps(steam_apps))
with open(steamapps_path, encoding="utf-8") as f:
	steam_apps = json.loads(f.read())

# daily save of an offline version of the fixer api
fixer_path = os.path.join(base_path, "databases", "fixer.json")
if os.path.getmtime(fixer_path) < time.time()-24*3600:
	exchange_rates = reqToDict("http://data.fixer.io/api/latest?", {"access_key" : FIXERKEY})["rates"]
	del exchange_rates["EUR"]
	with open(fixer_path, "w") as f:
		f.write(json.dumps(exchange_rates))
with open(fixer_path) as f:
	exchange_rates = json.loads(f.read())

# ready countries and currencies data
countries_path = os.path.join(base_path, "databases", "countries.json")
with open(countries_path, encoding="utf-8") as f:
	countryjson = json.loads(f.read())
countries = {}
langs = {
	'cs' : "tschechisch ", 'tr' : "türkisch", 'ko' : "koreanisch", 
	'en' : "englisch", 'fr' : "französisch", 'pl' : "polnisch", 
	'es' : "spanisch", 'pt' : "portugiesisch", 'jp' : "japanisch", 
	'ru' : "russisch", 'de' : "deutsch", 'th' : "thailändisch", 
	'it' : "italienisch", 'nl' : "niederländisch", 'da' : "dänisch"
}
currencies = {}
localization_path = os.path.join(base_path, "databases", "localized_countries.json")
with open(localization_path, encoding="utf-8") as f:
	localization = json.loads(f.read())
for country in countryjson:
	countries[country["Alpha2Code"]] = [localization[country["Alpha2Code"]] if country["Alpha2Code"] in localization else country["Name"], country["Area"]]
	currencies[country["CurrencyCode"]] = [country["CurrencyName"], country["CurrencySymbol"]]
cityids_path = os.path.join(base_path, "databases", "cityids.json")
with open(cityids_path, encoding="utf-8") as f:
	cities = json.loads(f.read())