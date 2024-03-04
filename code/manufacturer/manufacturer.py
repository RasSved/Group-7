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
import sys
from bson.objectid import ObjectId

client = MongoClient('localhost', 27017)

db = client.MowerDB

requests = db.Requests
product = db.Products



class ProductForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    spec = TextAreaField("Spec", validators=[DataRequired()])
    description = TextAreaField("Description", validators=[DataRequired()])
    submit = SubmitField("Add Product")


@manufacturer_bp.route("/manufacturer", methods = ["GET", "POST"])
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



@manufacturer_bp.route("/requesthq.html", methods = ["GET", "POST"])
def requesthq():
    #verifies that logged in user is a manufacturer
    role = session["role"]
    if role != "manufacturer":
        return redirect("/logout")
    
    request_data = requests.find()
    return render_template("requesthq.html", title = "Request Page", data = request_data,)


@manufacturer_bp.route("/requestinfohq", methods = ["GET", "POST"])
def requestinfo():
    #verifies that logged in user is a manufacturer
    role = session["role"]
    if role != "manufacturer":
        return redirect("/logout")
    
    if "request_id" in session:
        requestId = session["request_id"]
        request = requests.find({"_id": ObjectId(requestId)})[0]  

        return render_template("requestinfohq.html", request=request)
    else:
        return redirect(url_for("manufacturer.manufacturer"))
    
@manufacturer_bp.route("/remove/<id>", methods = ["GET", "POST"])
def remove(id):
    requests.find_one_and_delete({"_id": ObjectId(id)})


    return redirect(url_for("manufacturer.requesthq"))

@manufacturer_bp.route("/service/", methods = ["GET", "POST"])
def service():
    data = request.json
    match data["type"]:
        case "mowerReq":
            redirect(url_for("manufacturer.manufactorer"))
            #När typen av request är mowerReq
            #kolla provider
            #kolla mover
            #skicka ticket med provider och mower uppdaterade  
        case "Change Provider":
            redirect(url_for("manufacturer.requesthq"))


        case "newArea":
            redirect(url_for("manufacturer.requesthq"))
            #När newArea
            #kolla kund 
            #Kolla area 
            #lägg till ticket med kund och area
    return "", 204


@manufacturer_bp.route("/customerinfohq", methods = ["GET", "POST"])
def customerinfo():
    #verifies that logged in user is a manufacturer
    role = session["role"]
    if role != "manufacturer":
        return redirect("/logout")
    
    if "customer_id" in session:
        customerId = session["customer_id"]
        customer = requests.find({"Customerid": str(customerId)})[0]    

        return render_template("customerinfohq.html", customer=customer)
    else:
        return redirect(url_for("manufacturer.manufacturer"))

@manufacturer_bp.route("/ServiceproviderList.html", methods = ["GET", "POST"])
def ServiceproviderList():
    #verifies that logged in user is a manufacturer
    role = session["role"]
    if role != "manufacturer":
        return redirect("/logout")
    
    #finnd serviceprovider accounts and put their information into array for frontend -->
    AccCursor = db.Accounts.find({"ProviderId": {"$ne": None} })
    SePrCursor = db.Service_Provider
    provider_accounts = []

    #for each serviceprovider, add their information to array (that will be presented to frontend)
    for document in AccCursor:
        another_account = {}
        another_account["ProviderId"]= document["ProviderId"]
        another_account["Email"] = document["Email"]

        #find relevant infromation from serviceprovider table and add them to 
        SePrInfo = SePrCursor.find_one({"Email": document["Email"]})
        another_account["Name"] = SePrInfo["Name"]
        another_account["Phone"] = SePrInfo["Phone"]
        #---



        provider_accounts.append(another_account)
    #<--


    print("providers:    ", provider_accounts)
    
    return render_template("ServiceproviderList.html", provider_accounts = provider_accounts, title = "Provider List")

@manufacturer_bp.route("/infoServiceProvider.html", methods = ["GET", "POST"])
def infoServiceProvider():
    #verifies that logged in user is a manufacturer
    role = session["role"]
    if role != "manufacturer":
        return redirect("/logout")
    
    areaCursor = db.Areas.find({"ProviderId": request.form["serviceproviderID"] })
    assignedAreas = []
    for area in areaCursor:
        assignedAreas.append(area)

    return render_template("infoServiceProviderhq.html", title = "Serviceprovider Information", assignedAreas = assignedAreas)

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


@manufacturer_bp.route("/enter", methods = ["GET", "POST"])
def enterrequest():
    print(request.form, file=sys.stderr)
    if "requestId" in request.form:
        requestId = request.form["requestId"]

        session["request_id"] = requestId
        return redirect(url_for("manufacturer.requestinfo"))
    else:
        return redirect(url_for("manufacturer.manufacturer"))
