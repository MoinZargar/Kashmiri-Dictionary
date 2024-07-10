import os
from flask import Flask,jsonify, request, session, sessions
from flask import render_template,url_for,Markup,flash,redirect
from forms import RegistrationForm,LoginForm
from flask_session import Session
from flask import jsonify
import json
import bcrypt
from data.database import data
from data.word import wordofDay
import mysql.connector
from flask_mysqldb import MySQL
app = Flask(__name__)




app.config['MYSQL_HOST'] ='dictionary.mysql.database.azure.com'
app.config['MYSQL_USER'] ='moin_bashir'
app.config['MYSQL_PASSWORD'] ='Nouman@321'
app.config['PORT']='3306'
app.config['SESSION_TYPE'] = 'filesystem'


app.config['MYSQL_DB'] = 'kashir'
app.config['SECRET_KEY'] = '5791628bbdedcr13ce0c676dfde280ba245'
mysql = MySQL(app)

#hashing password
def hash_password(password):
    # Generate a salt
    password = password.encode("utf-8")
    hash = bcrypt.hashpw(password, bcrypt.gensalt())
    stored_password = hash.decode("utf-8")
    return stored_password

# Verify a password against the hashed password in the database
def verify_password(password, hashed_password):
    if bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8")):
       return True
    return False

# Register a new user

def register_route():
    form = RegistrationForm()
    if form.validate_on_submit():
        username=form.username.data
        email=form.email.data
        password=form.password.data
        confirm_password=form.confirm_password.data
        hashed_password = hash_password(password)
         # Connect to the database
        conn = mysql.connect
        cursor = conn.cursor()
        # Check if the email already exists
        cursor.execute("SELECT * FROM user WHERE email=%s", (email,))
        result = cursor.fetchone()
        
        # If email already exists, show error message
        if result:
            flash('Email already exists, please login to continue.', 'danger')
            return redirect(url_for('login'))
        # Insert form data into the user table
        cursor.execute("INSERT INTO user (username, email, password) VALUES (%s, %s, %s)", (username, email,hashed_password))
        conn.commit()
        #Create admin
        admin="moinbashir2019@gmail.com"
        cursor.execute("SELECT* FROM user where email=%s",(admin,))
        result=cursor.fetchone()
        if result:
          cursor.execute("UPDATE user SET role = %s WHERE email = %s",(1,admin))
          conn.commit()
        # Close the cursor and connection
        cursor.close()
        conn.close()
        flash(f'Account created for {username}!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html',form=form)

# Login an existing user 
def login_route():
    form=LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = str(form.password.data)
        
        # Connect to the database
        conn = mysql.connect
        cursor = conn.cursor()
        log=False
        
        # Get the hashed password from the database
        cursor.execute("SELECT email FROM user WHERE email=%s", (email,))
        result = cursor.fetchone()
        
        # If there is no matching record, show error message
        if not result:
            flash('Login Unsuccessful. Please check email and password.', 'danger')
            return redirect(url_for('login'))
        cursor.execute("SELECT password,username,role FROM user WHERE email=%s", (email,))
        result = cursor.fetchone()
        hashed_password=str(result[0])
        # Verify the entered password with the hashed password
        if verify_password(password, hashed_password):
            session['logged_in'] = email
            session['name']=result[1]
            session['admin']=result[2]
            #for admin 
            if result[2]==1:
                return redirect(url_for('admin'))
            #for normal user
            else:
            # flash('You have been logged in!', 'success')
             return redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password.', 'danger')
            return redirect(url_for('login'))
    return render_template('login.html', form=form)

# logout route for expiring session 
def logout_route():
    
    # Remove the logged_in key from the session
    session.pop('logged_in', None)
    session.pop('admin', None)
    #Fetching random word from word table for Word of the day
    conn = mysql.connect
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM word ORDER BY RAND() LIMIT 1")
    results = cursor.fetchone()
    cursor.close()
    conn.close()
    return render_template('index.html', logged_in=False,results=results)
# removing login history after logout

def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    return response