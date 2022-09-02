"""
@Author: Henry Bust
This Class is responsible for handling the Database Interactions
It uses sqlite3 to store and retrieve Data that will later be used
by the *Insert use here*
"""
import sqlite3
import datetime

# TODO: Connect to real Log-File
def errorlog(errorstring):
    print(errorstring) 





class dbConnector():
    DB_FILEPATH = "data/recipedata.db"

    def __init__(self):
        self.conn = sqlite3.connect(self.DB_FILEPATH)

    def createDatabase(self):
        c = self.conn.cursor()
        command = """
        CREATE TABLE IF NOT EXISTS Ingredients (
            ID INT NOT NULL AUTO_INCREMENT,
            name VARCHAR(255) NOT NULL UNIQUE,
            PRIMARY KEY(ID)
        );

        CREATE TABLE IF NOT EXISTS Recipes (
            ID INT NOT NULL AUTO_INCREMENT,
            name VARCHAR(255) NOT NULL,
            source VARCHAR(255) UNIQUE,
            img_source VARCHAR(255),
            rating FLOAT,
            PRIMARY KEY(ID)
        );

        CREATE TABLE IF NOT EXISTS recipes_ingredients (
            recipe_id INT NOT NULL,
            ingredient_id INT NOT NULL
        );
        
        """
        c.executescript(command)
        c.close()
        self.conn.commit()

    def close_connection(self):
        self.conn.close()


def main():
    connection = dbConnector()
    connection.createDatabase()
    connection.close_connection()
    print("Done")

if __name__ == "__main__":
    main()