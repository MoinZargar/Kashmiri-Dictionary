import os
from flask import Flask,jsonify, redirect, request, session
from user import register_route,login_route,logout_route
from flask import render_template,url_for,Markup
from flask import jsonify
import json
from flask_session import Session
from data.database import data
from data.word import wordofDay
import mysql.connector
from flask_mysqldb import MySQL
app = Flask(__name__)



app.config['MYSQL_HOST'] ='localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] ='Alchemist@123'
app.config['SECRET_KEY'] ='5791628bbdedcr13ce0c676dfde280ba245', 
app.config['PORT']='3306'
def create_database():
   conn = mysql.connector.connect(
      host=app.config['MYSQL_HOST'],
      user=app.config['MYSQL_USER'],
      password=app.config['MYSQL_PASSWORD'],
      port=app.config['PORT'],
     
         
   )

   cursor = conn.cursor()
   
   cursor.execute("CREATE DATABASE IF NOT EXISTS kashir")
   cursor.execute("USE kashir")
   cursor.execute(
   '''CREATE TABLE IF NOT EXISTS user 
   (id INT AUTO_INCREMENT PRIMARY KEY,
   username VARCHAR(80) NOT NULL , email VARCHAR(120) NOT NULL
   UNIQUE, 
   password VARCHAR(160) NOT NULL,
   role INT DEFAULT 0
   )'''
   )
   cursor.execute(
   '''CREATE TABLE IF NOT EXISTS dictionary( 
        id INT(11) NOT NULL AUTO_INCREMENT,
        title VARCHAR(100) NOT NULL,
        pos VARCHAR(1000),
        englishMeaning VARCHAR(1000),
        kashmiriMeaning VARCHAR(1000),
        englishExample VARCHAR(10000),
        PRIMARY KEY (id)
   )'''
   )

   cursor.execute(
      '''CREATE TABLE IF NOT EXISTS word (
         id INT(11) NOT NULL AUTO_INCREMENT,
         title VARCHAR(100) NOT NULL,
         pos VARCHAR(1000),
         englishMeaning VARCHAR(1000),
         kashmiriMeaning VARCHAR(1000),
         englishExample VARCHAR(10000),
         PRIMARY KEY (id)
      )'''    
      
   )
   cursor.execute(
   '''CREATE TABLE IF NOT EXISTS contribution( 
        id INT(11) NOT NULL AUTO_INCREMENT,
        username VARCHAR(80) NOT NULL ,
        email VARCHAR(120) NOT NULL,
        title VARCHAR(100) NOT NULL,
        pos VARCHAR(1000),
        kashmiriMeaning VARCHAR(1000),
        englishExample VARCHAR(10000),
        status INT DEFAULT 0,
        PRIMARY KEY (id)
   )'''
   )
   cursor.close()
   conn.close()
   

# Call this function once in your application code to create the database and table.
create_database()

app.config['MYSQL_DB'] = 'kashir'
mysql = MySQL(app)
mysql = MySQL(app)

# admin route for rendering admin dashboard
@app.route("/admin", methods=['GET','POST'])
def admin():
   username=session.get('name')
   role=session.get('admin')
   
   conn = mysql.connect
   cursor = conn.cursor()
   
   if role:
     
     cursor.execute("SELECT * FROM contribution WHERE status = %s", (0,))
     result=cursor.fetchall()
     cursor.close()
     conn.close()
     return render_template("admin.html",result=result,username=username)
   else:
      return redirect(url_for('login'))
   
#route for adding or deleting new words suggested by user
@app.route("/admin_action", methods=['GET','POST'])
def admin_action():
   id=request.form.get("id")
   row_id=int(id)
   action=request.form.get("action")
   conn = mysql.connect
   cursor = conn.cursor()
   if action=="delete":
      #Status 1 here means that the entry has been rejected by admin
      cursor.execute("UPDATE contribution SET status=%s WHERE id=%s",(1,row_id))
      conn.commit()
      #Status 0 here represents the entries that are pending and not added or deleted by admin
      cursor.execute("SELECT * FROM contribution where status=%s",(0,))
      result = cursor.fetchall()
      return list(result)
   elif action=="add":
      #Status 2 here means that the entry has been approved/added to db by admin
      cursor.execute("UPDATE contribution SET status=%s WHERE id=%s",(2,row_id))
      conn.commit()

      #fetch the row to be added from contribution table
      cursor.execute("SELECT * FROM contribution where id=%s",(row_id,))
      result=cursor.fetchone()

      #Add a new word in main table(dictionary table)
      cursor.execute("INSERT INTO dictionary (title, pos,kashmiriMeaning, englishExample) VALUES (%s, %s, %s, %s)",(result[3],result[4],result[5],result[6]))
      conn.commit()

      #Status 0 here represents the entries that are pending and not added or deleted by admin
      cursor.execute("SELECT * FROM contribution where status=%s",(0,))
      results = cursor.fetchall()
      return list(results)
   cursor.close()
   conn.close()

#route for user dashboard

@app.route("/dashboard", methods=['GET','POST'])
def dashboard(): 
  logged_in=session.get('logged_in')
  if logged_in:
   username=session.get('name')
   email=session.get('logged_in')
   conn = mysql.connect
   cursor = conn.cursor()
   cursor.execute("SELECT * FROM contribution WHERE email=%s",(email,))
   result=cursor.fetchall()
   cursor.close()
   conn.close()
   return render_template("user_dashboard.html",result=result,username=username) 
  else:
     return redirect(url_for('login'))
#route for homepage
@app.route("/home", methods=['GET','POST'])
@app.route("/",methods=['GET','POST']) 
def home():
   #inserting data in dictionary and word table
   role=session.get('admin')
   conn = mysql.connect
   cursor = conn.cursor()
   query = "SELECT COUNT(*) FROM dictionary"
   cursor.execute(query)
   count1 = cursor.fetchone()[0]
   query = "SELECT COUNT(*) FROM word"
   cursor.execute(query)
   count2 = cursor.fetchone()[0]
   #Tables are empty inserting first time
   if count1 == 0 and count2==0:
        # Convert the list of dictionaries to a list of tuples 
        data_tuples = [(entry['title'], entry['pos'], entry['englishMeaning'], entry['kashmiriMeaning'], entry['englishExample']) for entry in data]
        query = "INSERT INTO dictionary (title, pos, englishMeaning, kashmiriMeaning, englishExample) VALUES (%s, %s, %s, %s, %s)"
        cursor.executemany(query, data_tuples)
        conn.commit()
        # Convert the list of dictionaries to a list of tuples
        data_tuples2 = [(entry['title'], entry['pos'], entry['englishMeaning'], entry['kashmiriMeaning'], entry['englishExample']) for entry in wordofDay]
        query = "INSERT INTO word (title, pos, englishMeaning, kashmiriMeaning, englishExample) VALUES (%s, %s, %s, %s, %s)"
        cursor.executemany(query, data_tuples2)
        conn.commit()
        cursor.close()
        conn.close()

    #Fetching random word from word table for Word of the day
   conn = mysql.connect
   cursor = conn.cursor()
   cursor.execute("SELECT * FROM word ORDER BY RAND() LIMIT 1")
   results = cursor.fetchone()
   cursor.close()
   conn.close()
   name=session.get('name')   
   logged_in=session.get('logged_in') 
   return render_template('index.html',results=results,logged_in=logged_in,name=name,role=role)

   
 #route for searched words           
@app.route('/result',methods=['POST'])
def result():
   conn = mysql.connect
   cursor = conn.cursor()
   inputWord=request.form.get('word')
   query = "SELECT * FROM dictionary WHERE title = %s"
   cursor.execute(query, (inputWord,))
   results= cursor.fetchall()
   cursor.close()
   conn.close()
   return jsonify(results)

# route for suggestion list
@app.route('/suggestion',methods=["POST"])
def get_suggestion():
   inputValue = request.form.get("inputValue")
   conn = mysql.connect
   cursor = conn.cursor()
   cursor.execute('SELECT * FROM dictionary WHERE LOWER(title) LIKE %s', (inputValue.lower() + '%',))
   result= cursor.fetchall()
   cursor.close()
   conn.close()
   return jsonify(result)


@app.route('/contribute',methods=['GET','POST'])
def contribute():
   logged_in=session.get('logged_in')
   if logged_in:
         if request.method=="POST":
            username=session.get('name')
            email=session.get('logged_in')
            print(username)
            EnglishWord=request.form['EnglishWord'] 
            KashmiriMeaning=request.form['KashmiriMeaning']
            EnglishExample=request.form['EnglishExample']
            pos=request.form['pos']
            conn = mysql.connect
            cursor = conn.cursor()
            cursor.execute("INSERT INTO contribution (username,email,title, pos, kashmiriMeaning, englishExample) VALUES(%s,%s,%s,%s,%s,%s)",(username,email,EnglishWord,pos,KashmiriMeaning,EnglishExample))
            conn.commit()
            cursor.close()
            conn.close()
            return redirect('/display')

         return render_template("contribute.html",url="display")
         
   else:
      return redirect(url_for('login'))
 
@app.route('/display')
def display(): 
   return render_template("submission.html")

@app.route("/login",methods=['GET','POST']) 
def login():
   
   return login_route()
@app.route("/register",methods=['GET','POST']) 
def register():
   return register_route()
@app.route('/logout')
def logout(): 
   # Remove the logged_in key from the session
   return logout_route()
if __name__=="__main__":
  app.run(debug=True)