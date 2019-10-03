from dbManager import getCursor
import mysql.connector

def addRecipe(recipeName, rating, url, img_url, ingredients):
	db = mysql.connector.connect(host="localhost",    # your host, usually localhost
                     user="rezepte",         # your username
                     passwd="1604",  # your password
                     database="rezepte"
                     )
	cursor = db.cursor()
	sqlTemp = "INSERT INTO recipe (name, rating, source, img_source ) VALUES (%s, %s, %s, %s)"
	sqlFormular = "INSERT INTO recipe (name, rating, source, img_source ) VALUES (" + recipeName + ", " + rating + ", " + url + ", " + img_url + ")"
	recipe = [
			(recipeName, rating, url, img_url)
			]
	cursor.executemany(sqlTemp, recipe)
	cursor.execute("COMMIT")
	cursor.execute("SELECT ID from recipe WHERE name = '" + recipeName + "'")
	fetch = cursor.fetchall()
	print(fetch)