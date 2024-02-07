from flask import Flask, render_template, request, redirect, url_for, session, Blueprint
manufacturer_bp = Blueprint('manufacturer', __name__, 
                        template_folder='templates',
                        static_folder='static')
from datetime import datetime
from werkzeug.utils import redirect
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired
from pymongo import MongoClient

client = MongoClient('localhost', 27017)

db = client.MowerDB

request = db.Request
product = db.Product


class ProductForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    spec = TextAreaField("Spec", validators=[DataRequired()])
    description = TextAreaField("Description", validators=[DataRequired()])
    submit = SubmitField("Add Product")


@manufacturer_bp.route("/manufacturer")
def manufacturer():
    #verifies that logged in user is a manufacturer
    role = session["role"]
    if role != "manufacturer":
        return redirect("/logout")
    
    return render_template("manmain.html", title = "Home Page")

@manufacturer_bp.route("/mowerpagehq.html")
def mower():
    #verifies that logged in user is a manufacturer
    role = session["role"]
    if role != "manufacturer":
        return redirect("/logout")
    
    return render_template("mowerpagehq.html", title = "Mower Page")



@manufacturer_bp.route("/requesthq.html")
def requesthq():
    #verifies that logged in user is a manufacturer
    role = session["role"]
    if role != "manufacturer":
        return redirect("/logout")
    
    request_data = request.find()
    return render_template("requesthq.html", title = "Request Page", data = request_data,)



@manufacturer_bp.route("/requestinfohq.html/<int:request_id>")
def requestinfo(request_id):
    #verifies that logged in user is a manufacturer
    role = session["role"]
    if role != "manufacturer":
        return redirect("/logout")
    
    request_info = request.find_one({'id': request_id})
    return render_template("requestinfohq.html", title = "Request Info", request_info = request_info)

@manufacturer_bp.route("/customerinfohq.html")
def customerinfo():
    #verifies that logged in user is a manufacturer
    role = session["role"]
    if role != "manufacturer":
        return redirect("/logout")
    
    return render_template("customerinfohq.html", title = "Customer Info")

@manufacturer_bp.route("/providerlisthq.html")
def providerlist():
    #verifies that logged in user is a manufacturer
    role = session["role"]
    if role != "manufacturer":
        return redirect("/logout")
    
    return render_template("providerlisthq.html", title = "Provider List")

@manufacturer_bp.route("/areainfohq.html")
def areainfo():
    #verifies that logged in user is a manufacturer
    role = session["role"]
    if role != "manufacturer":
        return redirect("/logout")
    
    return render_template("areainfohq.html", title = "Area Info")

@manufacturer_bp.route("/productlisthq.html")
def productlist():
    #verifies that logged in user is a manufacturer
    role = session["role"]
    if role != "manufacturer":
        return redirect("/logout")
    
    return render_template("productlisthq.html", title = "Product List")

@manufacturer_bp.route("/addproducthq.html", methods=("GET", "POST"))
def addproduct():
    #verifies that logged in user is a manufacturer
    role = session["role"]
    if role != "manufacturer":
        return redirect("/logout")
    
    if request.method == "POST":
        form = ProductForm(request.form)
        add_name = form.name.data
        add_spec = form.spec.data
        add_description = form.description.data
        submit = form.submit.data

        product.insert_one({
           "name": add_name,
            "spec": add_spec,
            "description": add_description,
            "submit": submit,
            "date_completed": datetime.utcnow()
        })
        return redirect("/productlisthq.html")
    else:
        form = ProductForm()
    return render_template("addproducthq.html", title = "Add Product", form = form)
