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

    cur = mysql.connection.cursor()
    cur.execute("SELECT nazwa from tagi")
    tags = cur.fetchall()
    cur.close()


    if request.method == 'GET':
        # Create a cursor
        cur = mysql.connection.cursor()

        # Execute a query
        cur.execute("SELECT nazwa FROM skladniki")

        # Fetch the results
        results = cur.fetchall()

        # Close the cursor
        cur.close()

        return render_template('index.html', results=results, tags=tags)

    if request.method == 'POST':

        selected_ingredients = request.form.getlist('ingr')
        selected_ingredients_string = ",".join(selected_ingredients)
        selected_ingredients2 = request.form.get('ingr2')
        selected_recipes = request.form.get('recipe_name')
        selected_tags = request.form.get('ingr3')


        # Create Query
        cur = mysql.connection.cursor()

        # Define query
        query = 'CALL przepisy_na_podstawie_podanych_skladników(%s)'
        query_recipe_name='CALL szukanie_po_nazwach(%s)'
        query_tags = 'CALL szukaj_po_tagu(%s)'

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
    
        elif selected_tags:
            cur.execute(query_tags, [selected_tags]) #redirect tagi.html 
            tagi = cur.fetchall()
            return render_template('tagi.html', tagi=tagi)

        results2 = cur.fetchall()
        print(results2)
       
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

@app.route('/tagi', methods =['GET'])
def tagi():
    print(tagi)
    return "Hello"

@app.route('/<selected_recipe>skladniki2', methods=["GET", "POST"])
def recipe_skladniki2(selected_recipe):
    
    int_selected_recipe = int(selected_recipe)
    print(int_selected_recipe)
    
    cur = mysql.connection.cursor()

    query = 'CALL skladniki_dla_przepisuid(%s)'

    cur.execute(query, (selected_recipe, ))

    results = cur.fetchall()

    cur.close()

    return render_template('skladniki2.html', results=results)

@app.route('/<selected_recipe>skladniki', methods=["GET", "POST"])
def recipe_skladniki(selected_recipe):
    
    user_id = session['id_user']
    int_selected_recipe = int(selected_recipe)
    print(int_selected_recipe)
    
    cur = mysql.connection.cursor()

    query = 'CALL skladniki_dla_przepisuid(%s)'

    cur.execute(query, (selected_recipe, ))

    results = cur.fetchall()

    cur.close()

    ### SECOND QUERY
    cur2 = mysql.connection.cursor()

    query_2 = """ SELECT skladniki.nazwa AS nazwa_skladnika,
            CASE WHEN user_has_skladniki.skladniki_id_skladniki IS NOT NULL THEN 'posiadasz składnik' ELSE 'nie posiadasz' END AS posiada
    FROM przepisy
    JOIN przepisy_has_skladniki ON przepisy.id_przepis = przepisy_has_skladniki.przepisy_id_przepis
    JOIN skladniki ON przepisy_has_skladniki.skladniki_id_skladniki = skladniki.id_skladniki
    LEFT JOIN user_has_skladniki ON skladniki.id_skladniki = user_has_skladniki.skladniki_id_skladniki
    AND user_has_skladniki.user_id_user = %s
    WHERE przepisy.id_przepis = %s """ 

    cur2.execute(query_2, (user_id, int_selected_recipe))

    results2 = cur2.fetchall()

    cur2.close()

    ingr_przepis = []
    for row in results:
        ingr_przepis.append(row[0])
        
    ingr_user = []
    for row in results2:
        if row[1] == 'nie posiadasz':
            ingr_user.append(row[0])

    print("przepis", ingr_przepis)
    print("user", ingr_user)

    return render_template('skladniki.html', results=results, results2=results2, ingr_przepis=ingr_przepis, ingr_user=ingr_user)

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

@app.route('/recenzje', methods =['GET'])
def recenzje():

    # Create a cursor
    cur = mysql.connection.cursor()

    # Execute a query
    cur.execute("SELECT id_przepis, nazwa FROM przepisy")

    # Fetch the results
    results = cur.fetchall()

    # Close the cursor
    cur.close()
    
    return render_template('recenzje.html', results=results)
    
@app.route('/<selected_recipe>recenzja-przepis.html', methods =['GET', 'POST'])
def recenzje_przepis(selected_recipe):


    if request.method == 'GET':
        # Create a cursor
        cur = mysql.connection.cursor()

        #query
        query = "SELECT * FROM recenzje WHERE przepisy_id_przepis = %s" 

        # Execute a query
        cur.execute(query, (selected_recipe,))

        # Fetch the results
        reviews = cur.fetchall()

        # Close the cursor
        cur.close()

        return render_template('recenzja-przepis.html', reviews=reviews)
    
    if request.method == 'POST':
        
        if 'submit_button' in request.form:

            ocena = request.form['options']
            tresc = request.form['tresc']
            user_id = session['id_user']

            print(ocena)
            # selected_recipe = przepis_id

            #convert to int
            int_selected_recipe = int(selected_recipe)
            int_ocena = int(ocena)

            cur = mysql.connection.cursor()

            #dodawanie recenzji do tabeli recenzje
            query = 'INSERT INTO recenzje (przepisy_id_przepis, user_id_user, recenzja, ocena_user, ilosc_zglaszen) VALUES (%s, %s, %s, %s, %s)'

            cur.execute(query, (int_selected_recipe, user_id, tresc, int_ocena, 0))

            #confirm changes on the table
            mysql.connection.commit()

            cur.close()

            return "Wystawiono opinie"

@app.route('/<reported_user><selected_przepis>zglos', methods =['GET', 'POST'])
def zglos(reported_user, selected_przepis):

    if request.method == 'GET':

        print(reported_user, type(reported_user))
        print(selected_przepis, type(selected_przepis))
        
        return render_template('zglos.html')
    
    if request.method == 'POST':

        tresc = request.form['report']
        int_reported_user = int(reported_user)
        int_selected_przepis = int(selected_przepis)

        cur = mysql.connection.cursor()

        #dodawanie recenzji do tabeli recenzje
        query = 'INSERT INTO zgloszenia (recenzje_przepisy_id_przepis, recenzje_user_id_user, user_id_user, tresc) VALUES (%s, %s, %s, %s)'

        cur.execute(query, (int_selected_przepis, int_reported_user, int_reported_user, tresc))

        mysql.connection.commit()

        cur.close()

        return "Przyjęto zgłoszenie"

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

@app.route("/lodowka", methods=['GET', 'POST'])
def lodowka():    
    user_id = session['id_user']
    if request.method == 'GET':

        # Create a cursor
        cur = mysql.connection.cursor()

        #define query
        query = 'CALL przepisy_na_podstawie_inventory(%s)'
        query2 = 'CALL pokaz_skladniki_uzytkownika(%s)'

        # Execute a query
        cur.execute(query, (user_id, ))

        # cur.commit()

        # Fetch the results
        results = cur.fetchall()

        # Close the cursor
        cur.close()

        cur2 = mysql.connection.cursor()
        cur2.execute(query2, (user_id,))
        results2=cur2.fetchall()
        cur2.close()

        # Create a cursor
        cur3 = mysql.connection.cursor()

        # Execute a query
        cur3.execute("SELECT nazwa FROM skladniki")

        # Fetch the results
        results3 = cur3.fetchall()

        # Close the cursor
        cur3.close()
            
        return render_template('lodowka.html', results=results, results2=results2, results3=results3)

    if request.method == 'POST':

        selected_ingredients = request.form.getlist('ingr')
        string_selected_ingredients = ",".join(selected_ingredients)
        
        cur = mysql.connection.cursor()

        query = "CALL dodaj_skladnik_do_inventory(%s, %s, %s)"
        cur.execute(query, (user_id, [string_selected_ingredients], 0))

        mysql.connection.commit()
        cur.close()

        return "Skladnik dodano"

@app.route('/usun_skladnik<ingredient>', methods=['GET'])
def usun_skladnik(ingredient):

    user_id = session['id_user']
    
    cur = mysql.connection.cursor()

    query = 'CALL usun_skladnik_z_inventory(%s, %s)'

    # Execute a query
    cur.execute(query, (user_id, ingredient))

    mysql.connection.commit()
    cur.close()

    return "Usunięto składnik"


@app.route("/przepisy", methods=["GET"])
def top10():

    # Create a cursor
    cur = mysql.connection.cursor()

    # Execute a query
    cur.execute("SELECT * FROM top_10_przepisow_wg_oceny")

    #   przepisy_na_podstawie_inventory

    # Fetch the results
    results = cur.fetchall()

    # Close the cursor
    cur.close()

    return render_template('top10.html', results=results)

if __name__ == "__main__":
    app.run(debug=True,host='0.0.0.0', port=5002)