from urllib.request import urlopen
from urllib.request import Request
from bs4 import BeautifulSoup as soup
import pandas as pd
import random
from datetime import datetime
from multiprocessing import pool
#from recipeManager import addRecipe
import logging
import pickle
import os

"""
@Author: Jakob Endler
"""


# Instantiating the Logger and the File Handler
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.FileHandler('data/log.txt')
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

CHEFKOCH_LINK = "https://www.chefkoch.de/rs/s0/Rezepte.html"

SAMPLE_RECIPE = "https://www.chefkoch.de/rezepte/2293561365672708/Gulaschsuppe-im-Kessel-oder-Topf.html"

def getRawData(url, useragent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:67.0) Gecko/20100101 Firefox/67.0'):
	"""returns a bs4.soup-Object of the given url
    @Params: 
        url: a string-url for a HLTV-Match page
		useragent: a string-useragent for the request
    @returns a bs4.soup-Object
	"""

	# User Agent Mozilla to Circumvent Security Blocking
	req = Request(url, headers={'User-Agent': useragent})

	# If using a proxy, define a .env file with the following content:
	# http_proxy=http://<proxy>:<port>
	
	# Also, when running with poetry, use this command to install support for .env files:
	# poetry self add poetry-dotenv-plugin

	# Connect and Save the HTML Page
	uClient = urlopen(req)
	page_html = uClient.read()
	uClient.close()

	# Parse HTML
	page_soup = soup(page_html, "html.parser")
	return page_soup

def findRezeptLinks(page_soup):
	"""returns a list of all links to recipes on the given page

	@Params:
		page_soup: a bs4.soup-Object of a recipe page
	@returns a list of links as strings
	"""
	rezept_link_list = []
	result_holder = page_soup.findAll("div", {"class": "ds-recipe-card bi-recipe-item"})
	result = []
	for rezept in result_holder:
		result.extend(rezept.findAll("a", {'href': True}))
	for link in result:
		href = str(link['href'])
		if "/rezepte/" in href:
			rezept_link_list.append(href)
	return rezept_link_list

def findLinkToNextPage(page_soup):
	nextPage = page_soup.findAll("a", {"class": "ds-btn ds-btn--round ds-btn--control"})[-1]
	return nextPage["href"]

def constructAllRecipePageLinks(count = 11420):
	basehtml = "https://www.chefkoch.de/rs/s__/Rezepte.html"
	result = [CHEFKOCH_LINK]
	for i in range(count):
		result.append(basehtml.replace("__", str(i)))
	return result

def getAllRecipePageLinks():
	#Weil insgesamt ~360k Rezepte und 41 pro Page => 11420
	result = []
	currentlink = CHEFKOCH_LINK
	while  True:
		if len(result) % 100 == 0: print("RecipePages Loaded: " + str(len(result)))
		result.append(currentlink)
		try:
			currentlink = "https://www.chefkoch.de" + findLinkToNextPage(getRawData(currentlink))
			print(currentlink)
		except Exception as e:
			print("Error while loading next page")
			print(e)
			break
	return result

def getRandomRecipeLink():
	"""returns a random link to a recipe page"""
	return (urlopen("https://www.chefkoch.de/rezepte/zufallsrezept/").geturl())

def asyncLoad(recipePageList):
	with pool.Pool(4) as p:
		p.map(asyncSinglePageLoad, recipePageList)

def asyncSinglePageLoad(page_list_url):
	page_soup = getRawData(page_list_url)
	for rezept in findRezeptLinks(page_soup):
		rezeptName, rating, url, imgsrc, zutaten = getRezeptInfo(rezept)
		#addRecipe(rezeptName, rating, url, imgsrc, zutaten)
	print("Finished a page")

def getRezeptInfo(url):
	zutaten = []
	page_soup = getRawData(url)
	imgsrc = page_soup.find("a", {"class":"bi-recipe-slider-open ds-target-link"})
	imgsrc = str(imgsrc)[str(imgsrc).find("src=") + 5:]
	imgsrc = imgsrc[:imgsrc.find('"')]
	rezeptName = page_soup.find("h1").text
	rating = str(page_soup.find("div", {"class":"ds-rating-avg"}))
	rating = rating[rating.find("strong") + 7:]
	rating = rating[:rating.find("<")]
	ingredient_table = page_soup.find("table", {"class":"ingredients table-header"})
	ingredientlist = ingredient_table.findAll("td", {"class":"td-right"})
	for ingredient in ingredientlist:
		if "(" in ingredient.text and ")" in ingredient.text and ingredient.text.index("(") < ingredient.text.index(")"):
			zutaten.append((ingredient.text[:ingredient.text.index("(")].replace("\n","") + ingredient.text[ingredient.text.index(")") + 1:].replace("\n","")).rstrip())
			continue
		zutaten.append(ingredient.text.replace("\n","").rstrip())
	return rezeptName, rating, url, imgsrc, zutaten
	
def filewriter(filename, line):
    with open(filename, 'a', encoding="utf-8") as f:
        f.write("\n" + line.rstrip('\r\n'))

def downloadStuff():
	index = 1
	masterlink = CHEFKOCH_LINK
	while True:
		page_soup = getRawData(masterlink)
		matchlinks = findRezeptLinks(page_soup)
		nextpageurl = findLinkToNextPage(page_soup)
		for link in matchlinks:
			print("Downloading No:" +  str(index) + " | Link: " + str(link))
			index +=1
			rezeptName, rating, url, imgsrc, zutaten = getRezeptInfo(link)
			#addRecipe(rezeptName, rating, url, imgsrc, zutaten)
			if index > 5000: return
		masterlink = nextpageurl	

def bruteForceRandomRecipes(limit=2000):
	result = {}
	while len(result) < limit:
		try:
			new_link = getRandomRecipeLink()
			if new_link in result: continue
			result[new_link] = list(getRezeptInfo(new_link))
			print("Just added " + str(result[new_link][0]))
		except Exception as e:
			print("Error while recipe")
			print(e)
			break
	pickle.dump(result, open("data/recipes.p", "wb" ) )
	return result


startTime = datetime.now()

if os.environ.get("HTTP_PROXY") is not None:
	print("Using Proxy.")

bruteForceRandomRecipes(limit=2000)

print(datetime.now() - startTime)