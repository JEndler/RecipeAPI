"""
@Author: Henry Bust (no other authors.)
This Class is responsible for handling the Database Interactions
It uses sqlite3 to store and retrieve Data that will later be used
by the *Insert use here*
"""
from genericpath import isfile
import re
import sqlite3
import traceback
import os
import pickle
import logging

# Instantiating the Logger and the File Handler
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.FileHandler('data/db_log.txt')
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

class dbConnector():
    DB_FILEPATH = "data/recipedata.sqlite"

    def __init__(self):
        self.conn = sqlite3.connect(self.DB_FILEPATH)

    def createDatabase(self):
        c = self.conn.cursor()
        command = """

        CREATE TABLE IF NOT EXISTS Recipes (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            source TEXT UNIQUE,
            img_source TEXT,
            rating FLOAT
        );

        CREATE TABLE IF NOT EXISTS Ingredients (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        );

        CREATE TABLE IF NOT EXISTS Recipes_Ingredients (
            recipe_id INT NOT NULL,
            ingredient_id INT NOT NULL,
            PRIMARY KEY (recipe_id, ingredient_id)
        );

        CREATE TABLE IF NOT EXISTS Tags (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        );

        CREATE TABLE IF NOT EXISTS Recipes_Tags (
            recipe_id INT NOT NULL,
            tag_id INT NOT NULL,
            PRIMARY KEY (recipe_id, tag_id)
        );
        
        """
        c.executescript(command)
        self.conn.commit()
        c.close()

    def close_connection(self):
        self.conn.close()
    
    def addIngredient(self, Name: str):
        try:    
            c = self.conn.cursor()
            c.execute("""
            INSERT INTO Ingredients
            (name)
            VALUES ('{}')
            """.format(Name.lower()))
        except sqlite3.IntegrityError:
            logger.info("INFO: Failed to add Ingredient (Ingredient name must be unique)")
        except sqlite3.OperationalError:
            logger.error("ERROR: operational error")
        except:
            logger.error("ERROR: addIngredient failed: Unknown error")
        finally:
            self.conn.commit()
                    
    
    def addIngredients(self, names: list):
        for name in names:
            self.addIngredient(name)
    
    def addTag(self, Name: str):
        try:    
            c = self.conn.cursor()
            c.execute("""
            INSERT INTO Tags
            (name)
            VALUES ('{}')
            """.format(Name.lower()))
        except sqlite3.IntegrityError:
            logger.info("INFO: Failed to add Tag (Tag name must be unique)")
        except sqlite3.OperationalError:
            logger.error("ERROR: operational error")
        except:
            logger.error("ERROR: addIngredient failed: Unknown error")
        finally:
            self.conn.commit()
                    
    
    def addTags(self, names: list):
        for name in names:
            self.addTag(name)

    def addRecipe(self, Name: str, Source: str, Img_Source: str, rating: float, ingredients: list, tags: list):
        try:
            try:
                c = self.conn.cursor()
                tpl = (Name, Source, Img_Source, rating)
                c.execute("""
                INSERT INTO Recipes
                (name, source, img_source, rating)
                VALUES (?,?,?,?)
                """, tpl)
                self.conn.commit()
            except sqlite3.IntegrityError:
                    logger.info("INFO: Failed to add Recipe (source must be unique)")
            c.execute("""
            SELECT ID from Recipes
            WHERE name = '{}'""".format(Name))
            recipeID = c.fetchall()[0][0]

            # Insert ingredients in the ingredients table:
            self.addIngredients(ingredients)
            try:

                for ingredient in ingredients:
                    SQL = "SELECT ID FROM Ingredients WHERE name ='" + ingredient.lower() + "'"
                    c.execute(SQL)
                    ingredientID = c.fetchall()[0][0]
                    SQL = "INSERT INTO Recipes_Ingredients(recipe_id, ingredient_id) VALUES ({},{})".format(str(recipeID),str(ingredientID))
                    c.execute(SQL)
                    self.conn.commit()
            except sqlite3.IntegrityError:
                    logger.info("INFO: Failed to add ingredient (name must be unique)")
            except Exception as e:
                logger.error(e)
            
            # Insert tags in the tags table:
            self.addTags(tags)
            for tag in tags:
                c.execute("SELECT ID FROM Tags WHERE name ='" + tag.lower() + "'")
                tagID = c.fetchall()[0][0]
                c.execute("INSERT INTO Recipes_Tags(recipe_id, tag_id) VALUES ({},{})".format(str(recipeID),str(tagID)))
                self.conn.commit()
        except sqlite3.IntegrityError:
                    logger.info("INFO: Failed to add tag (name must be unique)")
        except Exception as e:
            logger.error(e)
            traceback.print_exc
        finally:
            c.close()
            
        
    def getRecipes(self, ingredients: list, LIMIT = 25):
        c = self.conn.cursor()

        # SQL Statement to select the recipes, and the ratio of present ingredients, that have the most ingredients in common with the requested ingredients
        SQL = """
            SELECT id, name, count, source, img_source, rating FROM Recipes INNER JOIN 
            (SELECT recipe_id, COUNT(*) as count FROM Recipes_Ingredients INNER JOIN
                (SELECT ID FROM Ingredients WHERE Name IN {} )
            AS requested_ingredients ON requested_ingredients.id = Recipes_Ingredients.ingredient_id
            GROUP BY recipe_id
            ORDER BY count DESC
            LIMIT {}) AS recipe_counts ON id = recipe_counts.recipe_id
            """.format(
                "(" + ",".join([" '" + ingredient.replace(",","") + "' " for ingredient in ingredients]) + ")",
                LIMIT
                )

        c.execute(SQL)
        recipes = c.fetchall()
        c.close()
        return recipes

    def getIngredientCount(self, recipe_id):
        """Counts the number of ingredients for a given recipe id. Returns it as Int.
        """
        c = self.conn.cursor()
        c.execute("""
        SELECT COUNT(*) FROM Recipes_Ingredients
        WHERE recipe_id = {}
        """.format(recipe_id))
        count = c.fetchall()[0][0]
        c.close()
        return count

    

    def loadRecipeFromFile(self, pickle_path = "data/recipes.p"):
        """Loads a list of recipes from a pickle file.
            @Params: pickle_path: The path to the pickle file
            @Returns: None
            @Throws: FileNotFoundError if the pickle file does not exist
        """

        assert isfile(pickle_path), "ERROR: File not found"
        recipes = pickle.load(open(pickle_path,"rb"))
        for key in recipes.keys():
            name, source, img_source, rating, ingredients = recipes[key][0], recipes[key][2], recipes[key][3], recipes[key][1], recipes[key][4]
            self.connection.addRecipe(name, source, img_source, rating, ingredients)    

    def getAPIData(self, ingredient_list):
        """Gets all recipes that include the given ingredients.
            @Params: ingredient_list: A list of ingredients"""

        recipes = self.getRecipes(ingredient_list)
        res = []
        for recipe in recipes:
            total_ingredients = self.getIngredientCount(recipe[0])
            
            recipe_dict = {
                "name": recipe[1],
                "id": recipe[0],
                "present_ingredients": recipe[2],
                "total_ingredients": total_ingredients,
                "source": recipe[3],
                "img_source": recipe[4],
                "rating": recipe[5]
            }
            res.append(recipe_dict)
        return res

def main():

    connection = dbConnector()
    connection.createDatabase()
    connection.close_connection()
    print("Done")

if __name__ == "__main__":
    main()