"""
@Author: Henry Bust
This Class is responsible for handling the Database Interactions
It uses sqlite3 to store and retrieve Data that will later be used
by the *Insert use here*
"""
from msilib.schema import Error
import sqlite3
import traceback

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
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        );

        CREATE TABLE IF NOT EXISTS Recipes (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            source TEXT UNIQUE,
            img_source TEXT,
            rating FLOAT
        );

        CREATE TABLE IF NOT EXISTS Recipes_Ingredients (
            recipe_id INT NOT NULL,
            ingredient_id INT NOT NULL
        );
        
        """
        c.executescript(command)
        c.close()
        self.conn.commit()

    def close_connection(self):
        self.conn.close()
    
    def addRecipe(self, Name: str, Source: str, Img_Source: str, rating: float, ingredients: list):
        try:
            try:
                c = self.conn.cursor()
                tpl = (Name, Source, Img_Source, rating)
                c.execute("""
                INSERT INTO Recipes
                (name, source, img_source, rating)
                VALUES (?,?,?,?)
                """, tpl)
                c.close()
                self.conn.commit()
            except sqlite3.IntegrityError:
                    print("INFO: Failed to add Recipe (source must be unique)")
            c.execute("""
            SELECT ID from Recipes
            WHERE name = '{}'""".format(Name))
            recipeID = c.fetchall()[0][0]
            for ingredient in ingredients:
                try:
                    c.execute("INSERT INTO Ingredients(name) VALUES('" + ingredient + "')")
                    self.conn.commit()
                except sqlite3.IntegrityError:
                    print("INFO: Failed to add Ingredient (name must be unique)")
                except Exception as e:
                    pass
                finally:
                    c.execute("SELECT ID FROM Ingredients WHERE name ='" + ingredient + "'")
                    ingredientID = c.fetchall()[0][0]
                    c.execute("INSERT INTO Recipes_Ingredients(recipe_id, ingredient_id) VALUES ({},{})".format(str(recipeID),str(ingredientID)))
                    self.conn.commit()
        except:
            traceback.print_exc
        finally:
            c.close()
        
    def getRecipes(self, ingredients: list):
        c = self.conn.cursor()
        ingredient_ids = []
        for ingredient in ingredients:
            SQL = """
            SELECT ID
            FROM Ingredients
            WHERE name = {}""".format(ingredient)

    def addIngredient(self, Name: str):
        try:    
            c = self.conn.cursor()
            c.execute("""
            INSERT INTO Ingredients
            (name)
            VALUES ('{}')
            """.format(Name.lower()))
            c.close()
            self.conn.commit()
        except sqlite3.IntegrityError:
            print("INFO: Failed to add Ingredient (Ingredient name must be unique)")
        except sqlite3.OperationalError:
            print("ERROR: operational error")
        except:
            print("ERROR: addIngredient failed: Unknown error")
    
    def addIngredients(self, names: list):
        for name in names:
            self.addIngredient(name)


def main():
    connection = dbConnector()
    connection.createDatabase()
    connection.addRecipe("qqq", "asdas", "dmdm", 4.5, ["banane", "salat"])
    connection.close_connection()
    print("Done")

if __name__ == "__main__":
    main()