from flask import Flask, render_template, request, redirect, url_for,flash, session, send_file, jsonify
import pymysql, io
app = Flask (__name__)
app.secret_key = 'j4e_secret_key'
SESSION_USER_ID = 'user_id'

connection = pymysql.connect(
    host = "localhost",
    user = "root",
    password = "@ma7iy@_mak1li0*#1j+",
    database = "j4e_pwds_db",
    cursorclass = pymysql.cursors.DictCursor
    )
cursor = connection.cursor()

# ----------------- PATIENT CORNER ----------------- #

#   landing page ##
@app.route("/")
def landing_page():
    return render_template("index.html")

# logout route ##

@app.route("/Logout")
def logout():
    session.pop('user_id', None)
    flash("You have been logged out.")
    return redirect(url_for('landing_page'))

# signup route ## 

@app.route("/SignUp", methods=['GET', 'POST'])
def signup_page():
    next_page = request.args.get('next') or request.form.get('next')

    if request.method == 'POST':
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")

        # ✅ Check if user already exists
        cursor.execute("SELECT * FROM user WHERE User_email = %s", (email,))
        existing_user = cursor.fetchone()
        if existing_user:
            flash("Email already exists. Please log in instead.")
            # Redirect to login, preserving 'next' parameter (e.g. appointment)
            return redirect(url_for('login_page', next=next_page))

        # ✅ Create new user
        cursor.execute(
            "INSERT INTO user (User_name, User_email, User_password) VALUES (%s, %s, %s)",
            (name, email, password)
        )
        connection.commit()

        # ✅ Get user ID
        cursor.execute("SELECT User_id FROM user WHERE User_email = %s", (email,))
        user = cursor.fetchone()

        if user:
            # Auto-login after signup
            session['user_id'] = user['User_id']

            # Create empty profile
            cursor.execute(
                "INSERT INTO profile (Full_name, Email, Contact, User_id) VALUES (%s, %s, %s, %s)",
                (name, email, " ", user['User_id'])
            )
            connection.commit()
            flash("Account created successfully! You are now logged in.")

            # ✅ Redirect logic
            if next_page and next_page.startswith('/appointment'):
                return redirect(next_page)
            else:
                return redirect(url_for('home_page'))

        flash("Signup failed. Please try again.")
        return redirect(url_for('signup_page', next=next_page))

    # Render signup page with next-page memory
    return render_template("index.html", next_page=next_page)


# login route ##

@app.route('/Login', methods=['GET', 'POST'])
def login_page():
    next_page = request.args.get('next') or request.form.get('next')

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        cursor.execute("SELECT * FROM user WHERE User_email = %s", (email,))
        user = cursor.fetchone()

        if not user:
            flash("Email not found.")
            return redirect(url_for('login_page', next=next_page))
        elif user['User_password'] != password:
            flash("Incorrect password.")
            return redirect(url_for('login_page', next=next_page))
        else:
            session['user_id'] = user['User_id']
            flash("Login successful!")

            # ✅ Redirect to appointment if they came from Book Appointment
            if next_page and next_page.startswith('/appointment'):
                return redirect(next_page)

            # Otherwise, go home
            return redirect(url_for('home_page'))

    return render_template('login.html', next_page=next_page)

@app.route("/check_login")
def check_login():
    if 'user_id' in session:
        return jsonify({"logged_in": True})
    else:
        return jsonify({"logged_in": False})



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

# profile pages ##

@app.route("/Profile")
def profile_page():
    user_id = session.get('user_id')
    if not user_id:
        flash("Please log in to view your profile.")
        return redirect(url_for('landing_page'))

    cursor.execute("SELECT * FROM profile WHERE User_id = %s", (user_id,))
    profile = cursor.fetchone()

    cursor.execute("""
        SELECT appointment_id, fullname, appt_date, appt_time, service, doctor, notes, status, decline_message
        FROM appointment
        WHERE User_id = %s
        ORDER BY appt_date DESC
    """, (user_id,))
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
        cursor.execute("DELETE FROM appointment WHERE User_id = %s", (user_id,))
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

# cancel appointment route ##

@app.route("/cancel_appointment/<int:appt_id>", methods=["POST"])
def cancel_appointment(appt_id):
    user_id = session.get("user_id")
    if not user_id:
        flash("Please log in to cancel appointments.")
        return redirect(url_for("landing_page"))

    # Only allow cancel if appointment is 'Accepted'
    cursor.execute("""
        SELECT status FROM appointment 
        WHERE appointment_id = %s AND user_id = %s
    """, (appt_id, user_id))
    appt = cursor.fetchone()

    if not appt:
        flash("Appointment not found.")
        return redirect(url_for("profile_page"))

    if appt["status"] != "Accepted":
        flash("You can only cancel accepted appointments.")
        return redirect(url_for("profile_page"))

    cursor.execute(
        "DELETE FROM appointment WHERE appointment_id=%s AND user_id=%s",
        (appt_id, user_id)
    )
    connection.commit()
    flash("Appointment cancelled successfully.")
    return redirect(url_for("profile_page"))


   ## privacy policy page ##

@app.route("/Policy-Privacy")
def policy_page():
    return render_template("privacy-policy.html")

# ----------------- ASSISTANT CORNER ----------------- #

def get_cursor():
    return connection.cursor()

@app.route("/Assistant")
def assistant_page():
    return render_template("admin.html")

@app.route("/Assistant-Logout")
def assistant_logout():
    session.pop('user_id', None)
    flash("You have been logged out.")
    return redirect(url_for('assistant_page'))


# Assistant login route ##

@app.route("/assistant_login", methods=["POST"])
def assistant_login():
    email = request.form.get("email")
    password = request.form.get("password")

    cursor = get_cursor()
    cursor.execute("SELECT * FROM assistant WHERE Assistant_email = %s", (email,))
    assistant = cursor.fetchone()

    if not assistant:
        flash("Email not found.")
        return redirect(url_for("assistant_page"))
    elif assistant['Assistant_password'] != password:
        flash("Incorrect password.")
        return redirect(url_for("assistant_page"))
    else:
        session['assistant_id'] = assistant['Assistant_id']
        flash("Assistant login successful!")
        return redirect(url_for("view_appointments"))

# View appointments route ##

@app.route("/appointments-view", methods=["GET"])
def view_appointments():
    cursor = get_cursor()
    sql = "SELECT * FROM appointment WHERE status = 'Pending'"
    cursor.execute(sql)
    appointments = cursor.fetchall()
    return render_template("appointments-view.html", appointment=appointments)

# Accept appointment route ##

@app.route("/appointments-accept", methods=["POST"])
def accept_appointment():
    appointment_id = request.form.get("appointment_id")
    if not appointment_id:
        flash("No appointment ID provided.")
        return redirect(url_for("view_appointments"))

    cursor = connection.cursor()
    cursor.execute("""
        UPDATE appointment 
        SET status = %s, decline_message = NULL 
        WHERE appointment_id = %s
    """, ("Accepted", appointment_id))
    connection.commit()
    flash("Appointment accepted successfully.")
    return redirect(url_for("view_appointments"))

# Decline appointment route ##

@app.route("/appointments-decline", methods=["POST"])
def decline_appointment():
    appointment_id = request.form.get("appointment_id")
    decline_message = request.form.get("decline_message")

    if not appointment_id:
        flash("No appointment ID provided.")
        return redirect(url_for("view_appointments"))

    if not decline_message or decline_message.strip() == "":
        flash("Please provide a reason for declining.")
        return redirect(url_for("view_appointments"))

    cursor = connection.cursor()
    cursor.execute("""
        UPDATE appointment 
        SET status = %s, decline_message = %s 
        WHERE appointment_id = %s
    """, ("Declined", decline_message, appointment_id))
    connection.commit()
    flash("Appointment declined with message.")
    return redirect(url_for("view_appointments"))


if __name__ == "__main__":
    app.run(debug=True)