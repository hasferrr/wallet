import csv

from flask import Blueprint, render_template, request, session, send_file

from helpers import login_required, connect_db


export_page = Blueprint('export_page', __name__, template_folder='templates')


@export_page.route("/export", methods=["GET", "POST"])
@login_required
def export():
    """Export records to csv file"""

    # User reached route via POST
    if request.method == "POST":

        # If user click 'download' button, export data
        if request.form.get("export_now"):

            # Connect to database
            con, cur = connect_db()
            res = cur.execute("SELECT account_name,account_category,date,time,description,amount FROM records WHERE user_id = ?",
                                (session["user_id"],))

            # Header of csv file
            header = ("category", "type", "date", "time", "description", "amount")

            # Start writing
            with open(f'export/{session["user_id"]}.csv','w') as new_file:
                write_file = csv.writer(new_file)

                write_file.writerow(header)

                for i in res:
                    write_file.writerow(i)

            con.close()

        else:
            return render_template("error.html", error="what are you doing")

        return send_file(f"export/{session['user_id']}.csv", as_attachment=False, download_name="export.csv")

    # User reached route via GET
    else:
        return render_template("export.html")
