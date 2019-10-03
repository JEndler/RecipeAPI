from dbManager import getCursor

def addRecipe(recipeName, rating, url, img_url, ingredients):
	cursor = getCursor()
	cursor.execute("INSERT INTO recipe (name, rating, source, img_source ) VALUES (" + recipeName + "," + rating + "," + url + "," + img_url ")")
	mycursor.execute("COMMIT")
	mycursor.execute("SELECT ID from recipe WHERE name = '" + recipeName + "'")
	fetch = mycursor.fetch()
	print(fetch)