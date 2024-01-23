from flask import Flask, render_template, request, redirect, url_for, session, Blueprint
customer_bp = Blueprint('customer', __name__, 
                        template_folder='templates',
                        static_folder='static')

from pymongo import MongoClient
from bson.objectid import ObjectId
import sys


# Setting up/connecting to database
client = MongoClient('localhost', 27017)
db = client.MowerDB

# Single definition for table, change later
areas = db.Areas


@customer_bp.route("/", methods=["GET", "POST"])
def customer():
    all_areas = areas.find()   # get entire collection
    return render_template("CusMain.html", areas = all_areas)

@customer_bp.route("/add_area", methods=["POST"])
def addArea():
    #print(request.form, file=sys.stderr)
    if request.method == "POST":
        if all(k in request.form for k in ("sub", "grassLength", "address")): # if all needed keys are present
            print(request.form, file=sys.stderr)
            sub = request.form["sub"]
            grassLength = request.form["grassLength"]
            address = request.form["address"]
            areas.insert_one({"Sub": sub, "grassLength": grassLength, "CustomerId": 0, "ServiceId": None, "Address": address})      
    return redirect(url_for("customer.customer"))

@customer_bp.route("/edit_area", methods=["POST"])
def editArea():
    #print(request.form, file=sys.stderr)
    if request.method == "POST":
        if all(k in request.form for k in ("sub", "grassLength")): # if all needed keys are present
            print(request.form, file=sys.stderr)
            sub = request.form["sub"]
            grassLength = request.form["grassLength"]
            areas.insert_one({"Sub": sub, "grassLength": grassLength, "CustomerId": 0, "ServiceId": None, "Address": areas.area('Address') })      
    return redirect(url_for("customer.customer"))

@customer_bp.route("/enter", methods = ["GET", "POST"])
def enterArea():
    print(request.form, file=sys.stderr)
    if "areaId" in request.form:
        areaId = request.form["areaId"]
        # find area where id is the same as area clicked
        #print(area, file=sys.stderr)
        session["area_id"] = areaId
        return redirect(url_for("customer.area"))
    else:
        return redirect(url_for("customer.customer"))

@customer_bp.route("/area", methods = ["GET", "POST"])
def area():
    if "area_id" in session:
        areaId = session["area_id"]
        area = areas.find({"_id": ObjectId(areaId)})[0]    # find area where id is the same as area clicked
        return render_template("CusArea.html", area=area)
    else:
        return redirect(url_for("customer.customer"))
    

@customer_bp.route("/area/nav", methods = ["GET", "POST"])  # Depending on which button was clicked from navigation form, navigate
def areaNav():
    print(request.form, file=sys.stderr)
    page = request.form["navBar"]
    if page == "map":
        return redirect(url_for("customer.map"))
    elif page == "schedule":
        return redirect(url_for("customer.schedule"))
    elif page == "settings":
        return redirect(url_for("customer.settings"))
    elif page == "home":
        return redirect(url_for("customer.area"))
    else:
        return redirect(url_for("customer.customer"))

@customer_bp.route("/area/map", methods = ["GET", "POST"])
def map():
    print(request.form, file=sys.stderr)
    if "area_id" in session:
        areaId = session["area_id"]
        area = areas.find({"_id": ObjectId(areaId)})[0]    # find area where id is the same as area clicked
        #print(area, file=sys.stderr)
        return render_template("CusMap.html", area=area)
    else:
        return redirect(url_for("customer.customer"))

@customer_bp.route("/area/schedule", methods = ["GET", "POST"])
def schedule():
    print(request.form, file=sys.stderr)
    if "area_id" in session:
        areaId = session["area_id"]
        area = areas.find({"_id": ObjectId(areaId)})[0]    # find area where id is the same as area clicked
        #print(area, file=sys.stderr)
        return render_template("CusSched.html", area=area)
    else:
        return redirect(url_for("customer.customer"))

@customer_bp.route("/area/settings", methods = ["GET", "POST"])
def settings():
    print(request.form, file=sys.stderr)
    if "area_id" in session:
        areaId = session["area_id"]
        area = areas.find({"_id": ObjectId(areaId)})[0]    # find area where id is the same as area clicked
        #print(area, file=sys.stderr)
        return render_template("CusSett.html", area=area)
    else:
        return redirect(url_for("customer.customer"))
    
    


