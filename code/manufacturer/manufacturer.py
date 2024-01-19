from flask import Flask, render_template, request, redirect, url_for, session, Blueprint
manufacturer_bp = Blueprint('manufacturer', __name__, 
                        template_folder='templates',
                        static_folder='static')

@manufacturer_bp.route("/manufacturer")
def manufacturer():
    return render_template("ManMain.html")
