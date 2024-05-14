import os
from flask import Flask, render_template, request, redirect, url_for, session, Blueprint
customer_bp = Blueprint('customer', __name__, 
                        template_folder='templates',
                        static_folder='static')

from pymongo import MongoClient
from bson.objectid import ObjectId
import sys
from datetime import datetime, timedelta
import requests as rqs

# Setting up/connecting to database
database_address = os.environ.get("DATABASE_ADDRESS", "localhost")
database_port = os.environ.get("DATABASE_PORT", "27017")

client = MongoClient(database_address, int(database_port))
db = client.MowerDB

# Variables for connecting to Fabric API
eval_url = os.environ.get("EVALUATE_URL", "localhost:5001/sla/evaluate")
contractAPI_address = os.environ.get("CONTRACTAPI_ADDRESS", "localhost")
contractAPI_port = os.environ.get("CONTRACTAPI_PORT", "5001")


# Single definition for table, change later
areas = db.Areas
notifs = db.Notifications
mowers = db.Mower
services = db.Services
tickets = db.Service_Tickets
requests = db.Requests
accounts = db.Accounts

notifContent = {
    "service": "Your machine needs knife replacement, your service provider has been notified, no action required from you.",
    "replace-battery": "Your machine needs battery replacement, your service provider has been notified, no action required from you."
}





# @customer_bp.route("/", methods=["GET", "POST"])
# def customer():
#     cusAreas = areas.find() # {"CustomerId": 0}  # get areas belonging to user in session, placeholder for user in session
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
    
    notifStrings = {}
    customerId = accounts.find_one({"_id": ObjectId(session["user_id"])})["CustomerId"]
    cusAreas = areas.find({"CustomerId": customerId})   # get entire collection


    ### Check for notifications on all mowers in all areas

    cusAreasArr = list(cusAreas) # aparently needs to be list if you want a for loop in backend
    for area in cusAreasArr:     # make a list of all mowers on customers areas
        areaNotifs = []
        tempMowers = list(mowers.find({"AreaIds.AreaId": area["_id"]}))
        for mower in tempMowers:
            tempNotifs = notifs.find({"MowerId": mower["_id"]})
            for notif in tempNotifs:
                mess = notif["Content"]
                if mess == "stuck":
                    stuckTime = notif["Date"]
                    #print(area, file=sys.stderr)

                    ### Generate time left until service

                    timeDiff = datetime.now() - stuckTime 
                    timeDiff = timeDiff.days * 24 + timeDiff.seconds//3600
                    timeLeft = area["NotifTime"] - timeDiff


                    if timeLeft > 0:
                        content = {"text": "Your mower is stuck at " + str(mower["Xpos"]) + ", " + str(mower["Ypos"]) + "! View the map to see where. You may solve it yourself or a service provider will be called in " + str(timeLeft) + " hours.", "type": notif["Type"]}
                    else:
                        content = {"text": "Your mower is stuck at " + str(mower["Xpos"]) + ", " + str(mower["Ypos"]) + "! View the map to see where. Your service provider has been notified, no action required from you.", "type": "warning"}
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
        print(request.form, file=sys.stderr)
        if ("address" in request.form): # if all needed keys are present

            ### Generate values for insert

            print(request.form, file=sys.stderr)
            serviceId = None
            grassLength = None
            maxGrassLength = None
            minGrassLength = None
            address = request.form["address"]
            homeX = None
            homeY = None
            customerId = accounts.find_one({"_id": ObjectId(session["user_id"])})["CustomerId"]
            status = "Unconfirmed"
            objId = ObjectId()
            areas.insert_one({"ServiceId": serviceId, "GrassLength": grassLength, "GrassMaxLength": maxGrassLength, "GrassMinLength": minGrassLength, "CustomerId": customerId, "HomeX": homeX, "HomeY": homeY, "Address": address, "Status": status, "_id": objId}) 
            session["area_id"] = str(objId)  
            return redirect(url_for("customer.configure"))
    return redirect(url_for("customer.customer"))


@customer_bp.route("/edit_area", methods=["POST"])
def editArea():
    #print(request.form, file=sys.stderr)
    if request.method == "POST":
        if all(k in request.form for k in ("sub", "grassLength", "notifTime")): # if all needed keys are present


            ### Generate values for insert

            print(request.form, file=sys.stderr)
            areaId = ObjectId(session["area_id"])
            currArea = areas.find_one({"_id": areaId})
            sub = request.form["sub"]
            subId = services.find_one({"ServiceName": sub})['_id']
            grassLength = request.form["grassLength"]
            maxGrassLength = request.form["grassMax"]
            minGrassLength = request.form["grassMin"]
            notifTime = request.form["notifTime"]

            if (grassLength > maxGrassLength or grassLength < minGrassLength or maxGrassLength < minGrassLength):
                sub = services.find_one({"_id": currArea["ServiceId"]}) #get name of service level for current area
                #print(area, file=sys.stderr)
                if sub != None:
                    sub = sub["ServiceName"] 
                return render_template("CusConf.html", area=currArea, sub=sub, title="Customer Configure", grassLengthError = True)

            ### Update area, if it has not been confirmed by customer before, send off request to manufacturer

            if request.form["action"] == "submit":

                if currArea["Status"] == "Unconfirmed":
                    print("Unconfirmed")
                    cusId = accounts.find_one({"_id": ObjectId(session["user_id"])})["CustomerId"] 
                    data = {
                        'ServiceLevel': sub,
                        'TargetGrassLength': int(grassLength),
                        'MaxGrassLength': int(maxGrassLength),
                        'MinGrassLength': int(minGrassLength),
                    }
                    r = rqs.post(url=contractAPI_address + ":" + contractAPI_port + "/" + str(cusId) + "/sla", json=data)
                    if r.ok == False: 
                        print("EOF Error")
                        raise EOFError
                    slaID = r.content.decode()
                    newSlaID = slaID.replace('"', '')
                   
                    
                    areas.find_one_and_update({"_id": areaId}, {'$set': {"slaId": newSlaID, "GrassLength": int(grassLength), "GrassMaxLength": int(maxGrassLength), "GrassMinLength": int(minGrassLength), "ServiceId": subId, "NotifTime": int(notifTime), "Status": "Pending"}})
                    
                    ### Send request to manufacturer about new area needing assigned service provider
                    
                    address = areas.find_one({"_id": ObjectId(session["area_id"])})["Address"]
                    content = "Customer has requested mowing for area at address " + address + ". Please select service provider for this task."
                    requests.insert_one({"CustomerId": cusId, "Type": "newArea", "Content": content, "DateCreated": datetime.now(), "Completed": False, "AreaId": ObjectId(session["area_id"]) })
                else: 
                    print("Confirmed")
                    cusId = accounts.find_one({"_id": ObjectId(session["user_id"])})["CustomerId"]
                    data = {
                        'ServiceLevel': sub,
                        'TargetGrassLength': int(grassLength),
                        'MaxGrassLength': int(maxGrassLength),
                        'MinGrassLength': int(minGrassLength),
                    }
                    print("slaId:"+currArea["slaId"])
                    r = rqs.put(url=contractAPI_address + ":" + contractAPI_port + "/" + str(cusId)+ "/sla/" + currArea["slaId"], json=data)
                    if r.ok == False: 
                        print("EOF Error")
                        raise EOFError
                    areas.find_one_and_update({"_id": areaId}, {'$set': {"GrassLength": int(grassLength), "GrassMaxLength": int(maxGrassLength), "GrassMinLength": int(minGrassLength), "ServiceId": subId, "NotifTime": int(notifTime)}})
            
            elif request.form["action"] == "evaluate":
                data = {
                    'ServiceLevel': sub,
                    'TargetGrassLength': int(grassLength),
                    'MaxGrassLength': int(maxGrassLength),
                    'MinGrassLength': int(minGrassLength),
                }
                r = rqs.post(url=eval_url, json=data)
                if r.ok == False: 
                    raise EOFError
                
                if currArea == None:
                    currArea = {}
                currArea["GrassLength"] = grassLength
                currArea["GrassMaxLength"] = maxGrassLength
                currArea["GrassMinLength"] = minGrassLength
                currArea["NotifTime"] = notifTime
                return render_template("CusConf.html", area=currArea, sub=sub, title="Customer Configure", evaluatedCost=r.content.decode("utf-8"))

    return redirect(url_for("customer.customer"))
    

    
@customer_bp.route("/enter", methods = ["GET", "POST"])
def enterArea():
    print(request.form, file=sys.stderr)
    if "areaId" in request.form:
        areaId = request.form["areaId"]

        ### Find area where id is the same as area clicked
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

        ### Check for notifications on all mowers in this area

        for mower in tempMowers:
            tempNotifs = notifs.find({"MowerId": mower["_id"]})
            for notif in tempNotifs:
                mess = notif["Content"]
                if mess == "stuck":
                    stuckTime = notif["Date"]
                    #print(area, file=sys.stderr)

                    ### Generate time left until service
                    
                    timeDiff = datetime.now() - stuckTime 
                    timeDiff = timeDiff.days * 24 + timeDiff.seconds//3600
                    timeLeft = area["NotifTime"] - timeDiff

                    if timeLeft > 0:
                        content = {"text": "Your mower is stuck at " + str(mower["Xpos"]) + ", " + str(mower["Ypos"]) + "! View the map to see where. You may solve it yourself or a service provider will be called in " + str(timeLeft) + " hours.", "type": notif["Type"]}
                    else:
                        content = {"text": "Your mower is stuck at " + str(mower["Xpos"]) + ", " + str(mower["Ypos"]) + "! View the map to see where. Your service provider has been notified, no action required from you.", "type": "warning"}
                    
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
    

### Extenal API from simulated "mower"
#   Example JSON format
#   Mower is stuck:
#    {
#       "externalSystemSlug": "65eb20ea27fbfb29b54e6e5b",
#       "type": "stuck",
#    }
#    
#   Mower is no longer stuck:
#    {
#       "externalSystemSlug": "65eb20ea27fbfb29b54e6e5b",
#       "type": "unstuck",
#    }
#        
#    Mower needs knife replacement:
#    {
#       "externalSystemSlug": "65eb20ea27fbfb29b54e6e5b",
#       "type": "service",
#    }
#    

@customer_bp.route("/recData", methods=["GET", "POST"])
def recieveData():
    data = request.json
    print(request.json, file=sys.stderr)
    match data["type"]:
        case "stuck":
            externalSystemSlug = data["externalSystemSlug"]

            mower = mowers.find_one({"ExternalSystemSlug": externalSystemSlug})

            notifs.update_one({"MowerId": mower["_id"], "Content": "stuck",}, {'$setOnInsert': {"Type": "alert", "Seen": False, "Date": datetime.now()}}, upsert = True)
        
        case "trapped":
            externalSystemSlug = data["externalSystemSlug"]

            mower = mowers.find_one({"ExternalSystemSlug": externalSystemSlug})

            notifs.update_one({"MowerId": mower["_id"], "Content": "stuck",}, {'$setOnInsert': {"Type": "alert", "Seen": False, "Date": datetime.now()}}, upsert = True)
        case "unstuck":
            #Delete notification, update position

            externalSystemSlug = data["externalSystemSlug"]

            mower = mowers.find_one({"ExternalSystemSlug": externalSystemSlug})

            # mower = mowers.find_one_and_update({"_id": externalSystemSlug}, {'$set': {"Xpos": data["Xpos"], "Ypos": data["Ypos"]}})
            notifId = notifs.find_one({"MowerId": mower["_id"], "Content": "stuck"})["_id"]
            notifs.delete_one({"_id": notifId})

            #Set service ticket status to complete

            # tickets.find_one_and_update({"NotifId": notifId}, {"$set": {"Completed": True, "NotifId": None}})

        case "service":
            externalSystemSlug = data["externalSystemSlug"]
            mower = mowers.find_one({"ExternalSystemSlug": externalSystemSlug})

            notifs.update_one({"MowerId": mower["_id"], "Content": "service",}, {'$setOnInsert': {"Type": "warning", "Seen": False, "Date": datetime.now()}}, upsert = True)

        case "replace-battery":
            externalSystemSlug = data["externalSystemSlug"]
            mower = mowers.find_one({"ExternalSystemSlug": externalSystemSlug})

            notifs.update_one({"MowerId": mower["_id"], "Content": "replace-battery",}, {'$setOnInsert': {"Type": "warning", "Seen": False, "Date": datetime.now()}}, upsert = True)



    return "", 204
