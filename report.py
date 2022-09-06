from datetime import datetime

from flask import Blueprint, render_template, request, session

from helpers import login_required, connect_db, account_name_list, idr, horizontal_bar


report_page = Blueprint('report_page', __name__, template_folder='templates')


@report_page.route("/report", methods=["GET", "POST"])
@login_required
def report():
    """Financial report"""

    # Connect to database
    con, cur = connect_db()

    # Query data account_name and its amount
    # If THIS MONTH button was clicked OR
    # User reached route via GET
    if request.form.get('filter_btn') == 'This Month' or request.method == "GET":
        year_now = str(datetime.now().year)
        month_now = str(datetime.now().month)
        date_filter = year_now + '%' + month_now + '%'
        label = 'This Month'

    # If ALL TIME button was clicked
    elif request.form.get('filter_btn') == 'All Time':
        date_filter = '%'
        label = 'All Time'

    # If THIS YEAR button was clicked
    elif request.form.get('filter_btn') == 'This Year':
        year_now = str(datetime.now().year)
        date_filter = year_now + '%'
        label = 'This Year'

    # If LAST 30 DAYS button was clicked
    elif request.form.get('filter_btn') == 'Last 30D':
        label = "Last 30 Days"

    # If user select the date to filter
    elif request.form.get('filter_btn') == 'between':
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        label = 'Between ' + start_date + ' and ' + end_date

    # Prevent error 500 for magical reason
    else:
        date_filter = '0'
        label = None

    # Query records, and store to list ---> [('Income', 10000.0), ('Gifts', 10000.0)]
    if request.form.get('filter_btn') == 'between':
        res = cur.execute("SELECT account_name, amount FROM records WHERE user_id = ? AND account_category = ? AND date BETWEEN ? AND ?",
                            (session["user_id"], "Income", start_date, end_date))
        income_name_amount = list(res.fetchall())

        res = cur.execute("SELECT account_name, amount FROM records WHERE user_id = ? AND account_category = ? AND date BETWEEN ? AND ?",
                            (session["user_id"], "Expense", start_date, end_date))
        expense_name_amount = list(res.fetchall())

    elif request.form.get('filter_btn') == 'Last 30D':
        res = cur.execute("SELECT account_name, amount FROM records WHERE user_id = ? AND account_category = ? AND date BETWEEN date('now','localtime','-31 day') AND date('now','localtime')",
                            (session["user_id"], "Income"))
        income_name_amount = list(res.fetchall())

        res = cur.execute("SELECT account_name, amount FROM records WHERE user_id = ? AND account_category = ? AND date BETWEEN date('now','localtime','-31 day') AND date('now','localtime')",
                            (session["user_id"], "Expense"))
        expense_name_amount = list(res.fetchall())

    else:
        res = cur.execute("SELECT account_name, amount FROM records WHERE user_id = ? AND account_category = ? AND date LIKE ?",
                            (session["user_id"], "Income", date_filter))
        income_name_amount = list(res.fetchall())

        res = cur.execute("SELECT account_name, amount FROM records WHERE user_id = ? AND account_category = ? AND date LIKE ?",
                            (session["user_id"], "Expense", date_filter))
        expense_name_amount = list(res.fetchall())



    # Get all account_name and place to store total amount for each account ---> [['Income', 0], ['Gifts', 0], ['Others', 0]]
    income_list_totalamount, expense_list_totalamount = account_name_list('', 0.0)



    # Store to LIST OF TOTAL AMOUNT for each account, and get its TOTAL
    for i in income_name_amount:
        for j in income_list_totalamount:
            if i[0] == j[0]:
                j[1] += i[1]

    total_income = 0
    for i in income_list_totalamount:
        total_income += i[1]

    for i in expense_name_amount:
        for j in expense_list_totalamount:
            if i[0] == j[0]:
                j[1] += i[1]

    total_expense = 0
    for i in expense_list_totalamount:
        total_expense += i[1]



    # Get percentage per category (Income/Expense)
    j = 0
    for i in income_list_totalamount:
        try:
            income_list_totalamount[j].append(round(i[1] / total_income * 100, 2))
        except ZeroDivisionError:
            income_list_totalamount[j].append(0)
        j += 1

    j = 0
    for i in expense_list_totalamount:
        try:
            expense_list_totalamount[j].append(round(i[1] / total_expense * 100, 2))
        except ZeroDivisionError:
            expense_list_totalamount[j].append(0)
        j += 1



    # Format amount as IDR
    # Copy list
    income_list_amount_f = []
    for i in income_list_totalamount:
        income_list_amount_f.append(list(i))

    # Format amount
    i = 0
    length = len(income_list_amount_f)
    while i < length:
        income_list_amount_f[i][1] = idr(income_list_amount_f[i][1])
        i += 1

    expense_list_amount_f = []
    for i in expense_list_totalamount:
        expense_list_amount_f.append(list(i))

    # Format amount
    i = 0
    length = len(expense_list_amount_f)
    while i < length:
        expense_list_amount_f[i][1] = idr(expense_list_amount_f[i][1])
        i += 1

    # Format total amount
    total_income_f = idr(total_income)
    total_expense_f = idr(total_expense)



    # Get cash flow bar percentage
    if total_income > total_expense:
        income_percent = 100
        try:
            expense_percent = round(total_expense / total_income, 2) * 100
        except ZeroDivisionError:
            expense_percent = 0
        diff = "+ " + idr(total_income - total_expense)

    elif total_income < total_expense:
        expense_percent = 100
        try:
            income_percent = round(total_income / total_expense, 2) * 100
        except ZeroDivisionError:
            income_percent = 0
        diff = "- " + idr(total_expense - total_income)

    else:
        income_percent = 100
        expense_percent = 100
        diff = idr(0)



    # Separate list
    bars_expense = []
    height_expense = []
    for i in reversed(expense_list_totalamount):
        bars_expense.append(i[0])
        height_expense.append(i[1])



    # Plotting a Horizontal Barplot
    if sum(height_expense) == 0:
        img_name = "blank"
    else:
        img_name = str(session["user_id"]) + "e"
        horizontal_bar(height_expense, bars_expense, img_name, bar_color='#e74c3c')


    con.close()
    return render_template("report.html", total_income_f=total_income_f, total_expense_f=total_expense_f, diff=diff, income_percent=income_percent, expense_percent=expense_percent, income_list_amount_f=income_list_amount_f, expense_list_amount_f=expense_list_amount_f, label=label, img_name=img_name)
