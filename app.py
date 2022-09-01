from datetime import datetime

from flask import Flask, render_template, request, redirect, session
from flask_session import Session

from account import account_page
from helpers import connect_db, idr, get_date_now, get_time_now, date_validation, time_validation


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
        label = 'This Month'

    # User reached route via POST
    else:
        # If all time button was clicked
        if request.form.get('filter_btn') == 'alltime':
            date_filter = '%'
            label = 'All Time'

        # If all this year button was clicked
        elif request.form.get('filter_btn') == 'thisyear':
            year_now = str(datetime.now().year)
            date_filter = year_now + '%'
            label = 'This Year'

        # If user select the date to filter
        elif request.form.get('filter_btn') == 'between':
            start_date = request.form.get('start_date')
            end_date = request.form.get('end_date')
            label = 'Between ' + start_date + ' and ' + end_date

        # If user using search form
        elif request.form.get('search_btn') == 'search_btn':
            keyword = request.form.get('search_vield').strip()
            label = f'Keyword : "{keyword}"'

        # Prevent error 500 for magical reason
        else:
            date_filter = '0'
            label = None

    # Query records
    if request.form.get('filter_btn') == 'between':
        res = cur.execute("SELECT * FROM records WHERE user_id = ? AND date BETWEEN ? AND ?",
                          (session["user_id"], start_date, end_date))

    elif request.form.get('search_btn') == 'search_btn':
        res = cur.execute("SELECT * FROM records WHERE user_id = ? AND (account_name LIKE ? OR description LIKE ?)",
                          (session["user_id"], f"%{keyword}%", f"%{keyword}%"))

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
    return render_template("home.html", records=records, income=income, expense=expense, label=label, date_now=get_date_now(), time_now=get_time_now())


@app.route("/record", methods=["GET", "POST"])
def record():

    # User reached route via POST
    if request.method == 'POST':

        btnradio = request.form.get('btnradio')
        account_name = request.form.get('account_name')
        amount = request.form.get('amount')
        date = request.form.get('date')
        time = request.form.get('time')
        description = request.form.get('description')

        # Ensure input is a valid value
        # Check type (Income or Expense)
        if btnradio not in ['Income', 'Expense']:
            return render_template("error.html", error="invalid type")

        # Check category / account_name
        con, cur = connect_db()
        res = cur.execute("SELECT name FROM account")

        account_name_list = []
        for i in res:
            account_name_list.append(i[0])

        if account_name not in account_name_list:
            return render_template("error.html", error="invalid account name")

        # Check amount
        if float(amount) < 0:
            return render_template("error.html", error="invalid amount")

        # Check date and time
        if date_validation(date) == 1:
            return render_template("error.html", error="invalid value")

        elif time_validation(time) == 1:
            return render_template("error.html", error="invalid value")

        # Set max length of description
        if len(description) > 50:
            return render_template("error.html", error="too long")

        # Store to database
        cur.execute("INSERT INTO records (user_id,account_name,account_category,date,time,description,amount) VALUES (?,?,?,?,?,?,?)",
                    (session["user_id"], account_name, btnradio, date, time, description, amount))
        con.commit()

        con.close()
        return redirect("/")

    # User reached route via GET
    else:
        return redirect("/")


@app.errorhandler(404)
def page_not_found(error):
    return render_template("error.html", error="404 Page not found"), 404
