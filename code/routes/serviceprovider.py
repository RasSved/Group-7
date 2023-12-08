from flask import Flask, render_template, request, redirect, url_for, Blueprint, session	# Import the Flask class. An instance of this class will be our WSGI application.
serviceprovider_bp = Blueprint('serviceprovider', __name__)

@serviceprovider_bp.route("/serviceprovider")
def serviceprovider():
    return render_template("SePrMain.html")
