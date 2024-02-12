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
notifs = db.Notifications
mowers = db.Mower
services = db.Services

notifContent = {"service": "Your machine needs knife replacement, your service provider has been notified, no action required from you."}





# @customer_bp.route("/", methods=["GET", "POST"])
# def customer():
#     cusAreas = areas.find() # {"CustomerId": 0}  # get areas belonging to user in session, placefolder for user in session
#     print(cusAreas, file=sys.stderr)
#     cusNotifs = []
#     for area in cusAreas:  #### PICK UP HERE
#         cusNotifs.append(notifs.find({"AreaId": area["_id"]})) # Find notifications where areaId is one of customers areas

#     return render_template("CusMain.html", areas = cusAreas, title = "Customer Mainpage")

@customer_bp.route("/", methods=["GET", "POST"])
def customer():
    #verifies that logged in user is a customer
    role = session["role"]
    if role != "customer":
        return redirect("/logout")
    
    notifContent = {"service": "Your machine needs knife replacement, your service provider has been notified, no action required from you."}
    notifStrings = {}
    cusAreas = areas.find({"CustomerId": 0})   # get entire collection

    cusAreasArr = list(cusAreas) # aparently needs to be list if you want a for loop in backend
    for area in cusAreasArr:     # make a list of all mowers on customers areas
        areaNotifs = []
        tempMowers = list(mowers.find({"AreaIds.AreaId": area["_id"]}))
        for mower in tempMowers:
            tempNotifs = notifs.find({"MowerId": mower["_id"]})
            for notif in tempNotifs:
                mess = notif["Content"]
                if mess == "stuck":
                    content = {"text": "Your mower is stuck at " + str(mower["Xpos"]) + ", " + str(mower["Ypos"]) + "! View the map to see where. You may solve it yourself or a service provider will be called in X hours.", "type": notif["Type"]}
                else:
                    content = {"text": notifContent[mess], "type": notif["Type"]}
                areaNotifs.append(content)
        notifStrings[str(area["_id"])] = {"content": areaNotifs}
    print(notifStrings, file=sys.stderr)
    return render_template("CusMain.html", areas = cusAreasArr, notifs = notifStrings, title = "Customer Mainpage")

@customer_bp.route("/add_area", methods=["POST"])
def addArea():
    #print(request.form, file=sys.stderr)
    if request.method == "POST":
        if ("address" and "addressNumber" in request.form): # if all needed keys are present
            print(request.form, file=sys.stderr)
            serviceId = None
            grassLength = None
            address = request.form["address"] + " " + request.form["addressNumber"]
            homeX = None
            homeY = None
            customerId = 0 #placeholder for session
            status = "Unconfirmed"
            objId = ObjectId()
            areas.insert_one({"ServiceId": serviceId, "GrassLength": grassLength, "CustomerId": customerId, "HomeX": homeX, "HomeY": homeY, "Address": address, "Status": status, "_id": objId}) 
            session["area_id"] = str(objId)  
            return redirect(url_for("customer.configure"))
    return redirect(url_for("customer.customer"))


@customer_bp.route("/edit_area", methods=["POST"])
def editArea():
    #print(request.form, file=sys.stderr)
    if request.method == "POST":
        if all(k in request.form for k in ("sub", "grassLength", "notifTime")): # if all needed keys are present
            print(request.form, file=sys.stderr)
            areaId = ObjectId(session["area_id"])
            currArea = areas.find_one({"_id": areaId})
            sub = request.form["sub"]
            subId = services.find_one({"ServiceName": sub})['_id']
            grassLength = request.form["grassLength"]
            notifTime = request.form["notifTime"]
            if currArea["Status"] == "Unconfirmed":
                areas.find_one_and_update({"_id": areaId}, {'$set': {"GrassLength": int(grassLength), "ServiceId": subId, "NotifTime": int(notifTime), "Status": "Pending"}})
            else: 
                areas.find_one_and_update({"_id": areaId}, {'$set': {"GrassLength": int(grassLength), "ServiceId": subId, "NotifTime": int(notifTime)}})
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
    #verifies that logged in user is a customer
    role = session["role"]
    if role != "customer":
        return redirect("/logout")
    
    if "area_id" in session:
        areaId = session["area_id"]
        area = areas.find({"_id": ObjectId(areaId)})[0]    # find area where id is the same as area clicked
        areaNotifs = []
        tempMowers = list(mowers.find({"AreaIds.AreaId": area["_id"]}))
        for mower in tempMowers:
            tempNotifs = notifs.find({"MowerId": mower["_id"]})
            for notif in tempNotifs:
                mess = notif["Content"]
                if mess == "stuck":
                    content = {"text": "Your mower is stuck at " + str(mower["Xpos"]) + ", " + str(mower["Ypos"]) + "! View the map to see where. You may solve it yourself or a service provider will be called in X hours.", "type": notif["Type"]}
                else:
                    content = {"text": notifContent[mess], "type": notif["Type"]}
                areaNotifs.append(content)
        return render_template("CusArea.html", area=area, title="Customer Area", notifs=areaNotifs)
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
    elif page == "configure":
        return redirect(url_for("customer.configure"))
    elif page == "home":
        return redirect(url_for("customer.area"))
    else:
        return redirect(url_for("customer.customer"))

@customer_bp.route("/area/map", methods = ["GET", "POST"])
def map():
    #verifies that logged in user is a customer
    role = session["role"]
    if role != "customer":
        return redirect("/logout")
    
    print(request.form, file=sys.stderr)
    if "area_id" in session:
        areaId = session["area_id"]
        area = areas.find({"_id": ObjectId(areaId)})[0]    # find area where id is the same as area clicked
        #print(area, file=sys.stderr)
        return render_template("CusMap.html", area=area, title="Customer Map")
    else:
        return redirect(url_for("customer.customer"))

@customer_bp.route("/area/schedule", methods = ["GET", "POST"])
def schedule():
    #verifies that logged in user is a customer
    role = session["role"]
    if role != "customer":
        return redirect("/logout")
    
    print(request.form, file=sys.stderr)
    if "area_id" in session:
        areaId = session["area_id"]
        area = areas.find({"_id": ObjectId(areaId)})[0]    # find area where id is the same as area clicked
        #print(area, file=sys.stderr)
        return render_template("CusSched.html", area=area, title="Customer Schedule")
    else:
        return redirect(url_for("customer.customer"))

@customer_bp.route("/area/configure", methods = ["GET", "POST"])
def configure():
    #verifies that logged in user is a customer
    role = session["role"]
    if role != "customer":
        return redirect("/logout")
    
    print(request.form, file=sys.stderr)
    if "area_id" in session:
        areaId = session["area_id"]
        area = areas.find({"_id": ObjectId(areaId)})[0]    # find area where id is the same as area clicked
        sub = services.find_one({"_id": area["ServiceId"]}) #get name of service level for current area
        #print(area, file=sys.stderr)
        if sub != None:
            sub = sub["ServiceName"] 
        return render_template("CusConf.html", area=area, sub=sub, title="Customer Configure")
    else:
        return redirect(url_for("customer.customer"))
    

