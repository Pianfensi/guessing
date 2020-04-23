# guessing questions
Project written in Python 3.7 for reading several APIs to generate guessing questions (in german)
# How does it work?
The file "APIKeys.py" includes all the necessary authentification keys of the API services, so you have to include your owns.
The file "APIHelpers.py" includes several functions and helps to update some databases.
The folder "databases" includes static helper jsons for localizing country names or reduce the amount of API requests by updating on a daily base.
The class API is the super class of all the API classes for Steam, Twitch, Pokemon, ...
The class APILoader reads all the .py files (not beginning with API) that includes the API classes. With the method APILoader.getQA() you'll get a tuple with a random question and an answer dictionary:
  - "value"
  - "fmt" for a regex check whether an user answer is valid
  - "text" for a convenient solution
  - "reaction" which I used for my Twitch chat so that you can give a feedback for user answers, there are three placeholders: username(s), verb (in german for plural cases), distance to the exact value
# How to build your own API
Just use one of the used APIs (like Area) and save the class file in the same folder, APILoader handles the rest.
# Known issues
Their is no 100 % guarantee for not crashing right now because of several infinite loops that may go on forever.
# Credits
All creators of the used APIs
https://github.com/umpirsky/country-list (for localized countries)
http://bulk.openweathermap.org/sample/ (for making it possible to have kind of a random way to get a city in the world)
