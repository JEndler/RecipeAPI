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
		print('Rezept ' + recipeName + ' ist schon in der Datenbank vorhanden. Überspringe...')

def getRecipes(ingredients):
	db = mysql.connector.connect(host="localhost",    # your host, usually localhost
                     user="rezepte",         # your username
                     passwd="1604",  # your password
                     database="rezepte"
                     )
	cursor = db.cursor()
	ingredientIDS =[] 
	SQL = "SELECT ID FROM ingredient WHERE name in ("
	for ingredient in ingredients:
		SQL += "'" + ingredient + "',"
	SQL += ")"
	old_string = SQL
	k = old_string.rfind(",")
	SQL = old_string[:k] + old_string[k+1:]
	cursor.execute(SQL)
	ingredientIDS.append(cursor.fetchall())
	print("ingredient ids= \n")
	print(ingredientIDS)
	SQL = "SELECT recipe_ingredient.recipe_id FROM recipe_ingredient"
	lastTable = "recipe_ingredient"
	for pIngredientID in ingredientIDS[0][0]:
		SQL += " INNER JOIN (SELECT " + lastTable + ".recipe_id FROM recipe_ingredient WHERE ingredient_id = " + str(pIngredientID) + ") " + str(pIngredientID) + "a" + " ON " + lastTable + ".recipe_id = " + str(pIngredientID) + "a" + ".recipe_id"
		lastTable = str(pIngredientID) + "a"
	SQL += " GROUP BY recipe_id"

	print("STATEMENT: \n" + SQL)
	cursor.execute(SQL)
	print(len(cursor.fetchall()))