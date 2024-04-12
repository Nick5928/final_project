import requests 
import psycopg2
from psycopg2 import Error, IntegrityError
import bcrypt

#APIKEY and BASEURL for spoonacular api only uses this for the recipe and meal plan generator
APIKEY = "a7a0217f23184955a25d9af31afbc7a1"
BASEURL = "https://api.spoonacular.com"

#Create a 3 meal plan using spoonacular api with target_calories
def meal_plan(target_calories):

    #Build Url to generate meal plan
    URL = f"{BASEURL}/mealplanner/generate?apiKey={APIKEY}&timeFrame=day&targetCalories={target_calories}"

    
    response = requests.get(URL)
    recipes_data = response.json()


    #list to hold recipe json
    recipes = []


    #Loop through the recipes in recipes data
    for recipe in recipes_data['meals']:

        #Grab id for nutrient api call
        recipe_id = recipe['id']

        #Build url for nutrient api call
        URL = f"{BASEURL}/recipes/{recipe_id}/nutritionWidget.json?apiKey={APIKEY}"

        response = requests.get(URL)

        recipe_data = response.json()

        #Grab nutrients from recipe json
        nutrients = recipe_data['nutrients']

        #Build and append recipe json to recipes
        build_recipe_json(nutrients, recipe, recipes)


    return recipes


def get_recipes(inc_ingred = "", excl_ingred = ""):

    #Build params and URL for search recipes api call
    params = f"apiKey={APIKEY}&includeIngredients={inc_ingred}&excludeIngredients={excl_ingred}&addRecipeNutrition=true&number=3&sort=random"
    URL = f"{BASEURL}/recipes/complexSearch?{params}"


    response = requests.get(URL)

    recipe_data = response.json()

    #list to hold recipe json
    recipes = []

    #Loop through the recipes in recipes data
    for recipe in recipe_data['results']:

        #Grab nutrients from recipe json
        nutrients = recipe['nutrition']['nutrients']


        print("util.py")
        
        #Build and append recipe json to recipes
        build_recipe_json(nutrients, recipe, recipes)
        
    return recipes

def get_nutri(nutri):

    cal, carb, fat, protein = "", "", "", ""

    for nutrient in nutri:
            if nutrient['name'] == 'Calories':
                cal = nutrient['amount']
            elif nutrient['name'] == 'Carbohydrates':
                carb = nutrient['amount']
            elif nutrient['name'] == 'Fat':
                fat = nutrient['amount']
            elif nutrient['name'] == 'Protein':
                protein = nutrient['amount']
    return cal, carb, fat, protein



def build_recipe_json(nutri, recipe, recipes):
    cal, carb, fat, protein = get_nutri(nutri)

    recipe_id = recipe['id']

    img_type = recipe['imageType']
    img_size = "90x90"

    img_url = f"https://img.spoonacular.com/recipes/{recipe_id}-{img_size}.{img_type}"
    recipe_info = {
            "title": recipe['title'],
            "image": img_url,
            "link": recipe['sourceUrl'],
            "nutrients" :{
                "calories": cal,
                "carbohydrates": carb,
                "fat": fat,
                "protein": protein
            }

        }

    recipes.append(recipe_info)


def connect_to_db(username='nick5928',password='pass',host='127.0.0.1',port='5432',database='Healthy'):
	try:
	    
	    connection = psycopg2.connect(user=username,
	                                  password=password,
	                                  host=host,
	                                  port=port,
	                                  database=database)

	    cursor = connection.cursor()
	    print("connected to the database")

	    return connection, cursor

	except (Exception, Error) as error:
	    print("Error while connecting to PostgreSQL", error)


def disconnect_from_db(connection,cursor):
    if (connection):
        cursor.close()
        connection.close()
        print("PostgreSQL connection is closed.")
    else:
    	print("Connection does not work.")



def add_user(username, email, first_name, password, connection, cursor, last_name=""):
    sql = """
        INSERT INTO users (username, email, password_hash, first_name, last_name)
        VALUES (%s, %s, %s, %s, %s)
    """
    salt = bcrypt.gensalt()




    values = (username, email, password, first_name, last_name)


    
    try:
        cursor.execute(sql, values)
        connection.commit()
        return True

    except IntegrityError as error:
        connection.rollback()
        print("Error: Username or email already exists:", error)


        return "Error: Username or email already exists. Try again"
    except Exception as error:
        connection.rollback()
        print("Errors while executing the SQL query: ", error)

        return "An error occurred during signup. Please try again later."


def sign_user_in(username, input_password, connection, cursor):
    cursor.execute("SELECT password_hash FROM users WHERE username = %s", (username,))

    row = cursor.fetchone()

    if row:
        stored_password = row[0]

        if input_password == stored_password:

            cursor.execute("SELECT user_id FROM users WHERE username = %s", (username,))

            user_id = cursor.fetchone()[0]

            return True, user_id
        else:
            return "incorrect"

    else: 
        return "not found"


def check_spoon(user_id, connection, cursor):

    cursor.execute("SELECT username, password_hash, email, first_name, last_name, spoon_id FROM users WHERE user_id = %s", (user_id,))
    row = cursor.fetchone()

    if row:  
        username, password, email, first_name, last_name, spoon_id = row
        
        if spoon_id is None:
            user = {
                "username": username,
                "password": password,
                "email": email,
                "first_name": first_name,
                "last_name": last_name,
                "spoon_id": spoon_id
            }

            return user

        else:
            return False

    
    else: 
        return -1


def connect_spoon(user):
    




    




