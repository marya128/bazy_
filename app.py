from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL


app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret key' 

app.config['MYSQL_HOST'] = 'database-project-pwr.mysql.database.azure.com'
app.config['MYSQL_USER'] = 'project0admindb'
app.config['MYSQL_PASSWORD'] = 'dzbany&p0rcelanyDB*k0l'
app.config['MYSQL_DB'] = 'dbp2'
 
mysql = MySQL(app)


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == 'GET':
        # Create a cursor
        cur = mysql.connection.cursor()

        # Execute a query
        cur.execute("SELECT nazwa FROM skladniki")

        # Fetch the results
        results = cur.fetchall()

        # Close the cursor
        cur.close()

        return render_template('index.html', results=results)

    if request.method == 'POST':

        selected_ingredients = request.form.getlist('ingr')
        selected_ingredients_string = ",".join(selected_ingredients)
        selected_ingredients2 = request.form.get('ingr2')
        selected_recipes = request.form.get('recipe_name')


        # Create Query
        cur = mysql.connection.cursor()

        # Define query
        query = 'CALL przepisy_na_podstawie_podanych_skladników(%s)'
        query_recipe_name='CALL szukanie_po_nazwach(%s)'

        if selected_ingredients:

            # Call the procedure with the selected ingredient
            cur.execute(query, [selected_ingredients_string])

        elif selected_ingredients2:
            print("hello")
            ingredients = selected_ingredients2.split()

            # Join the ingredients with a comma and no whitespace
            ingredients_string = ",".join(ingredients)

            cur.execute(query, [ingredients_string])

        elif selected_recipes:

            selected_recipes = request.form.get('recipe_name')
        
            return redirect(url_for('przepisy_nazwa', selected_recipes=selected_recipes, **request.args))
    

        results2 = cur.fetchall()
       
    cur.close() #!!!!!!
    return render_template('index.html', results2=results2)

@app.route('/<selected_recipes>przepisy-nazwa.html', methods =['GET'])
def przepisy_nazwa(selected_recipes):

    print(selected_recipes)

    cur = mysql.connection.cursor()

    query_recipe_name='CALL szukanie_po_nazwach(%s)'

    cur.execute(query_recipe_name, [selected_recipes])

    results3 = cur.fetchall()

    cur.close()
    
    return render_template('przepisy-nazwa.html', results3=results3)

@app.route('/usun>', methods = ['POST'])
def usun():
    
    user_id = session['id_user']

    cur = mysql.connection.cursor()

    query = 'CALL usuwanie_uzytkownika(%s)'

    cur.execute(query, (user_id, ))

    #confirm changes on the table
    mysql.connection.commit()

    cur.close()

    return "Konto usunieto"

@app.route('/login', methods =['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'username' in request.form:

        username = request.form['username']
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM user WHERE nazwa = % s', (username, ))
        account = cursor.fetchone()
        print(account)

        if account:
            session['loggedin'] = True
            session['nazwa'] = account[1]
            session['id_user'] = account[0]
            msg = 'Logged in successfully !'
            return redirect("/")
        else:
            msg = 'Incorrect username !'

    return render_template('login.html', msg = msg)

@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    return redirect(url_for('login'))


@app.route("/lodowka", methods=["GET"])
def lodowka():    

    user_id = session['id_user']

    # Create a cursor
    cur = mysql.connection.cursor()

    #define query
    query = 'CALL przepisy_na_podstawie_inventory(%s)'

    # Execute a query
    cur.execute(query, (user_id, ))

    # cur.commit()

    # Fetch the results
    results = cur.fetchall()

    # Close the cursor
    cur.close()

    return render_template('lodowka.html', results=results)

@app.route("/recenzje", methods=["GET"])
def recenzje():

    # Create a cursor
    cur = mysql.connection.cursor()

    # Execute a query
    cur.execute("SELECT * FROM top_10_przepisow_wg_oceny")

    #   przepisy_na_podstawie_inventory

    # Fetch the results
    results = cur.fetchall()

    # Close the cursor
    cur.close()

    return render_template('recenzje.html', results=results)

