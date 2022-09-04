from flask import Blueprint, render_template, request, redirect, session, flash
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import login_required, connect_db, username_validation, del_temp_files

"""
Modular Applications with Blueprints
https://flask.palletsprojects.com/en/2.2.x/blueprints/
"""
account_page = Blueprint('account_page', __name__, template_folder='templates')


@account_page.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Ensure that user log out first before log in
    if session.get("user_id") is not None:
        return render_template("error.html", error="please log out first")

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username and password was submitted
        if not request.form.get("username"):
            return render_template("error.html", error="must provide username")

        if not request.form.get("password"):
            return render_template("error.html", error="must provide password")

        # Query database for username
        con, cur = connect_db()
        rows = cur.execute("SELECT * FROM users WHERE username=:name", {"name": request.form.get("username").lower()})
        rows = list(rows.fetchall())

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0][2], request.form.get("password")):
            con.close()
            return render_template("error.html", error="invalid username or password")

        # Remember which user has logged in
        session["user_id"] = rows[0][0]

        # Redirect user to home page
        con.close()
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@account_page.route("/logout")
@login_required
def logout():
    """Forget user id"""

    # Delete temp files
    del_temp_files()

    # Pop session
    if session.get("user_id") is not None:
        session.pop("user_id")

    return redirect("/")


@account_page.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # Ensure that user log out first before register
    if session.get("user_id") is not None:
        return render_template("error.html", error="please log out first")

    # User reached route via POST
    if request.method == "POST":

        # Ensure username and password was submitted
        username = request.form.get("username")
        if not username:
            return render_template("error.html", error="must provide username")

        password = request.form.get("password")
        if not password or not request.form.get("confirmation"):
            return render_template("error.html", error="must provide password")

        # Check length
        if len(username) > 26 or len(username) < 3:
            return render_template("error.html", error="too long/short")
        if len(password) < 8:
            return render_template("error.html", error="password at least 8 chars length")

        # Confirmation
        if password != request.form.get("confirmation"):
            return render_template("error.html", error="password doesn't match")

        # Username Validation
        validity = username_validation(username)
        if validity == 1:
            return render_template("error.html", error="invalid char(s)")
        elif validity == 2:
            return render_template("error.html", error="symbols are not allowed (except: _ )")

        del username
        username = request.form.get("username").lower()

        # Query data
        con, cur = connect_db()
        users_database = cur.execute("SELECT username FROM users")

        # Ensure submitted username not already taken
        for user in users_database.fetchall():
            if user[0] == username:
                con.close()
                return render_template("error.html", error="username is already taken")

        # Add them to users table in database
        hash = generate_password_hash(password)
        cur.execute("INSERT INTO users (username, hash) VALUES (?, ?)", (username, hash))
        con.commit()

        # Set session
        session["user_id"] = cur.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchall()[0][0]

        con.close()
        return redirect("/")

    # User reached route via GET
    else:
        return render_template("register.html")


@account_page.route("/settings", methods=["GET", "POST"])
@login_required
def settings():
    """Settings"""

    if request.method == "POST":
        if request.form["button"] == "Change Username":
            return redirect("/settings/username")

        elif request.form["button"] == "Change Password":
            return redirect("/settings/password")

        elif request.form["button"] == "Delete Account":
            return redirect("/settings/delete")

    return render_template("settings.html")


@account_page.route("/settings/password", methods=["GET", "POST"])
@login_required
def changepass():
    """Change the password"""

    if request.method == "POST":
        # Ensure all form was submitted
        if not request.form.get("old_password"):
            return render_template("error.html", error="must provide old password")

        if not request.form.get("new_password") or not request.form.get("confirmation"):
            return render_template("error.html", error="must provide new password")

        # Password at least 8 chars length
        if len(request.form.get("new_password")) < 8:
            return render_template("error.html", error="password at least 8 chars length")

        # Confirmation
        if request.form.get("new_password") != request.form.get("confirmation"):
            return render_template("error.html", error="password doesn't match")

        # Query database by session id
        con, cur = connect_db()
        user = cur.execute("SELECT * FROM users WHERE id = ?", (session["user_id"],))
        user = list(user.fetchall())

        # Check inputted old password
        if not check_password_hash(user[0][2], request.form.get("old_password")):
            con.close()
            return render_template("error.html", error="old password doesn't match")

        # Replace (change) the password into database
        hashes_password = generate_password_hash(request.form.get("new_password"))
        cur.execute("UPDATE users SET hash = ? WHERE id = ?", (hashes_password, session["user_id"]))
        con.commit()

        con.close()
        flash("Password was changed successfully!")
        return redirect("/settings/password")

    else:
        return render_template("changepass.html")


@account_page.route("/settings/username", methods=["GET", "POST"])
@login_required
def changeusername():

    if request.method == "POST":
        # Ensure form submitted
        new = request.form.get("new_username")
        if not new:
            return render_template("error.html", error="type your new username")

        # Username Validation
        validity = username_validation(new)
        if validity == 1:
            return render_template("error.html", error="invalid char(s)")
        elif validity == 2:
            return render_template("error.html", error="symbols are not allowed (except: _ )")

        del new
        new = request.form.get("new_username").lower()

        # Connect to sqlite3 db
        con, cur = connect_db()

        # Check apakan new username sudah ada di database atau belum
        old_user = cur.execute("SELECT username FROM users WHERE username = ?", (new,))
        old_user = list(old_user.fetchall())

        # Jika ada, return error
        if not old_user == []:
            con.close()
            return render_template("error.html", error="username is already taken")

        # Jika tidak ada, ganti username
        cur.execute("UPDATE users SET username = ? WHERE id = ?", (new, session["user_id"]))
        con.commit()

        con.close()
        flash("Username was changed successfully!")
        return redirect("/settings/username")

    else:
        con, cur = connect_db()
        user = cur.execute("SELECT username FROM users WHERE id = ?", (session["user_id"],)).fetchall()[0][0]
        con.close()
        return render_template("changeusername.html", user=user)


@account_page.route("/settings/delete", methods=["GET", "POST"])
@login_required
def delete_account():
    """Delete username, hash, records from database"""

    # User reached route via GET
    if request.method == "GET":
        return render_template("delete.html")

    # User reached route via POST
    else:

        # If user click the button
        if request.form.get("del"):

            # Password verif
            if not request.form.get("password"):
                return render_template("error.html", error="must provide password")
            if request.form.get("sayonara") != "sayonara":
                return render_template("error.html", error="please type 'sayonara'")

            # Query user data from database
            con, cur = connect_db()
            rows = cur.execute("SELECT * FROM users WHERE id = ?", (session["user_id"],))

            # Ensure password is correct
            if not check_password_hash(rows.fetchall()[0][2], request.form.get("password")):
                return render_template("error.html", error="invalid password")

            # Delete all data !!!
            # Delete temporary files
            del_temp_files()

            # Delete all records
            cur.execute("DELETE FROM records WHERE user_id = ?", (session["user_id"],))

            # Delete username and hash, but keep the primary key
            cur.execute("UPDATE users SET username = '-', hash = '-' WHERE id = ?", (session["user_id"],))

            # Commit and close connection
            con.commit()
            con.close()

            # Clear session
            session.clear()

            return redirect("/")

        else:
            return render_template("error.html", error="guess what")
