from flask import Flask, render_template, request, redirect, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from function import login_required, connect_db

# Configure app
app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure session
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
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
        rows = cur.execute("SELECT * FROM users WHERE username=:name", {"name":request.form.get("username").lower()})
        rows = list(rows.fetchall())

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0][2], request.form.get("password")):
            return render_template("error.html", error="invalid username or password")

        # Remember which user has logged in
        session["user_id"] = rows[0][0]

        # Redirect user to home page
        con.close()
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    """Forget user id"""

    if session.get("user_id") is not None:
        session.pop("user_id")

    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
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

        # Username validation
        if not username.isascii():
            return render_template("error.html", error="invalid char(s)")

        specialchars = "`~!@#$%^&*()-=+}{[\|];:,.<>/?' " + '"'
        for i in range(len(username)):
            if username[i] in specialchars:
                return render_template("error.html", error="symbols are not allowed (except: _ )")

        del username
        username = request.form.get("username").lower()

        # Query data
        con, cur = connect_db()
        users_database = cur.execute("SELECT username FROM users")

        # Ensure submitted username not already taken
        for user in users_database.fetchall():
            if user[0] == username:
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


@app.errorhandler(404)
def page_not_found(error):
    return render_template("error.html", error="404 Page not found"), 404
