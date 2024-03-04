from flask import Flask, render_template, request, redirect, url_for, session, Blueprint
serviceprovider_bp = Blueprint('serviceprovider', __name__ , template_folder='templates', static_folder='static')

from pymongo import MongoClient
from bson.objectid import ObjectId
import sys

from datetime import datetime

# Setting up/connecting to database
client = MongoClient('localhost', 27017)
db = client.MowerDB

# Single definition for table, change later
accounts = db.Accounts
areas = db.Areas
mowers = db.Mower
service_tickets = db.Service_Tickets
requests = db.Requests
products = db.Products
accounts = db.Accounts
services = db.Services


@serviceprovider_bp.route("/", methods=["GET", "POST"])
def serviceprovider():
    # Verifies that logged in user is a serviceprovider
    role = session["role"]
    if role != "serviceprovider":
        return redirect("/logout")

    providerId      = accounts.find_one( {"_id": ObjectId(session["user_id"])} )["ProviderId"]

    all_areas       = areas.find()      # get entire collection
    all_mowers      = list(mowers.find( {"ProviderId": providerId} ))  # get all mowers of specific provider, update to contain object id
    all_products    = list(products.find())
    all_tickets     = list(service_tickets.find( {"ProviderId": providerId, "Completed": False} ))

    for mower in all_mowers:            # Add fields, addresses and name to display on main page
        #print(mower["AreaIds"], file=sys.stderr)
        mower["Addresses"] = []
        mower["Name"] = products.find_one({"_id": mower["ProductId"]})["name"]
        for areaId in mower["AreaIds"]:
            #print(areaId, file=sys.stderr)
            mower["Addresses"].append(areas.find_one({"_id": ObjectId(areaId["AreaId"])})["Address"])

    # Get current time
    current_time = datetime.now()

    for ticket in all_tickets:
        diff = (ticket['DueDate'] - current_time).days
        print(diff)
        if diff < 2:
            ticket["colour"] = 'red'
        elif diff < 8:
            ticket["colour"] = 'orange'
        else:
            ticket["colour"] = 'yellow'

    return render_template("SePrMain.html", title = "Service Provider Mainpage", areas = all_areas, mowers = all_mowers, products = all_products, tickets = all_tickets)


@serviceprovider_bp.route("/enter", methods = ["GET", "POST"])
def enterArea():
    print(request.form, file=sys.stderr)
    if "areaId" in request.form:
        areaId = request.form["areaId"]
        print(areaId, file=sys.stderr)
        session["area_id"] = areaId
        return redirect(url_for("serviceprovider.area"))
    else:
        return redirect(url_for("serviceprovider.serviceprovider"))


@serviceprovider_bp.route("/area", methods = ["GET", "POST"])
def area():
    #verifies that logged in user is a serviceprovider
    role = session["role"]
    if role != "serviceprovider":
        return redirect("/logout")

    if "area_id" in session:
        areaId = session["area_id"]
        curr_area = areas.find_one({"_id": ObjectId(areaId)})    # find area where id is the same as area clicked
        providerId = accounts.find_one({"_id": ObjectId(session["user_id"])})["ProviderId"]

        area_mowers = list(mowers.find({"ProviderId": providerId, "AreaIds": {'$elemMatch': {"AreaId": ObjectId(session["area_id"])}}}))  # get all mowers of specific provider, update to contain object id
        available_mowers = list(mowers.find({"ProviderId": providerId, "AreaIds": {'$not': {'$elemMatch': {"AreaId": ObjectId(session["area_id"])}}}})) # get all mowers that belong to provider but are not on current area

        area_tickets = list( service_tickets.find( {"ProviderId": providerId, "Completed": False, "AreaId": ObjectId(areaId)} ) )

        for mower in area_mowers: # add fields, Addresses and Name to display on main page
            mower["Addresses"] = []
            mower["Name"] = products.find_one({"_id": mower["ProductId"]})["name"]


            for areaId in mower["AreaIds"]:
                #print(areaId["AreaId"], file=sys.stderr)
                mower["Addresses"].append(areas.find_one({"_id": areaId["AreaId"]})["Address"])

        for mower in available_mowers: # repeat for other mowers
            mower["Addresses"] = []
            mower["Name"] = products.find_one({"_id": mower["ProductId"]})["name"]


            for areaId in mower["AreaIds"]:
                #print(areaId["AreaId"], file=sys.stderr)
                mower["Addresses"].append(areas.find_one( {"_id": ObjectId(areaId["AreaId"])} )["Address"])

        # Get current time
        current_time = datetime.now()

        for ticket in area_tickets:
            diff = (ticket['DueDate'] - current_time).days
            #print(diff)
            if diff < 2:
                ticket["colour"] = 'red'
            elif diff < 8:
                ticket["colour"] = 'orange'
            else:
                ticket["colour"] = 'yellow'

        return render_template("SePrArea.html", title = "Service Provider Area", area=curr_area, area_mowers=area_mowers, available_mowers=available_mowers, area_tickets = area_tickets)
    else:
        return redirect(url_for("serviceprovider.serviceprovider"))


@serviceprovider_bp.route("/area/enter_mower", methods = ["GET", "POST"])
def enterMower():
    print(request.form, file=sys.stderr)
    if ("areaId" in request.form):

        areaId = request.form["areaId"]
        mowerId = request.form["mowerId"]

        #print(area, file=sys.stderr)

        session["area_id"] = areaId
        session["mower_id"] = mowerId

        return redirect(url_for("serviceprovider.mower"))
    else:   # if the request contains wrong info, send the user back to serviceproviders main-page
        return redirect(url_for("serviceprovider.serviceprovider"))


@serviceprovider_bp.route("/area/mower", methods = ["GET", "POST"])
def mower():
    # verifies that logged in user is a serviceprovider
    role = session["role"]
    if role != "serviceprovider":
        return redirect("/logout")

    #print(request.form, file=sys.stderr)
    if "area_id" in session and "mower_id" in session:
        areaId = session["area_id"]
        area = areas.find({"_id": ObjectId(areaId)})     # find area where id is the same as area clicked
        #print(area, file=sys.stderr)

        mowerId = session["mower_id"]
        lawnmower = mowers.find({"_id": ObjectId(mowerId)})
        print(lawnmower, file=sys.stderr)

        return render_template("SePrMower.html", area=area, lawnmower=lawnmower, title = "Service Provider Mower")
    else:
        return redirect(url_for("serviceprovider.area"))


@serviceprovider_bp.route("/area/add_mower", methods=["POST"])
def requestMower():
    #print(request.form, file=sys.stderr)
    if request.method == "POST":
        print(request.form, file=sys.stderr)
        print("here", file=sys.stderr)
        productId = ObjectId(request.form["productId"])

        # find the active provider
        userId = session["user_id"]
        current_user = accounts.find_one({'_id': ObjectId(userId)})
        providerId = current_user["ProviderId"]

        # make request to Husqvarna
        req_providerId = providerId
        type = "newMower"
        content = "Service Provider has requested a new lawnmower!"
        dateCreated = datetime.now()

        # adding the request
        requests.insert_one({"Completed": False, "DateCreated": dateCreated, "Content": content, "Type": type, "ProviderId": req_providerId, "ProductId": productId})

        return redirect(url_for("serviceprovider.serviceprovider"))
    return redirect(url_for("serviceprovider.serviceprovider")) 


@serviceprovider_bp.route("/area/revMow", methods = ["GET", "POST"])
def removeMower():
    mowerId =ObjectId(request.form["mowerId"])
    areaId = ObjectId(session["area_id"])
    lawnmower = mowers.find_one({"_id": mowerId})
    #print(lawnmower, file=sys.stderr)
    for area in lawnmower["AreaIds"]:
        if area["AreaId"]==areaId:
            lawnmower["AreaIds"].remove(area)
    mowers.find_one_and_update({"_id": mowerId}, {'$set': {"AreaIds": lawnmower["AreaIds"]}})
    return redirect(url_for("serviceprovider.area"))


@serviceprovider_bp.route("/area/addMow", methods= ["GET", "POST"])
def addMower():
    mowerId = ObjectId(request.form["mowerId"])
    areaId = ObjectId(session["area_id"])
    lawnmower = mowers.find_one({"_id": mowerId})
    lawnmower["AreaIds"].append({"AreaId": areaId})
    mowers.find_one_and_update({"_id": mowerId}, {'$set': {"AreaIds": lawnmower["AreaIds"]}})
    return redirect(url_for("serviceprovider.area"))


@serviceprovider_bp.route("/area/nav", methods = ["GET", "POST"])  # Depending on which button was clicked from navigation form, navigate
def areaNav():
    print(request.form, file=sys.stderr)
    page = request.form["navBar"]
    if page == "map":
        return redirect(url_for("serviceprovider.map"))
    elif page == "schedule":
        return redirect(url_for("serviceprovider.schedule"))
    elif page == "configuration":
        return redirect(url_for("serviceprovider.configuration"))
    elif page == "home":
        return redirect(url_for("serviceprovider.area"))
    else:
        return redirect(url_for("serviceprovider.serviceprovider"))


@serviceprovider_bp.route("/area/map", methods = ["GET", "POST"])
def map():
    #verifies that logged in user is a serviceprovider
    role = session["role"]
    if role != "serviceprovider":
        return redirect("/logout")

    print(request.form, file=sys.stderr)
    if "area_id" in session:
        areaId = session["area_id"]
        area = areas.find_one({"_id": ObjectId(areaId)})    # find area where id is the same as area clicked
        #print(area, file=sys.stderr)

        lawnmower = mowers.find()

        return render_template("SePrMap.html", area=area, lawnmower=lawnmower, title = "Service Provider Map")
    else:
        return redirect(url_for("serviceprovider.serviceprovider"))


@serviceprovider_bp.route("/area/schedule", methods = ["GET", "POST"])
def schedule():
    #verifies that logged in user is a serviceprovider
    role = session["role"]
    if role != "serviceprovider":
        return redirect("/logout")

    print(request.form, file=sys.stderr)
    if "area_id" in session:
        areaId = session["area_id"]
        area = areas.find_one({"_id": ObjectId(areaId)})    # find area where id is the same as area clicked
        #print(area, file=sys.stderr)

        lawnmower = mowers.find()

        return render_template("SePrSchedule.html", area=area, lawnmower=lawnmower, title = "Service Provider Schedule")
    else:
        return redirect(url_for("serviceprovider.serviceprovider"))


@serviceprovider_bp.route("/area/configuration", methods = ["GET", "POST"])
def configuration():
    #verifies that logged in user is a serviceprovider
    role = session["role"]
    if role != "serviceprovider":
        return redirect("/logout")

    print(request.form, file=sys.stderr)
    if "area_id" in session:
        areaId = session["area_id"]
        area = areas.find_one({"_id": ObjectId(areaId)})    # find area where id is the same as area clicked
        #print(area, file=sys.stderr)
        serviceId = area["ServiceId"]

        service = services.find_one({"_id": serviceId})
        print(service, file=sys.stderr)

        return render_template("SePrConf.html", area=area, service=service, title = "Customer Configurations")
    else:
        return redirect(url_for("serviceprovider.serviceprovider"))
