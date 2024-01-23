from flask import Flask, render_template, request, redirect, url_for, session, Blueprint
manufacturer_bp = Blueprint('manufacturer', __name__, 
                        template_folder='templates',
                        static_folder='static')
from flask import render_template, flash, request
from datetime import datetime
from werkzeug.utils import redirect
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired
from flask import Flask
from pymongo import MongoClient

client = MongoClient('localhost', 27017)

db = client.NewCluster

guides = db.sample_guides


class ProductForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    spec = TextAreaField("Spec", validators=[DataRequired()])
    description = TextAreaField("Description", validators=[DataRequired()])
    submit = SubmitField("Add Product")


@manufacturer_bp.route("/manufacturer")
def manufacturer():
    return render_template("manmain.html", title = "Home Page")

@manufacturer_bp.route("/mowerpagehq.html")
def mower():
    return render_template("mowerpagehq.html", title = "Mower Page")



@manufacturer_bp.route("/requesthq.html")
def requesthq():
    data_from_mongodb = guides.find()
    #requests = []
    #for request in guides.find().sort("date_completed", -1):
    #    request["_id"] =str(request["_id"])
    #    request["date_completed"] = request["date_completed"].strftime("%b %d %Y %H:%M%S")
    #    requests.append(request)
    return render_template("requesthq.html", title = "Request Page", data = data_from_mongodb)



@manufacturer_bp.route("/requestinfohq.html")
def requestinfo():
    return render_template("requestinfohq.html", title = "Request Info")

@manufacturer_bp.route("/customerinfohq.html")
def customerinfo():
    return render_template("customerinfohq.html", title = "Customer Info")

@manufacturer_bp.route("/providerlisthq.html")
def providerlist():
    return render_template("providerlisthq.html", title = "Provider List")

@manufacturer_bp.route("/areainfohq.html")
def areainfo():
    return render_template("areainfohq.html", title = "Area Info")

@manufacturer_bp.route("/productlisthq.html")
def productlist():
    return render_template("productlisthq.html", title = "Product List")

@manufacturer_bp.route("/addproducthq.html", methods=("GET", "POST"))
def addproduct():
    if request.method == "POST":
        form = ProductForm(request.form)
        add_name = form.name.data
        add_spec = form.spec.data
        add_description = form.description.data
        submit = form.submit.data

        guides.insert_one({
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
