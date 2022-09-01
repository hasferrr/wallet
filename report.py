from flask import Blueprint, render_template, request, redirect

from helpers import login_required


report_page = Blueprint('report_page', __name__, template_folder='templates')


@report_page.route("/report", methods=["GET", "POST"])
@login_required
def report():
    return render_template("report.html")
