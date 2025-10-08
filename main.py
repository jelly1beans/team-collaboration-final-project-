from flask import Flask, render_template, request, redirect, url_for,flash, session, send_file
from admin import admin_bp
import pymysql, io
app = Flask (__name__)
app.register_blueprint(admin_bp)
app.secret_key = 'your_secret_key'
SESSION_USER_ID = 'user_id'

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

@app.route("/Logout")
def logout():
    session.pop('user_id', None)
    flash("You have been logged out.")
    return redirect(url_for('landing_page'))


## signup route ##
@app.route("/SignUp", methods=['POST'])
def signup_process():
    name = request.form.get("name")
    email = request.form.get("email")
    password = request.form.get("password")
    
    cursor.execute("INSERT INTO user (User_name, User_email, User_password) VALUES(%s, %s, %s)",
                   (name, email, password))  
    connection.commit()

    cursor.execute("SELECT User_id FROM user WHERE User_email = %s", (email,))
    user = cursor.fetchone()
    user_id = user['User_id']
    session['user_id'] = user_id

    # auto create profile row
    cursor.execute("INSERT INTO profile (Full_name, Email, Contact, User_id) VALUES (%s, %s, %s, %s)",
                   (name, email, " ", user_id))
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
        session['user_id'] = user['User_id']   # ✅ Save login session
        flash("Login successfully!")
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

## profile pages ##

@app.route("/Profile")
def profile_page():
    user_id = session.get('user_id')
    if not user_id:
        flash("Please log in to view your profile.")
        return redirect(url_for('landing_page'))

    cursor.execute("SELECT * FROM profile WHERE User_id = %s", (user_id,))
    profile = cursor.fetchone()

    cursor.execute("SELECT * FROM appointment WHERE User_id = %s", (user_id,))
    appointments = cursor.fetchall()

    return render_template("profile.html", profile=profile, appointments=appointments)


@app.route("/profile", methods=["POST"])
def edit_profile_page():
    user_id = session.get("user_id")
    if not user_id:
        flash("Please log in to edit your profile.")
        return redirect(url_for("landing_page"))

    action = request.form.get("action-btn")
    fullname = request.form.get("fullname")
    contact_number = request.form.get("contact_number")
    email = request.form.get("email")
    file = request.files.get("profileImage")
    if not fullname or not contact_number or not email:
        flash("Full name, contact number, and email are required.")
        return redirect(url_for("profile_page"))
    # Read image only if uploaded
    image_data = file.read() if file and file.filename else None

    if action == "delete-btn":
        # delete profile + user
        cursor.execute("DELETE FROM profile WHERE User_id = %s", (user_id,))
        cursor.execute("DELETE FROM user WHERE User_id = %s", (user_id,))
        connection.commit()
        session.clear()
        flash("Account and profile deleted.")
        return redirect(url_for("landing_page"))

    elif action == "save-btn":
        cursor.execute("SELECT * FROM profile WHERE User_id = %s", (user_id,))
        existing = cursor.fetchone()

        if existing:
            # If new image uploaded, update it too
            if image_data:
                cursor.execute(
                    """UPDATE profile 
                       SET Full_name=%s, Contact=%s, Email=%s, Image=%s 
                       WHERE User_id=%s""",
                    (fullname, contact_number, email, image_data, user_id),
                )
            else:
                # Keep old image if not replaced
                cursor.execute(
                    """UPDATE profile 
                       SET Full_name=%s, Contact=%s, Email=%s 
                       WHERE User_id=%s""",
                    (fullname, contact_number, email, user_id),
                )
        else:
            # Insert new profile row (must include Image, even if None)
            cursor.execute(
                """INSERT INTO profile (Full_name, Contact, Email, Image, User_id) 
                   VALUES (%s, %s, %s, %s, %s)""",
                (fullname, contact_number, email, image_data, user_id),
            )

        connection.commit()
        flash("Profile saved.")

    return redirect(url_for("profile_page"))


@app.route('/profile/image/<int:user_id>')
def get_profile_image(user_id):
    cursor.execute("SELECT Image FROM profile WHERE User_id = %s", (user_id,))
    profile = cursor.fetchone()

    if profile and profile['Image']:
        return send_file(io.BytesIO(profile['Image']), mimetype='image/jpeg')
    else:
        return redirect("https://img.icons8.com/ios-filled/100/FFFFFF/user.png")

## home page ##
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

@app.route("/appointment", methods=["GET", "POST"])
def appointment_page():
    if request.method == "GET":
        return render_template("appointment.html")

    user_id = session.get("user_id")
    if not user_id:
        flash("Please log in first.")
        return redirect(url_for("landing_page"))

    fullname = request.form["fullname"]
    gender = request.form["gender"]
    contact = request.form["contact"]
    email = request.form["email"]
    date = request.form["date"]
    time = request.form["time"]
    service = request.form["service"]
    doctor = request.form["doctor"]
    notes = request.form.get("notes", "")

    cursor.execute("""INSERT INTO appointment
                      (user_id, fullname, gender, contact, email, appt_date, appt_time, service, doctor, notes)
                      VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                   (user_id, fullname, gender, contact, email, date, time, service, doctor, notes))
    connection.commit()
    flash("Appointment booked successfully.")
    return redirect(url_for("profile_page"))

@app.route("/cancel_appointment/<int:appt_id>", methods=["POST"])
def cancel_appointment(appt_id):
    user_id = session.get("user_id")
    if not user_id:
        flash("Please log in to cancel appointments.")
        return redirect(url_for("landing_page"))
    cursor.execute(
        "DELETE FROM appointment WHERE appointment_id=%s AND user_id=%s",(appt_id, user_id))
    connection.commit()
    if cursor.rowcount > 0:
        flash("Appointment cancelled.")
    else:
        flash("Could not cancel appointment — not found or not yours.")
    return redirect(url_for("profile_page"))


## privacy policy page ##

@app.route("/Policy-Privacy")
def policy_page():
    return render_template("privacy-policy.html")

@app.route("/Admin")
def admin_page():
    return render_template("admin.html")

if __name__ == "__main__":
    app.run(debug=True)