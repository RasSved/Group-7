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

@customer_bp.route("/area", methods = ["GET", "POST"])
def area():
    print(request.form, file=sys.stderr)
    if "areaId" in request.form:
        areaId = request.form["areaId"]
        area = areas.find({"_id": ObjectId(areaId)})[0]    # find area where id is the same as area clicked
        #print(area, file=sys.stderr)
        return render_template("CusArea.html", area=area)
    else:
        return redirect(url_for("customer.customer"))



