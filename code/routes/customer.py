from flask import Flask, render_template, request, redirect, url_for, session, Blueprint
customer_bp = Blueprint('customer', __name__)

@customer_bp.route("/customer")
def customer():
    return render_template("CusMain.html")
