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


@app.route("/", methods=["GET", "POST"])
def index():
    # If user has not been loged in
    if session.get("user_id") is None:
        return render_template("index.html")

    # If user logged in
    # Connect to database
    con, cur = connect_db()

    # User reached route via GET
    if request.method == "GET":

        year_now = str(datetime.now().year)
        month_now = str(datetime.now().month)
        date_filter = year_now + '%' + month_now + '%'
        time = 'This Month'

    # User reached route via POST
    else:
        # If all time button was clicked
        if request.form.get('filter_btn') == 'alltime':
            date_filter = '%'
            time = 'All Time'

        # If all this year button was clicked
        elif request.form.get('filter_btn') == 'thisyear':
            year_now = str(datetime.now().year)
            date_filter = year_now + '%'
            time = 'This Year'

        # If user select the date to filter
        elif request.form.get('filter_btn') == 'between':
            start_date = request.form.get('start_date')
            end_date = request.form.get('end_date')
            time = 'Between ' + start_date + ' and ' + end_date

        # Prevent error 500
        else:
            date_filter = '%'
            time = None

    # Query records
    if request.form.get('filter_btn') == 'between':
        res = cur.execute("SELECT * FROM records WHERE user_id = ? AND date BETWEEN ? AND ?", (session["user_id"], start_date, end_date))
    else:
        res = cur.execute("SELECT * FROM records WHERE user_id = ? AND date LIKE ?", (session["user_id"], date_filter))
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
    return render_template("home.html", records=records, income=income, expense=expense, time=time)


@app.errorhandler(404)
def page_not_found(error):
    return render_template("error.html", error="404 Page not found"), 404
