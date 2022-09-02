from flask import Blueprint, render_template, request, redirect, session

from helpers import login_required, connect_db, account_name_list, idr


report_page = Blueprint('report_page', __name__, template_folder='templates')


@report_page.route("/report", methods=["GET", "POST"])
@login_required
def report():
    """Financial report"""

    # Connect to database
    con, cur = connect_db()

    # Query data [('Income', 10000.0), ('Gifts', 10000.0)] and store to list
    res = cur.execute("SELECT account_name, amount FROM records WHERE user_id = ? AND account_category = ?", (session["user_id"], "Income"))
    income_name_amount = list(res.fetchall())

    res = cur.execute("SELECT account_name, amount FROM records WHERE user_id = ? AND account_category = ?", (session["user_id"], "Expense"))
    expense_name_amount = list(res.fetchall())

    # Get all account_name and place to store total amount for each account [['Income', 0], ['Gifts', 0], ['Others', 0]]
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

    # Format amount as IDR
    income_list_amount_formatted = list(income_list_totalamount)
    i = 0
    length = len(income_list_amount_formatted)
    while i < length:
        income_list_amount_formatted[i][1] = idr(income_list_amount_formatted[i][1])
        i += 1

    expense_list_amount_formatted = list(expense_list_totalamount)
    i = 0
    length = len(expense_list_amount_formatted)
    while i < length:
        expense_list_amount_formatted[i][1] = idr(expense_list_amount_formatted[i][1])
        i += 1

    total_income_formatted = idr(total_income)
    total_expense_formatted = idr(total_expense)

    con.close()
    return render_template("report.html")
