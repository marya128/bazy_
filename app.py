from flask import Flask, render_template, request
from flask_mysqldb import MySQL


app = Flask(__name__)

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
        print(selected_ingredients)

         # Create a cursor
        cur = mysql.connection.cursor()

        # Calling the procedura
        cur.callproc('przepisy_na_podstawie_podanych_skladników', selected_ingredients)

        # Fetch the results
        results2 = cur.fetchone()
        print(results2)
        # Close the cursor
        cur.close()

        return render_template('index.html', selected_ingredients=selected_ingredients, results2=results2)

