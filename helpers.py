import sqlite3
from functools import wraps
from datetime import datetime
from string import ascii_letters, digits
from random import choice

from flask import redirect, session
import matplotlib.pyplot as plt
from numpy import arange as arange


def login_required(f):
    """
    Login Required Decorator
    https://flask.palletsprojects.com/en/2.2.x/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


def connect_db(db="wallet.db"):
    con = sqlite3.connect(db)
    cur = con.cursor()
    return con, cur


def username_validation(username):
    if not username.isascii():
        return 1
    specialchars = "`~!@#$%^&*()-=+}{[\|];:,.<>/?' " + '"'
    for i in range(len(username)):
        if username[i] in specialchars:
            return 2
    return 0


def idr(value):
    # Format value as IDR
    value = f"Rp{value:,.2f}"
    rupiah = value.replace(".", "#")
    rupiah = rupiah.replace(",", ".")
    rupiah = rupiah.replace("#", ",")
    return rupiah


def get_date_now():

    now = datetime.now()

    # Set date_now
    day = now.day
    if day < 10:
        day = f"0{day}"
    month = now.month
    if month < 10:
        month = f"0{month}"
    year = now.year

    date_now = f"{year}-{month}-{day}"
    return date_now


def get_time_now():

    now = datetime.now()

    # Set time_now
    hour = now.hour
    if hour < 10:
        hour = f"0{hour}"
    minute = now.minute
    if minute < 10:
        minute = f"0{minute}"

    time_now = f"{hour}:{minute}"
    return time_now


def date_validation(date_text):
    """
    How do I validate a date string format in python?
    https://stackoverflow.com/questions/16870663/how-do-i-validate-a-date-string-format-in-python
    """
    try:
        datetime.strptime(date_text, '%Y-%m-%d')
        return 0
    except ValueError:
        return 1


def time_validation(time_text):
    try:
        datetime.strptime(time_text, '%H:%M')
        return 0
    except ValueError:
        return 1


def id_generator(size=32, chars=ascii_letters + digits):
    """
    Random string generation with upper case letters and digits
    https://stackoverflow.com/questions/2257441/random-string-generation-with-upper-case-letters-and-digits
    """
    return ''.join(choice(chars) for i in range(size))


def account_name_list(selected='', plug=''):
    # Query
    con, cur = connect_db()
    res = cur.execute("SELECT * FROM account")

    # Assign to list for each account_name (category) and its selected option if any
    income_list = []
    expense_list = []
    for i in res:
        if i[0] == 'Income':
            if i[1] == selected:
                income_list.append([i[1], 'selected'])
            else:
                income_list.append([i[1], plug])
        else:
            if i[1] == selected:
                expense_list.append([i[1], 'selected'])
            else:
                expense_list.append([i[1], plug])

    con.close()
    return income_list, expense_list


def bublesort_list_of_list_rev(input):

    # Copy list of list
    array = []
    for i in input:
        array.append(list(i))

    # Bubble sort
    length = len(array)
    swap_counter = -1

    while swap_counter != 0:
        swap_counter = 0
        i = 0
        while i < length - 1:
            # If 2 adjacent array not in order, swap them and add 1 to swap_counter
            if array[i][1] > array[i + 1][1]:
                temp = array[i]
                array[i] = array[i + 1]
                array[i + 1] = temp
                del temp
                swap_counter += 1
            i += 1

    return array


def horizontal_bar(height, bars, file_name="foo", bar_color='#69b3a2'):
    """
    Plotting a Horizontal Barplot using Matplotlib
    https://www.python-graph-gallery.com/2-horizontal-barplot
    """
    # Example
    # height = [30, 120, 5505, 180, 450]
    # bars = ('A', 'B', 'C', 'D', 'E')
    y_pos = arange(len(bars))

    # Create horizontal bars
    plt.barh(y_pos, height, color=bar_color)

    # Create names on the x-axis
    plt.yticks(y_pos, bars)

    # Save graphic
    plt.tight_layout()
    plt.savefig("static/img/" + file_name + ".png")
