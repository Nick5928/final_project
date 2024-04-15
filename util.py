import requests 
import psycopg2
from psycopg2 import Error, IntegrityError

#APIKEY and BASEURL for spoonacular api
APIKEY = "a7a0217f23184955a25d9af31afbc7a1"
BASEURL = "https://api.spoonacular.com"

"""
Generate a three meal plan for one day using spoonacular api

Parameters:
- target_calories (int): Target calories for the meal plan in one day

Returns:
- recipes: json object containing information about the recipes
"""
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


"""
Get three random recipes from spoonacular api

Parameters:
- inc_ingred (string): The ingredients to include
- excl_ingred (string): The ingredients to exclude

Returns:
- recipes: json object containing information about the recipes
"""
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


        
        #Build and append recipe json to recipes
        build_recipe_json(nutrients, recipe, recipes)
        
    return recipes

"""
Get nutirition information from a nutrients object

Parameters:
- nutri (dict): Nutrition object

Returns:
- cal (int): Calories 
- carb (int): Carbohydrates
- fat (int): Fat
- protein (int): Protein
"""
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


"""
Add recipe information to recipes object

Parameters:
- nutri (dict): Nutritient object
- recipe(dict): Recipe object
- Recipe(dict): Recipes object
"""
def build_recipe_json(nutri, recipe, recipes):
    #Get nutrient information from the nutrient object
    cal, carb, fat, protein = get_nutri(nutri)

    #Pull the id from the recipe object
    recipe_id = recipe['id']

    #Pull the image type to build the image link
    img_type = recipe['imageType']
    img_size = "90x90"

    #Build image link
    img_url = f"https://img.spoonacular.com/recipes/{recipe_id}-{img_size}.{img_type}"

    #Build recipe info object
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

    #Add recipe info object to recipes object
    recipes.append(recipe_info)


"""
Connect to a databse

Function from Rui Wu
"""
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


"""
Disconnect from database

Function from Rui Wu

"""
def disconnect_from_db(connection,cursor):
    if (connection):
        cursor.close()
        connection.close()
        print("PostgreSQL connection is closed.")
    else:
    	print("Connection does not work.")


"""
Add user to user table

Parameters:
- username (string): Users username
- email (string): Users email
- first_name(string): Users first name
- last_name(string)NOT REQUIRED: Users last name
- password(string): Users password
- connection: The database connection
- cursor: The database cursor

Returns:
True if user was added
Error msg if user couldn't be added
"""
def add_user(username, email, first_name, password, connection, cursor, last_name=""):

    #Build sql query
    sql = """
        INSERT INTO users (username, email, password, first_name, last_name)
        VALUES (%s, %s, %s, %s, %s)
    """
    
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


"""
Sign user in to the web app if possible

Parameters:
- username(string): Users username
- input_password(string): Typed password from user
- connection: Database connection
- cursor: Database cursor

Returns:
- True and user_id if user existed and password was correct
- Message, -1 corresponding to the error occured if otherwise
"""
def sign_user_in(username, input_password, connection, cursor):

    #Grab password for the user from users table
    cursor.execute("SELECT password FROM users WHERE username = %s", (username,))
    stored_password = cursor.fetchone()



    if stored_password:
        
        #Password was correct
        if input_password == stored_password[0]:

            #Get users user_id if password was correct
            cursor.execute("SELECT user_id FROM users WHERE username = %s", (username,))
            user_id = cursor.fetchone()[0]

            return True, user_id
        else:
            #Password was incorrect
            return "incorrect" , -1

    #User was not found
    else: 
        return "not found", -1



"""
Add meal to user's recipes

Parameters:
- meal_data(dict): Meal object to add to users recipes
- user_id(int): Users user_id
- connection: Database connection
- cursor: Database cursor

Returns:
- True if meal was added false otherwise
"""
def add_meal(meal_data, user_id, connection, cursor):
    """
    recipe_id
    user_id
    recipe_name
    recipe_link
    calories
    fat
    protein
    carbohydrates
    """

    #Build sql query
    sql = """
        INSERT INTO recipes (user_id, recipe_name, recipe_link, calories, fat, protein, carbohydrates)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """

    values = (
        user_id, 
        meal_data['recipe_name'], 
        meal_data['recipe_link'], 
        meal_data['calories'], 
        meal_data['fat'], 
        meal_data['protein'], 
        meal_data['carbohydrates']
    )

    try:
        cursor.execute(sql, values)
        connection.commit()
        return True

    
    except Exception as error:
        connection.rollback()
        print("Errors while executing the SQL query: ", error)

        return False




"""
Delete meal from user's recipes

Parameters:
- meal_data(dict): Meal object to delete from users recipes
- user_id(int): Users user_id
- connection: Database connection
- cursor: Database cursor

Returns:
- True if meal was deleted, False otherwise
"""
def del_meal(recipe_name, user_id, connection, cursor):

    try: 
        cursor.execute("DELETE FROM recipes WHERE recipe_name = %s AND user_id = %s", (recipe_name, user_id))
        if cursor.rowcount == 0:
            return False
        
        connection.commit()
        return True
    except Exception as e:
        connection.rollback()
        return False


"""
Check if meal can be added or not

Parameters:
- recipe_name(string): Name of recipe
- user_id(int): Users user_id
- cursor: Database cursor

Returns:
- False if recipe exists for that user otherwise True
"""
def check_meal(recipe_name, user_id, cursor):
    cursor.execute("SELECT * FROM recipes WHERE user_id = %s AND recipe_name = %s", (user_id, recipe_name))
    row = cursor.fetchone()

    if row:  
        return False
 
    
    return True


"""
Get a users recipes data

Parameters:
- user_id(int): Users user_id
- cursor: Database cursor

Returns:
- Recipe object holding all of the users recipes
"""
def get_users_recipes(user_id, cursor):
    cursor.execute("SELECT * FROM recipes WHERE user_id = %s", (user_id,))
    rows = cursor.fetchall()

    result = []



    for row in rows:
        name, link, cal, fat , protein, carbs = row[2:8]
        data = {
            "recipe_name" : name,
            "recipe_link" : link,
            "calories": cal,
            "fat": fat,
            "protein": protein,
            "carbohydrates": carbs
        }
        result.append(data)

    
    return result







    








    




