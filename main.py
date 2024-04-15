from flask import Flask, jsonify, render_template,request, session, redirect, url_for
import util
from psycopg2 import Error, IntegrityError
from functools import wraps

username='nick5928'
password='pass'
host='127.0.0.1'
port='5432'
database='Healthy'

app = Flask(__name__)
app.secret_key = "980fd8as9hfa89shglksjxcnksd09gsa0gS"



def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return func(*args, **kwargs)
    return wrapper



@app.route('/api/add_meal', methods = ['POST'])
def add_meal():

    meal_data = request.get_json()

    db_conn, db_cursor = util.connect_to_db()
    
    


    
    return_msg = False
    if util.check_meal(meal_data['recipe_name'], session['user_id'], db_cursor):
        util.add_meal(meal_data, session['user_id'], db_conn, db_cursor)
        return_msg = True
    
    util.disconnect_from_db(db_conn, db_cursor)


    return jsonify({'success' : return_msg})


@app.route('/api/del_meal/<string:recipe_name>', methods = ['POST'])
def del_meal(recipe_name):

    db_conn, db_cursor = util.connect_to_db()

    return_msg = False
    if not util.check_meal(recipe_name, session['user_id'], db_cursor):
        return_msg = util.del_meal(recipe_name, session['user_id'], db_conn, db_cursor)
    
    util.disconnect_from_db(db_conn, db_cursor)


    return jsonify({'success' : return_msg})



@app.route('/api/meal_plan/<int:target_calories>', methods=['GET'])
def api_gen_meal_plan(target_calories):
    

    meals = util.meal_plan(target_calories)

  

    return jsonify(meals)

    

@app.route('/api/custom_recipes/<string:inc_ingred>/', methods=['GET'])
def api_gen_recipes(inc_ingred):
    recipes = util.get_recipes(inc_ingred)

    
    return jsonify(recipes)

@app.route('/api/custom_recipes/<string:inc_ingred>/<string:excl_ingred>', methods=['GET'])
def api_gen_recipes_exclude(inc_ingred, excl_ingred):

    recipes = util.get_recipes(inc_ingred, excl_ingred)

    
    return jsonify(recipes)


   

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/signup_page')
def signup_page():
    return render_template('signup.html')

@app.route('/login', methods=['POST'])
def login():
    db_conn, db_cursor = util.connect_to_db()
    username = request.form['login-username']
    password = request.form['login-password']


    result, user_id = util.sign_user_in(username, password, db_conn, db_cursor)

    

    util.disconnect_from_db(db_conn,db_cursor)

    
    if result == True:
        session['user_id'] = user_id
        return home()
    
    else:
        return render_template('login_fail.html')


@app.route('/signup', methods=['POST'])
def signup():


    username = request.form['signup-username']
    email = request.form['signup-email']

    full_name = request.form['signup-name']

    name_parts = full_name.split()

    first_name = name_parts[0]  
    last_name = name_parts[1] if len(name_parts) > 1 else ""



    password = request.form['signup-password']

    db_conn, db_cursor = util.connect_to_db()

    result = util.add_user(username, email, first_name, password, db_conn, db_cursor, last_name)

    util.disconnect_from_db(db_conn, db_cursor)

    if result == True:
        return index()

    else:
        return render_template("signup_fail.html")
    

@app.route('/home')
@login_required
def home():
    return render_template('home.html')



@app.route('/plan')
@login_required
def plan():
    return render_template('plan.html')

@app.route('/recipe')
@login_required
def recipe():
    return render_template('recipe.html')


@app.route('/myrecipes')
@login_required
def user_recipes():
    user_id = session['user_id']

    db_conn, db_cursor = util.connect_to_db()

    user_recipes = util.get_users_recipes(user_id, db_cursor)


    util.disconnect_from_db(db_conn,db_cursor)


    
    return render_template('user_recipes.html', user_recipes=user_recipes)



if __name__ == '__main__':
    app.debug = True
    ip = '127.0.0.1'
    app.run(host=ip)

