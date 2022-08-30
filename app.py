from datetime import datetime

from flask import Flask, render_template, request, redirect, session
from flask_session import Session

from account import account_page
from helpers import connect_db, idr


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
    # If user has not been loged in
    if session.get("user_id") is None:
        return render_template("index.html")

    # User logged in
    con, cur = connect_db()

    # Query records
    year_now = str(datetime.now().year)
    month_now = str(datetime.now().month)
    this_month = year_now + '%' + month_now + '%'
    res = cur.execute("SELECT * FROM records WHERE user_id = ? AND date LIKE ?", (session["user_id"], this_month))
    res = list(res)

    # Sum income and expenses
    income = 0
    expense = 0
    for i in res:
        if i[3] == 'Income':
            income += i[7]
        else:
            expense += i[7]

    # Format amount as IDR
    records = []
    for i in res:
        i = list(i)
        i[7] = idr(i[7])
        records.append(i)

    income = idr(income)
    expense = idr(expense)

    con.close()
    return render_template("home.html", records=records, income=income, expense=expense, time='This Month')


@app.errorhandler(404)
def page_not_found(error):
    return render_template("error.html", error="404 Page not found"), 404
