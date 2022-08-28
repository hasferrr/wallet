from flask import Flask, render_template, request, redirect, session
from flask_session import Session

from account import account_page


# Configure app
app = Flask(__name__)
app.register_blueprint(account_page)
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure session
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


@app.route("/")
def index():
    return render_template("index.html")


@app.errorhandler(404)
def page_not_found(error):
    return render_template("error.html", error="404 Page not found"), 404
