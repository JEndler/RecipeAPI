import mysql.connector

def getCursor():
	try:
		connection = getConnection()
		return connection.cursor()
	except Exception as e:
		print(e)
		pass

def getConnection():
	try:
		db = mysql.connector.connect(host="localhost",    # your host, usually localhost
                     user="rezepte",         # your username
                     passwd="1604",  # your password
                     database="rezepte"
                     )
		return db
	except Exception as e:
		print('database connection failed. Try installing the database first or check the connection preferences.')
	
	