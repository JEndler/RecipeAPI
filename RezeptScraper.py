from urllib.request import urlopen
from urllib.request import Request
from bs4 import BeautifulSoup as soup
import pandas as pd
import random
from datetime import datetime

CHEFKOCH_LINK = "https://www.chefkoch.de/rs/s0/Rezepte.html"

SAMPLE_RECIPE = "https://www.chefkoch.de/rezepte/2293561365672708/Gulaschsuppe-im-Kessel-oder-Topf.html"

def getRawData(url, useragent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:67.0) Gecko/20100101 Firefox/67.0'):

	# User Agent Mozilla to Circumvent Security Blocking
	req = Request(url, headers={'User-Agent': useragent})

	# Connect and Save the HTML Page
	uClient = urlopen(req)
	page_html = uClient.read()
	uClient.close()

	# Parse HTML
	page_soup = soup(page_html, "html.parser")
	return page_soup

def findRezeptLinks(page_soup):
	rezept_link_list = []
	result_holder = page_soup.findAll("article", {"class": "rsel-item ds-grid-float ds-col-12 ds-col-m-8"})
	result = []
	for rezept in result_holder:
		result.extend(rezept.findAll("a", {'href': True}))
	for link in result:
		href = str(link['href'])
		if "/rezepte/" in href:
			rezept_link_list.append(href)
	return rezept_link_list

def findLinkToNextPage(page_soup):
	nextPage = page_soup.find("a", {"class": "ds-page-link bi-paging-next"})
	return nextPage["href"]

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
	return str(rezeptName) + ";" + str(rating) + ";" + str(url) + ";" +  str(imgsrc) + ";" + str(zutaten)
	
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
			filewriter("rezeptData.csv", getRezeptInfo(link))
			if index > 5000: return
		masterlink = nextpageurl	

startTime = datetime.now()

downloadStuff()

print(datetime.now() - startTime)