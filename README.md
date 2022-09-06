# Wallet

Track your income and expenses.

## Description

`Wallet` is a web application for **recording personal financial reports**, both income and expenses. This application will store the user's income and expenses with the date and time (when the user got or spent the money), category (what income or expense category), the amount in [Rupiah](https://en.wikipedia.org/wiki/Indonesian_rupiah), and description the user typed.

![demo1](/static/img/demo1.png)

![demo2](/static/img/demo2.png)

## Feature

There are some features that you can use in this `Wallet`

### Register and Login

*Let's make an account!*

### Display

Display every record on the Home in the form of a table.

1. Search

     **Search** for data and display records based on the appropriate category or description.

1. Filters

     **Filter** the records based on date, or use the `filter button` that has been provided.

### Record

1. Record

    **Record** income and expenses. You can also choose a category that has been provided or if the record does not match the list provided, the `Other` category is also available in the category options.

1. Edit

    When you realize to enter the wrong data, or *oh no I forgot to type the description*, you can **edit** the record by clicking the pencil button to the right of each row shown.

1. Delete

    **Delete** the record by clicking the cross button on the left of each row that is displayed.

### Report

1. Cash Flow

    The **total income**, **total expenses**, and **the difference between the two** will be displayed in the form of a bar on a specific date.

1. Income and Expenses

    Income and expenses **for each category** will be displayed and their percentage for each type (income or expenses) for a specific date.

1. Horizontal Bar plot

    A **horizontal bar plot** of expenses will be displayed and can be used for comparison in each category.

### Export

All data containing `category`, `type`, `date`, `time`, `description`, and `amount` can be exported to a ***CSV file*** and downloaded by the user.

### Settings

1. Change the username
1. Change the password
1. Delete the account and all data

## Project Files Description

Wallet is a web application created using `Python3`, `Flask`, and `SQLite3`.

**Python Files:**

- **[app.py](app.py)** - contains the configuration of the Flask app; Blueprint that links to `account.py`, `export.py`, and `report.py`; and sessions. Financial data will be recorded here. Edit, Delete records route, and error handlers are also declared here.
- **[account.py](account.py)** - contains routes for `register`, `login`, `logout`, and `settings` (which contains change username, change password, and delete account routes)
- **[export.py](export.py)** - serves to export data where the data is based on the logged-in user, retrieved from the database using `sqlite3`, and writes a CSV file that then can be downloaded by the user.
- **[report.py](report.py)** - contains the report page where the data is first queried from the database filtered by date. Furthermore, the data is processed and calculated in this python file such as summing and formatting total income. Then, a horizontal bar plot is created using `myplotlib.pyplot` plot and saved as an image, which is then displayed in an HTML file.
- **[helpers.py](helpers.py)** - contains function declarations for other python files to implement abstractions and minimize the use of the same code for different implementations.

**Templates:**

- **[layout.html](/templates/layout.html)** - is an outline arrangement of all HTML files. All HTML files extend this file to display the same head, navbar, and other settings for all HTML files.
- **[HTML file inside `/templates/include/` directory](/templates/include/)** - does not extend layout.html. The file is used for several other HTML files with the Jinja2 `include` keyword like `{% include "include/record.html" %}` in the HTML file section that wants to include this HTML file code.
- **[Other HTML files](/templates/)** - functions like the name of the HTML file itself and will be rendered from a python file using Flask's `render_template`.
- **[CSS](/static/light.css)** - I am using Bootstrap 5 with `Flaty` theme from [Bootswatch](https://bootswatch.com/).
- **[JS](templates/include/record.html)** - I only use JavaScript code on [record.html](templates/include/record.html). So, I do not separate the script into a JS file in the static directory.

Why do I just replace the `username` and `hash` in the users table with the **`-`** character instead of deleting the row from the database when the user deletes the account? The reason is that the `session` I am using is the session user's id which means that the `id` of the user will be taken as a session. However, the id in the users table is ***autoincremented***. Therefore, if a row is deleted from the `users` table when the user deletes his/her account, the `id` under it will be reduced so that other users will use the session ***user minus 1*** of his/her user id, not his/her own id. That's the reason why I didn't delete the row from the `users` table.

## Credit

by HasFer :)

> This project was created to complete the Final Project on the CS50x course
