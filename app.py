from flask import Flask, render_template, request, session, logging, url_for, redirect, flash
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re, time, steganography, os
from passlib.hash import sha256_crypt
from datetime import date
from PIL import Image
import random
from flask_mail import Mail, Message
from cryptosteganography import CryptoSteganography
from werkzeug.utils import secure_filename

app = Flask(__name__)

app.secret_key = '12345'

#database connection details
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'register'

app.config['UPLOAD_FOLDER']='/static/images/steg'

# Intialize MySQL
mysql = MySQL(app)

# configuration of mail
app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'mgangrade24@gmail.com'
app.config['MAIL_PASSWORD'] = ''
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)


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

@app.route("/txttoimg", methods=['GET','POST'])
def txttoimg():
    # Check if user is loggedin
    if 'loggedin' in session:
        if request.method=='POST':
            secrettext = request.form['secrettext']
            email = request.form['email']
            algo = request.form['algo']
            
            
            file = request.files['img[]']
            file.save(secure_filename(file.filename))
            image = file.filename.replace(" ","_")
            image = image.replace("(","")
            image = image.replace(")","")
            output = 'output_' + image

            print(image)
            print(file.filename)
            print(algo)
            print(email)
            print(secrettext)
            print(output)
            
            if algo == 'aes':
                keyAES = random.randint(1000000, 99999999)
                stegoAES = CryptoSteganography(str(keyAES))
                stegoAES.hide(image, output, secrettext)

                msg = Message(
                "HideO - A Steganography Tool",
                sender ='mgangrade24@gmail.com',
                recipients = [email, session['email']])
                msg.body = "Hello HideO User,\n" + "Here are the details of secret data sent to you." + "\n\nSent By: " + session['name'] + "\n\nKey: "+ str(keyAES) +"\n\nAlgorithm Used: AES"

                with app.open_resource(output) as fp:
                    msg.attach(output, "image/png", fp.read())
            

                mail.send(msg)
                flash("Mail has been sent successfully!","success")
            
            if algo == 'des':
                keyDES = random.randint(1000000, 99999999)
                stegoDES = CryptoSteganography(str(keyDES))
                stegoDES.hide(image, output, secrettext)

                msg = Message(
                "HideO - A Steganography Tool",
                sender ='mgangrade24@gmail.com',
                recipients = [email, session['email']])
                msg.body = "Hello HideO User,\n" + "Here are the details of secret data sent to you." + "\n\nSent By: " + session['name'] + "\n\nKey: "+ str(keyDES) +"\n\nAlgorithm Used: DES"

                with app.open_resource(output) as fp:
                    msg.attach(output, "image/png", fp.read())
            

                mail.send(msg)
                flash("Mail has been sent successfully!","success")






        # User is loggedin show them the home page
        return render_template('txttoimg.html')
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))

@app.route("/imgintoimg",methods=["GET","POST"])
def imgintoimg():
    # Check if user is loggedin
    if 'loggedin' in session:

        if request.method=="POST":
            email = request.form['email']

            cover = request.files['cover']
            cover.save(secure_filename(cover.filename))
            coverimg = cover.filename.replace(" ","_")
            coverimg = coverimg.replace("(","")
            coverimg = coverimg.replace(")","")

            secret = request.files['secret']
            secret.save(secure_filename(secret.filename))
            secretimg = secret.filename.replace(" ","_")
            secretimg = secretimg.replace("(","")
            secretimg = secretimg.replace(")","")
            output = 'output_' + secretimg + "+" + coverimg

            n_bits = 6

            image_to_hide = Image.open(secretimg)
            image_to_hide_in = Image.open(coverimg)

            steganography.encode(image_to_hide, image_to_hide_in, n_bits).save(output)


            msg = Message(
                "HideO - A Steganography Tool",
                sender ='mgangrade24@gmail.com',
                recipients = [email, session['email']])

            msg.body = "Hello HideO User,\n" + "Here are the details of secret data sent to you." + "\n\nSent By: " + session['name'] + "\n\nYou can upload this image to HideO to get the secret image hidden in it."

            with app.open_resource(output) as fp:
                msg.attach(output, "image/png", fp.read())
            

            mail.send(msg)
            flash("Mail has been sent successfully!","success")



        # User is loggedin show them the home page
        return render_template('imgintoimg.html')
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))


@app.route("/imgfromimg",methods=["GET","POST"])
def imgfromimg():
    # Check if user is loggedin
    if 'loggedin' in session:

        if request.method=="POST":

            image = request.files['img[]']
            # path = os.path.join(app.config['UPLOAD_FOLDER'],image.filename)
            image.save(secure_filename(image.filename))
            img = image.filename.replace(" ","_")
            img = img.replace("(","")
            img = img.replace(")","")
            output = "unmerged_" + img

            n_bits = 6

            image_to_decode = Image.open(img)
            steganography.decode(image_to_decode, n_bits).save(output)

            print(output)
            print(img)

            return render_template('secretimg.html',stego=img,secret=output,name=session['name'])

            




        # User is loggedin show them the home page
        return render_template('imgfromimg.html')
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))


@app.route("/secretimg")
def secretimg():
    # Check if user is loggedin
    if 'loggedin' in session:
        # User is loggedin show them the home page
        return render_template('secretimg.html')
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))


@app.route("/imgtotxt",methods=['GET','POST'])
def imgtotxt():
    # Check if user is loggedin
    if 'loggedin' in session:

        if request.method=="POST":
            key = request.form['key']
            algo = request.form['algo']
            file = request.files['img[]']
            file.save(secure_filename(file.filename))
            image = file.filename.replace(" ","_")
            image = image.replace("(","")
            image = image.replace(")","")


            if algo=='aes':
                stegoAES = CryptoSteganography(str(key))
                secret = stegoAES.retrieve(image)

                if secret == "None":
                    flash("Entered Key Is Wrong Or The Image Has No Information Hidden!","danger")
                    return redirect(url_for('imgtotxt'))

                return render_template('secretmsg.html', secret=secret, name=session['name'])
            

            if algo=='des':
                stegoDES = CryptoSteganography(str(key))
                secret = stegoDES.retrieve(image)

                if secret == "None":
                    flash("Entered Key Is Wrong Or The Image Has No Information Hidden!","danger")
                    return redirect(url_for('imgtotxt'))

                return render_template('secretmsg.html', secret=secret, name=session['name'])



        # User is loggedin show them the home page
        return render_template('imgtotxt.html')
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))


@app.route("/secretmsg")
def secretmsg():
    # Check if user is loggedin
    if 'loggedin' in session:
        # User is loggedin show them the home page
        return render_template('secretmsg.html')
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

    app.run(debug=True,port=8081)
