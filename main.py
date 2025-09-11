from flask import Flask, render_template, request, redirect, url_for
import pymysql
app = Flask (__name__)

connection = pymysql.connect(
    host = "localhost",
    user = "root",
    password = "@ma7iy@_mak1li0*#1j+",
    database = "j4e_pwds_db",
    cursorclass = pymysql.cursors.DictCursor
    )
cursor = connection.cursor()

@app.route("/")
def landing_page():
    return render_template("index.html")

@app.route("/SignUp", methods=['POST'])
def signup_process():
    name = request.form.get("name")
    email = request.form.get("email")
    password = request.form.get("password")
    
    sql="INSERT INTO registration (PWDs_name, PWDs_email, PWDs_password) VALUES(%s, %s, %s)"
    cursor.execute(sql, (name, email, password))  
    connection.commit()

    return redirect(url_for("home_page"))

@app.route("/Login")
def login_page():
    return render_template("login.html")

@app.route("/LogIn", methods=['POST'])
def login_process():
    email = request.form.get("name")
    password = request.form.get("password")
    
    sql="SELECT * FROM registration WHERE PWDs_name=%s AND PWDs_password=%s"
    cursor.execute(sql, (email, password))
    
    connection.commit()

    return redirect(url_for("home_page"))

@app.route("/Home")
def home_page():
    return render_template("home.html")


if __name__ == "__main__":
    app.run(debug=True)