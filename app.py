import sqlite3

from flask import Flask, render_template, request, redirect, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from function import login_required

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
        con, cur = connect_db("wallet.db")
        rows = cur.execute("SELECT * FROM users WHERE username=:name", {"name":request.form.get("username")})
        rows = list(rows.fetchall())

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0][2], request.form.get("password")):
            return render_template("error.html", error="invalid username and/or password")

        # Remember which user has logged in
        session["user_id"] = rows[0][0]

        # Redirect user to home page
        con.close()
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    if session.get("user_id") is not None:
        # Forget user_id
        session.pop("user_id")

    return redirect("/")


@app.errorhandler(404)
def page_not_found(error):
    return render_template("error.html", error="404 Page not found"), 404


def connect_db(db):
    con = sqlite3.connect(db)
    cur = con.cursor()
    return con, cur
