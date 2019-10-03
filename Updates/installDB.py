import MySQLdb

warningCount = 0

def printWarning(message):
	global warningCount
	warning = "\033[1;33;40mWARNING: \033[m"
	print(warning + message)
	warningCount += 1

db = MySQLdb.connect(host="localhost",    	# your host, usually localhost
                     user="rezepte",         	# your username
                     passwd="1604"  			# your password
                     )
cursor = db.cursor()

cursor.execute("SHOW DATABASES")
fetch = cursor.fetchall()

databaseExists = False
for databases in fetch:
	if('rezepte' in databases):
		databaseExists = True
		printWarning("Database already exists. skipping...")
if not databaseExists:
	cursor.execute("CREATE DATABASE rezepte")

db = MySQLdb.connect(host="localhost",    # your host, usually localhost
                     user="rezepte",         # your username
                     passwd="1604",  # your password
                     database="rezepte"
                     )
cursor = db.cursor()

ingredientExists = False
recipeExists = False
cursor.execute("SHOW TABLES")
fetch = cursor.fetchall()
for tables in fetch:
	if 'ingredient' in tables:
		ingredientExists = True
		printWarning('Table ingredient already exists. skipping...')
	if 'recipe' in tables:
		recipeExists = True
		printWarning('Table recipe already exists. skipping...')
if not ingredientExists:
	cursor.execute('CREATE TABLE ingredient(ID INT NOT NULL AUTO_INCREMENT, name VARCHAR(255) NOT NULL, PRIMARY KEY(ID))')
	print('table ingredient successfully created!')
if not recipeExists:
	cursor.execute('CREATE TABLE recipe(ID INT NOT NULL AUTO_INCREMENT, name VARCHAR(255) NOT NULL UNIQUE, source VARCHAR(255), img_source VARCHAR(255), rating FLOAT, PRIMARY KEY(ID))')
	print('table recipe successfully created!')
print('update script runned with ' + str(warningCount) + ' warnings')