from flask import Flask, render_template, request, redirect, url_for,flash
import pymysql
app = Flask (__name__)
app.secret_key = 'your_secret_key'

connection = pymysql.connect(
    host = "localhost",
    user = "root",
    password = "@ma7iy@_mak1li0*#1j+",
    database = "j4e_pwds_db",
    cursorclass = pymysql.cursors.DictCursor
    )
cursor = connection.cursor()

## routes ##
@app.route("/")
def landing_page():
    return render_template("index.html")

## signup route ##

@app.route("/SignUp", methods=['POST'])
def signup_process():
    name = request.form.get("name")
    email = request.form.get("email")
    password = request.form.get("password")
    
    sql="INSERT INTO user (User_name, User_email, User_password) VALUES(%s, %s, %s)"
    cursor.execute(sql, (name, email, password))  
    connection.commit()

    return redirect(url_for("home_page"))
## login route ##

@app.route("/Login")
def login_page():
    return render_template("login.html")

@app.route('/LogIn', methods=['POST'])
def login():
    email = request.form['email']
    password = request.form['password']

    cursor.execute("SELECT * FROM user WHERE User_email = %s", (email,))
    user = cursor.fetchone()

    if not user:
        flash("Email not found.")
        return redirect(url_for('login_page'))
    elif user['User_password'] != password:
        flash("Incorrect password.")
        return redirect(url_for('login_page'))
    else:
        flash("Login successful!")
        return redirect(url_for('home_page'))
    
## forgot password route ##  
  
@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']
        new_password = request.form['new_password']

        cursor.execute("SELECT * FROM user WHERE User_email = %s", (email,))
        user = cursor.fetchone()

        if user:
            cursor.execute("UPDATE user SET User_password = %s WHERE User_email = %s", (new_password, email))
            connection.commit()
            flash("Password updated successfully.")
            return redirect(url_for('home_page'))
        else:
            flash("Email not found.")
            return redirect(url_for('forgot_password'))

    return render_template('forgot_password.html')

## other pages ##

@app.route("/Profile")
def profile_page():
    return render_template("profile.html")

@app.route("/Home")
def home_page():
    return render_template("home.html")

## services pages ##

@app.route("/Farsighted")
def farsighted_page():
    return render_template("farsighted.html")

@app.route("/Astigmatism")
def astigmatism_page():   
    return render_template("astigmatism.html")

@app.route("/Cataracts")
def cataracts_page():
    return render_template("Cataracts.html")

@app.route("/Nearsighted")
def nearsighted_page():
    return render_template("nearsighted.html")

@app.route("/Services")
def service_page():
    return render_template("Services.html")

@app.route("/Presbyopia")
def presbyopia_page():
    return render_template("Presbyopia.html")

## appointment page ##

@app.route("/Appointment")
def appointment_page():
    return render_template("appointment.html")

@app.route("/AppointmentProcs", methods=['POST'])
def appointment_process():
    fullname = request.form.get("fullname")
    gender = request.form.get("gender")
    contact = request.form.get("contact")
    email = request.form.get("email")
    date = request.form.get("date")
    time = request.form.get("time")
    service = request.form.get("service")
    doctor = request.form.get("doctor")
    reason= request.form.get("notes")

    
    sql="INSERT INTO appointment (full_name, gender, contact, email, date, time, service, doctor, notes) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s)"
    cursor.execute(sql, (fullname, gender, contact, email, date, time, service, doctor, reason))  
    connection.commit()

    
    # Flash message with doctor and reason
    flash(f"You have successfully booked an appointment with Dr. {doctor} for '{service}'.", "success")

    return redirect(url_for("home_page"))

## privacy policy page ##

@app.route("/Policy-Privacy")
def policy_page():
    return render_template("privacy-policy.html")

if __name__ == "__main__":
    app.run(debug=True)