from flask import Flask, render_template, request, session, logging, url_for, redirect, flash
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
from passlib.hash import sha256_crypt
from datetime import date
import time
from flask_mail import Mail, Message

app = Flask(__name__)

app.secret_key = '12345'

#database connection details
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'register'

# Intialize MySQL
mysql = MySQL(app)


@app.route("/")
def home():
  return render_template("home.html")

# register
@app.route("/register", methods=['GET','POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        password = request.form['password']
        confirm = request.form['confirm']
        secure_password = sha256_crypt.hash(str(password))

        if password == confirm and 'name' in request.form and 'password' in request.form and 'email' in request.form and 'phone' in request.form and 'confirm' in request.form:
            # Check if account exists using MySQL
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT * FROM users WHERE email = %s', (email,))
            account = cursor.fetchone()
            # If account exists show error and validation checks
            if account:
                flash("Account already exists!","danger")
                return render_template('register.html')
            else:
                #if account is new
                cursor.execute('INSERT INTO users VALUES (NULL, %s, %s, %s, %s)', (name, email, phone, secure_password))
                mysql.connection.commit()
                flash("Registration Successfull. You can login now!","success")
                return redirect(url_for('login'))

        else:
            flash("Password doesn't match or the fields are empty. Try again!","danger")
            return render_template('register.html')

    return render_template("register.html")

#login
@app.route("/login",methods=['GET','POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        secure_password = sha256_crypt.hash(str(password))

        # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM users WHERE email = %s', (email,))
        # Fetch one record and return result
        account = cursor.fetchone()
        

        # If account exists in accounts table in our database
        if account:
            if sha256_crypt.verify(password,account['password']):
                # Create session data, we can access this data in other routes
                session['loggedin'] = True
                session['id'] = account['id']
                session['email'] = account['email']
                session['phone'] = account['phone']
                session['name'] = account['name']
                # Redirect to home page
                
                return redirect(url_for('main'))
            else:
                #Incorrect
                flash("Invalid Credentials!","danger")
                return render_template("login.html")

            
        else:
            # Account doesnt exist
            flash("No such user!","danger")
            return render_template("login.html")

        
    return render_template("login.html")


@app.route("/main")
def main():
    # Check if user is loggedin
    if 'loggedin' in session:
        # User is loggedin show them the home page
        return render_template('main.html', name=session['name'],)
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))

@app.route("/txttoimg")
def txttoimg():
    # Check if user is loggedin
    if 'loggedin' in session:
        # User is loggedin show them the home page
        return render_template('txttoimg.html')
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))

@app.route('/logout')
def logout():
    # Remove session data, this will log the user out
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('name', None)
   # Redirect to login page
   flash("You are now logged out!","success")
   return redirect(url_for('login'))


if __name__ == '__main__':
    debug=True
    app.run(debug=True,port=8080)
