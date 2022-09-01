import sqlite3
from functools import wraps
from datetime import datetime
from string import ascii_letters, digits
from random import choice

from flask import redirect, session


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
