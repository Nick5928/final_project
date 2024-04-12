from flask import Flask, render_template,request, jsonify, json, session, redirect, url_for
import util
from psycopg2 import Error, IntegrityError
from functools import wraps

username='nick5928'
password='pass'
host='127.0.0.1'
port='5432'
database='Healthy'

app = Flask(__name__)


app.secret_key = 'bfsd67sdfbsd7a76dfabsdf7asd6f66dhdasdjf94'

#ADD ROUTE FOR ADD BUTTON AND DELETEBUTTON
#EDIT PLAN ROUTE
def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return func(*args, **kwargs)
    return wrapper

@app.route('/api/connect', methods = ['GET'])
def user_connect():
    db_conn, db_cursor = util.connect_to_db()

    user = util.check_spoon(session['user_id'], db_conn, db_cursor)


    if user == -1:
        #user not found
    elif user is False:
        #user already connected
    
    else: 
        #user is not connected


    util.disconnect_from_db(db_conn,db_cursor)

    return jsonify({'success': True})

    

@app.route('/api/meal_plan/<int:target_calories>', methods=['GET'])
def api_gen_meal_plan(target_calories):
    

    meals = util.meal_plan(target_calories)

    print(meals)

    #return jsonify({'success': True})

    return jsonify(meals)

    

@app.route('/api/custom_recipes/<string:inc_ingred>/', methods=['GET'])
def api_gen_recipes(inc_ingred):
    recipes = util.get_recipes(inc_ingred)

    print(recipes)
    
    return jsonify(recipes)

@app.route('/api/custom_recipes/<string:inc_ingred>/<string:excl_ingred>', methods=['GET'])
def api_gen_recipes_exclude(inc_ingred, excl_ingred):

    recipes = util.get_recipes(inc_ingred, excl_ingred)

    print(recipes)
    
    return jsonify(recipes)

    #return jsonify({'success': True})

   

@app.route('/')
def index():
    return render_template('login.html')

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
        return result


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
        return result
    

@app.route('/home')
@login_required
def home():
    return render_template('home.html')

@app.route('/introduction')
@login_required
def intro():
    return render_template('intro.html')

@app.route('/plan')
@login_required
def plan():
    return render_template('plan.html')

@app.route('/recipe')
@login_required
def recipe():
    return render_template('recipe.html')




@app.route('/myplan')
@login_required
def user_plan():
    #GENERATE DATA TO PASS TO CLIENT FOR PLAN
    return render_template('user_plan.html')



if __name__ == '__main__':
    app.debug = True
    ip = '127.0.0.1'
    app.run(host=ip)

