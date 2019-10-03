def getCursor():
	try:
		return getConnection.getCursor()
	except Exception as e:
		

	
def getConnection():
	try:
		db = MySQLdb.connect(host="localhost",    # your host, usually localhost
                     user="rezepte",         # your username
                     passwd="1604",  # your password
                     database="rezepte"
                     )
		return db
	except Exception as e:
		print('database connection failed. Try installing the database first or check the connection preferences.')
	
	