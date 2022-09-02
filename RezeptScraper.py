from urllib.request import urlopen
from urllib.request import Request
from bs4 import BeautifulSoup as soup
import pandas as pd
import random
from datetime import datetime
from multiprocessing import pool
import dbConnector
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

CHEFKOCH_RANDOM_LINK = "https://www.chefkoch.de/rezepte/zufallsrezept/"

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
	redirect_url = uClient.geturl()
	uClient.close()

	# Parse HTML
	page_soup = soup(page_html, "html.parser")
	return page_soup, redirect_url

def getRandomRecipeLink():
	"""returns a random link to a recipe page"""
	return (urlopen(CHEFKOCH_RANDOM_LINK).geturl())

def asyncSinglePageLoad(page_url):
	db = dbConnector.dbConnector()
	try:
		result = getRezeptInfo(page_url)
		print(result)
		db.addRecipe(result[0], result[2], result[3], result[1], result[4], result[5])
		print("Just added " + str(result[0]))
	except Exception as e:
		print("Error while recipe loading: " + str(page_url))
		print(e)
	db.close_connection()

def asyncLoad(threads = 8, url = CHEFKOCH_RANDOM_LINK, scrape_count = 5000):
	"""Multithreaded loading of recipes."""

	with pool.Pool(threads) as p:
		p.map(asyncSinglePageLoad, [url] * scrape_count)


def getRezeptInfo(url):
	"""Given a url to a recipe, returns a tuple of the following information:
		- Name of the Recipe
		- Rating of the Recipe
		- URL to the Recipe
		- URL to the Image of the Recipe
		- List of Ingredients 
		- List of Tags
	"""
	zutaten = []
	page_soup, redirect_url = getRawData(url)
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
	tags = [tag.text.strip() for tag in page_soup.findAll("a", {"class":"ds-tag bi-tags"})]
	return rezeptName, rating, redirect_url, imgsrc, zutaten, tags

def filewriter(filename, line):
    with open(filename, 'a', encoding="utf-8") as f:
        f.write("\n" + line.rstrip('\r\n'))

def bruteForceRandomRecipes(limit=3000):
	"""brute forces random recipes until limit is reached
	   saves each recipe to a dictionary and writes it to a file.
	"""
	result = {}
	db = dbConnector.dbConnector()
	while len(result) < limit:
		try:
			new_link = getRandomRecipeLink()
			if new_link in result: continue
			result[new_link] = list(getRezeptInfo(new_link))
			db.addRecipe(result[new_link][0], result[new_link][2], result[new_link][3], result[new_link][1], result[new_link][4], result[new_link][5])
			print("Just added " + str(result[new_link][0]))
		except Exception as e:
			print("Error while recipe")
			print(e)
			break
	pickle.dump(result, open("data/recipes.p", "wb" ) )
	db.close_connection()
	return result

startTime = datetime.now()

if os.environ.get("HTTP_PROXY") is not None:
	print("Using Proxy.")

asyncLoad(threads=8, scrape_count=1)

print(datetime.now() - startTime)