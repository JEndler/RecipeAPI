from dbManager import getCursor
import mysql.connector

def addRecipe(recipeName, rating, url, img_url, ingredients):
	db = mysql.connector.connect(host="localhost",    # your host, usually localhost
                     user="rezepte",         # your username
                     passwd="1604",  # your password
                     database="rezepte"
                     )
	cursor = db.cursor()
	try:
		sqlTemp = "INSERT INTO recipe (name, rating, source, img_source ) VALUES (%s, %s, %s, %s)"
		recipe = [
			(recipeName, rating, url, img_url)
			]
		cursor.executemany(sqlTemp, recipe)
		cursor.execute("COMMIT")
		cursor.execute("SELECT ID from recipe WHERE name = '" + recipeName + "'")
		recipeID = cursor.fetchall()[0][0]
		for ingredient in ingredients:
			try:
				cursor.execute("INSERT INTO ingredient(name) VALUES('" + ingredient + "')")
				cursor.execute('COMMIT')
			except Exception as e:
				pass
			finally:
				cursor.execute("SELECT ID FROM ingredient WHERE name ='" + ingredient + "'")
				ingredientID = cursor.fetchall()[0][0]
				cursor.execute("INSERT INTO recipe_ingredient(recipe_id, ingredient_id) VALUES ("+ str(recipeID) + ", " + str(ingredientID) + ")")
				cursor.execute('COMMIT')
	except Exception as e:
		print('Rezept ' + recipeName + 'ist schon in der Datenbank vorhanden. Überspringe...')
	
