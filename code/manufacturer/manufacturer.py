import os
from flask import Flask, render_template, request, redirect, url_for, session, Blueprint
manufacturer_bp = Blueprint('manufacturer', __name__, 
                        template_folder='templates',
                        static_folder='static')
from datetime import datetime, timedelta
from werkzeug.utils import redirect
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired
from pymongo import MongoClient
import sys
from bson.objectid import ObjectId

database_address = os.environ.get("DATABASE_ADDRESS", "localhost")
database_port = os.environ.get("DATABASE_PORT", "27017")
client = MongoClient(database_address, int(database_port))

db = client.MowerDB

requests = db.Requests
product = db.Products
tickets = db.Service_Tickets
mowers = db.Mower
provider = db.Service_Provider
areas = db.Areas


#Form for adding products
class ProductForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    # external_system_slug = StringField("External System Slug", validators=[DataRequired()])
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
    #Takes data from databse and sends to html
    request_data = requests.find()
    return render_template("requesthq.html", title = "Request Page", data = request_data,)


@manufacturer_bp.route("/requestinfohq", methods = ["GET", "POST"])
def requestinfo():
    #verifies that logged in user is a manufacturer

    providers = list(provider.find())
    products = list(product.find())

    role = session["role"]
    if role != "manufacturer":
        return redirect("/logout")

    #Takes data from databse and sends to html in this case specific request
    if "request_id" in session:
        requestId = session["request_id"]
        request = requests.find({"_id": ObjectId(requestId)})[0]  

        return render_template("requestinfohq.html", request=request, providers = providers, products = products)
    else:
        return redirect(url_for("manufacturer.manufacturer"))
    
@manufacturer_bp.route("/remove/<id>", methods = ["GET", "POST"])
def remove(id):
  #Finds data from database and removes it 
    requests.find_one_and_delete({"_id": ObjectId(id)})


    return redirect(url_for("manufacturer.requesthq"))

@manufacturer_bp.route("/requestinfo/service", methods = ["POST"])
def service():
    id = request.form["requestId"]
    data = requests.find_one({"_id": ObjectId(id)})
    print(data["Type"])
  #Match case to see what type of request we are dealing with
    match data["Type"]:
        case 'mowerReq':
            providerId = ObjectId(data["ProviderId"])
            productId = ObjectId(request.form["productId"])
            externalSystemSlug = request.form["externalSystemSlug"]

            mowers.insert_one({"ProviderId": providerId, "ProductId": productId, "ExternalSystemSlug": externalSystemSlug, "AreaIds": [], "Xpos": 0, "Ypos": 0})
            
            requests.find_one_and_update({"_id": ObjectId(id)}, {'$set': {"Completed": True}})
            return redirect(url_for("manufacturer.requesthq"))
        case "newArea":        
            areaId = ObjectId(data["AreaId"])
            customerId = ObjectId(data["CustomerId"])
            providerId = ObjectId(request.form["providerId"])

            dueDate = datetime.now() + timedelta(days=2)
            tickets.insert_one({"AreaId": areaId, "CustomerId": customerId, "DateCreated": datetime.now(), "Content": "newArea", "Completed": False, "DueDate": dueDate, "ProviderId": providerId, "WorkTaskId": "placeholder-work-id"})
            areas.find_one_and_update({"_id": areaId}, {"$set": {"ProviderId": providerId}})
            requests.find_one_and_update({"_id": ObjectId(id)}, {'$set': {"Completed": True}})
            return redirect(url_for("manufacturer.requesthq"))
   

@manufacturer_bp.route("/pick/<id>", methods = ["GET", "POST"])
def pick(id):
    #verifies that logged in user is a manufacturer
    role = session["role"]
    if role != "manufacturer":
        return redirect("/logout")
    
    dataprod = product.find_one({"_id": ObjectId(id)})
    productId = ObjectId(dataprod["_id"])

    mowers.insert_one({"ProductId": productId})
    
    return redirect(url_for("manufacturer.requesthq"))


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
    
    #find serviceprovider accounts and put their information into array for frontend -->
    AccCursor = db.Accounts.find({"ProviderId": {"$ne": None} }) #list(db.Accounts.find({"ProviderId": {"$ne": None} }))
    SePrCursor = db.Service_Provider
    provider_accounts = []

    #for each serviceprovider, add their information to array (that will be presented to frontend)
    for document in AccCursor:
        another_account = {}
        another_account["ProviderId"]= document["ProviderId"]
        another_account["Email"] = document["Email"]

        #find relevant infromation from serviceprovider table and add them to 
        SePrInfo = SePrCursor.find_one({"_id": document["ProviderId"]})
        another_account["Name"] = SePrInfo["Name"]
        another_account["Phone"] = SePrInfo["Phone"]
        #---



        provider_accounts.append(another_account)
    #<--
    
    return render_template("ServiceproviderList.html", provider_accounts = provider_accounts, title = "Provider List")

@manufacturer_bp.route("/infoServiceProvider.html", methods = ["GET", "POST"])
def infoServiceProvider():
    #verifies that logged in user is a manufacturer
    role = session["role"]
    if role != "manufacturer":
        return redirect("/logout")
    
    areaCursor = db.Areas.find({"ProviderId": ObjectId(request.form["serviceproviderID"]) })
    assignedAreas = []
    for area in areaCursor:
        assignedAreas.append(area)

    return render_template("infoServiceProviderhq.html", title = "Assigned Areas", assignedAreas = assignedAreas)

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
    #Takes content from product DB and sends it to the html
    product_data = product.find()
    return render_template("productlisthq.html", title = "Product List", product=product_data)


@manufacturer_bp.route("/productpick.html")
def productpick():
    #verifies that logged in user is a manufacturer
    role = session["role"]
    if role != "manufacturer":
        return redirect("/logout")
    #Takes content from product db and sends it to html
    product_data = product.find()
    return render_template("productpick.html", title = "Product List", product=product_data)

@manufacturer_bp.route("/addproducthq.html", methods=("GET", "POST"))
def addproduct():
    #verifies that logged in user is a manufacturer
    role = session["role"]
    if role != "manufacturer":
        return redirect("/logout")
    #takes the data entered in the form and adds to product db
    if request.method == "POST":
        form = ProductForm(request.form)
        add_name = form.name.data
        add_spec = form.spec.data
        add_description = form.description.data

        product.insert_one({
            "Name": add_name,
            "Spec": add_spec,
            "Description": add_description,
        })
        return redirect(url_for("manufacturer.productlist"))
    else:
        form = ProductForm()
    return render_template("addproducthq.html", title = "Add Product", form = form)


@manufacturer_bp.route("/enter", methods = ["GET", "POST"])
def enterrequest():
    print(request.form, file=sys.stderr)
    #controll that request id exists, send to requestinfo page if it does
    if "requestId" in request.form:
        requestId = request.form["requestId"]

        session["request_id"] = requestId
        return redirect(url_for("manufacturer.requestinfo"))
    else:
        return redirect(url_for("manufacturer.manufacturer"))
    

@manufacturer_bp.route("/removeprod/<id>", methods = ["GET", "POST"])
def removeprod(id):
    #Removes product with id from html (clicked product)
    product.find_one_and_delete({"_id": ObjectId(id)})


    return redirect(url_for("manufacturer.productlist"))
