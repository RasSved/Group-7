import os
from flask import Flask, render_template, request, redirect, url_for, session, Blueprint
serviceprovider_bp = Blueprint('serviceprovider', __name__ , template_folder='templates', static_folder='static')

from pymongo import MongoClient
from bson.objectid import ObjectId
import sys
import serviceprovider.task_assignments as task_assignments
import serviceprovider.dtos as dtos
import serviceprovider.work_tasks as work_tasks

from datetime import datetime, timedelta

# Setting up/connecting to database
database_address = os.environ.get("DATABASE_ADDRESS", "localhost")
database_port = os.environ.get("DATABASE_PORT", "27017")
client = MongoClient(database_address, int(database_port))
db = client.MowerDB

# Single definition for table, change later
accounts = db.Accounts
areas = db.Areas
mowers = db.Mower
notifs = db.Notifications
service_tickets = db.Service_Tickets
requests = db.Requests
products = db.Products
accounts = db.Accounts
services = db.Services
service_providers = db.Service_Provider

@serviceprovider_bp.route("/", methods=["GET", "POST"])
def serviceprovider():
    # Verifies that logged in user is a serviceprovider
    role = session["role"]
    if role != "serviceprovider":
        return redirect("/logout")

    providerId      = accounts.find_one( {"_id": ObjectId(session["user_id"])} )["ProviderId"]

    all_mowers      = list(mowers.find( {"ProviderId": providerId} ))  # Get all mowers of specific provider, update to contain object id
    all_products    = list(products.find())
    all_tickets     = list(service_tickets.find( {"ProviderId": providerId, "Completed": False} ))

    all_areas = list(areas.find({"ProviderId": providerId }))
    for ticket in all_tickets:
        ticket["AreaIds"] = []
        if 'MowerId' in ticket:
            print("bingus", file=sys.stderr)
            lawnmower = mowers.find_one( {'_id': ObjectId(ticket['MowerId'])} )
            for area_id in lawnmower['AreaIds']:
                ticket["AreaIds"].append(area_id["AreaId"])
                area = areas.find_one( {'_id': area_id["AreaId"]} )
                if area not in all_areas:
                    all_areas.append( area )
        else:
            ticket["AreaIds"] = [ticket["AreaId"]]
            area = areas.find_one( {'_id': ticket["AreaId"]} )
            if area not in all_areas:
                all_areas.append( area )
    #print(all_areas, file=sys.stderr)

    for mower in all_mowers:            # Add fields, addresses and name to display on main page
        #print(mower["AreaIds"], file=sys.stderr)
        mower["Addresses"] = []
        mower["Name"] = products.find_one({"_id": mower["ProductId"]})["Name"]
        for areaId in mower["AreaIds"]:
            #print(areaId, file=sys.stderr)
            mower["Addresses"].append(areas.find_one({"_id": ObjectId(areaId["AreaId"])})["Address"])

    current_time = datetime.now()   # Get current time

    for ticket in all_tickets:

        if ticket['Content'] == "newArea":
            ticket["desc"] = "A new area is needed to be setup!"
        elif ticket['Content'] == work_tasks.WorkTaskType.BLADE_CHANGE.value:
            ticket["desc"] = "You need to replace the knife on a mower!"
        elif ticket['Content'] == work_tasks.WorkTaskType.STUCK.value:
            ticket["desc"] = "A mower is stuck! Push it!"
        else:
            ticket["desc"] = "This is a placeholder for a description of the ticket!"

        diff = (ticket['DueDate'] - current_time).days
        #print(diff)
        if diff < 2:
            ticket["colour"] = 'red'
        elif diff < 8:
            ticket["colour"] = 'orange'
        else:
            ticket["colour"] = 'yellow'

    return render_template("SePrMain.html", title = "Service Provider Mainpage", areas = all_areas, mowers = all_mowers, products = all_products, tickets = all_tickets, providerId = providerId)


@serviceprovider_bp.route("/enter", methods = ["GET", "POST"])
def enterArea():
    #print(request.form, file=sys.stderr)
    if "areaId" in request.form:
        areaId = request.form["areaId"]
        #print(areaId, file=sys.stderr)
        session["area_id"] = str(areaId)
        return redirect(url_for("serviceprovider.area"))
    else:
        return redirect(url_for("serviceprovider.serviceprovider"))


@serviceprovider_bp.route("/area", methods = ["GET", "POST"])
def area():
    # Verifies that logged in user is a serviceprovider
    role = session["role"]
    if role != "serviceprovider":
        return redirect("/logout")

    if "area_id" in session:
        areaId = session["area_id"]
        curr_area = areas.find_one({"_id": ObjectId(areaId)})    # find area where id is the same as area clicked
        providerId = accounts.find_one({"_id": ObjectId(session["user_id"])})["ProviderId"]

        area_mowers = list(mowers.find({"AreaIds": {'$elemMatch': {"AreaId": ObjectId(session["area_id"])}}}))  # get all mowers of specific area, update to contain object 
        available_mowers = list(mowers.find({"ProviderId": providerId, "AreaIds": {'$not': {'$elemMatch': {"AreaId": ObjectId(session["area_id"])}}}})) # get all mowers that belong to provider but are not on current area

        tickets = list( service_tickets.find( {"ProviderId": providerId, "Completed": False} ) )
        # area_tickets = list( service_tickets.find( {"ProviderId": providerId, "Completed": False, "AreaId": ObjectId(areaId)} ) )

        for mower in area_mowers: # add fields, Addresses and Name to display on main page
            # for area in mower["AreaIds"]:

                #print(areaId, file=sys.stderr)
                
                # if str(area["AreaId"]) == str(areaId):
                #     print("AreaId", file=sys.stderr)
                #     mower_tickets = list(service_tickets.find({"MowerId": mower["_id"], "Completed": False}))
                #     for ticket in mower_tickets:
                #         if ticket not in area_tickets:
                #             area_tickets.append(ticket)

            mower["Addresses"] = []
            mower["Name"] = products.find_one({"_id": mower["ProductId"]})["Name"]

            for areaId in mower["AreaIds"]:
                #print(areaId["AreaId"], file=sys.stderr)
                mower["Addresses"].append(areas.find_one({"_id": areaId["AreaId"]})["Address"])

        for mower in available_mowers: # repeat for other mowers
            mower["Addresses"] = []
            mower["Name"] = products.find_one({"_id": mower["ProductId"]})["Name"]


            for areaId in mower["AreaIds"]:
                #print(areaId["AreaId"], file=sys.stderr)
                mower["Addresses"].append(areas.find_one( {"_id": ObjectId(areaId["AreaId"])} )["Address"])

        # Get current time
        current_time = datetime.now()

        for ticket in tickets:

            if ticket['Content'] == "newArea":
                ticket["desc"] = "A new area is needed to be setup!"
            elif ticket['Content'] == work_tasks.WorkTaskType.BLADE_CHANGE.value:
                ticket["desc"] = "You need to replace the knife on a mower!"
            elif ticket['Content'] == work_tasks.WorkTaskType.STUCK.value:
                ticket["desc"] = "A mower is stuck! Push it!"
            else:
                ticket["desc"] = "This is a placeholder for a description of the ticket!"

            diff = (ticket['DueDate'] - current_time).days
            #print(diff)
            if diff < 2:
                ticket["colour"] = 'red'
            elif diff < 8:
                ticket["colour"] = 'orange'
            else:
                ticket["colour"] = 'yellow'

            ticket["Assigned"] = task_assignments.assignment_to_task_exist(ticket['WorkTaskId'])

            ticket["AssignedToMe"] = task_assignments.is_provider_assigned(ticket['ProviderId'], ticket['WorkTaskId'])


        return render_template("SePrArea.html", title = "Service Provider Area", area=curr_area, area_mowers=area_mowers, available_mowers=available_mowers, area_tickets = tickets, providerId = providerId)
    else:
        return redirect(url_for("serviceprovider.serviceprovider"))


@serviceprovider_bp.route("/area/complete_ticket", methods = ["GET", "POST"])
def completeServiceTicket():
    print(request.form, file=sys.stderr)
    if ("ticket_id" in request.form):

        ticket_id = request.form["ticket_id"]
        ticket = service_tickets.find_one({'_id': ObjectId(ticket_id)})
        result = service_tickets.update_many({'WorkTaskId': ticket['WorkTaskId']}, {'$set': {'Completed': True}})

        completed = task_assignments.complete_task(ticket['ProviderId'], ticket['WorkTaskId'])
        print(completed)

        #print(result, file=sys.stderr)

        current_ticket = service_tickets.find_one({'_id': ObjectId(ticket_id)})

        if "NotifId" in current_ticket:
            notifId = current_ticket['NotifId']

            for ticket in list(service_tickets.find()):
                if "NotifId" in ticket:
                    if ticket['NotifId'] == notifId:
                        service_tickets.update_one({'_id': ObjectId(ticket['_id'])}, {'$set': {'NotifId': None}})

            notifs.delete_one( {'_id': ObjectId(notifId)} )

        if "newArea" in current_ticket['Content']:
            # change the status of the area to *something*
            areaId = current_ticket['AreaId']
            result_area = areas.update_one( {'_id': ObjectId(areaId)}, {'$set': {'Status': "Up & Running"}} )
            print(result, file=sys.stderr)

        return redirect(url_for("serviceprovider.area"))
    else:   # if the request contains wrong info, send the user back to serviceproviders main-page
        return redirect(url_for("serviceprovider.serviceprovider"))

@serviceprovider_bp.route("/area/take_ticket", methods = ["POST"])
def takeServiceTicket():
    print(request.form, file=sys.stderr)
    if ("ticket_id" in request.form):

        ticket_id = ObjectId(request.form["ticket_id"])
        service_ticket_object = service_tickets.find_one({'_id': ObjectId(ticket_id)})

        try:
            takeWorkUrl = service_ticket_object["TakeWorkUrl"]
        except:
            takeWorkUrl = None
        
        assignment = task_assignments.assign_task(providerId=service_ticket_object["ProviderId"], workTaskId=service_ticket_object["WorkTaskId"],  takeTaskUrl=takeWorkUrl)
        print(assignment)
        service_tickets.update_one({'_id': ObjectId(ticket_id)}, {'$set': {'Assignment': assignment["_id"]}})
        
        return redirect(url_for("serviceprovider.area"))
    else:   # if the request contains wrong info, send the user back to serviceproviders main-page
        return redirect(url_for("serviceprovider.serviceprovider"))


@serviceprovider_bp.route("/area/enter_mower", methods = ["GET", "POST"])
def enterMower():
    print(request.form, file=sys.stderr)
    if ("areaId" in request.form):

        areaId = request.form["areaId"]
        mowerId = request.form["mowerId"]

        session["area_id"] = areaId
        session["mower_id"] = mowerId

        return redirect(url_for("serviceprovider.mower"))
    else:   # if the request contains wrong info, send the user back to serviceproviders main-page
        return redirect(url_for("serviceprovider.serviceprovider"))


@serviceprovider_bp.route("/area/mower", methods = ["GET", "POST"])
def mower():
    # Verifies that logged in user is a serviceprovider
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
        #print(lawnmower, file=sys.stderr)

        return render_template("SePrMower.html", area=area, lawnmower=lawnmower, title = "Service Provider Mower")
    else:
        return redirect(url_for("serviceprovider.area"))


@serviceprovider_bp.route("/area/add_mower", methods=["POST"])
def requestMower():
    #print(request.form, file=sys.stderr)
    if request.method == "POST":
        print(request.form, file=sys.stderr)
        productId = ObjectId(request.form["productId"])

        # find the active provider
        userId = session["user_id"]
        current_user = accounts.find_one({'_id': ObjectId(userId)})
        providerId = current_user["ProviderId"]

        # make request to Husqvarna
        type = "mowerReq"
        content = "Service Provider request a new lawnmower!"
        dateCreated = datetime.now()

        # adding the request
        requests.insert_one({"Completed": False, "DateCreated": dateCreated, "Content": content, "Type": type, "ProviderId": providerId, "ProductId": productId})

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
    # Verifies that logged in user is a serviceprovider
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
    # Verifies that logged in user is a serviceprovider
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
    # Verifies that logged in user is a serviceprovider
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

@serviceprovider_bp.route("/work-task", methods=["POST"])
def new_work_task():
    raw_data = request.json
    try:
        new_work_task = dtos.NewWorkTask(
            workTask=work_tasks.WorkTaskType.from_str(raw_data['workTaskType']),
            tecnicianSystemSlug=raw_data['tecnicianSystemSlug'],
            mowerSystemSlug=raw_data['mowerSystemSlug'],
            workTaskId=raw_data['workTaskId'],
            takeWorkUrl=raw_data['takeWorkUrl'],
        )
    except(NotImplementedError):
        return f"the work task: {raw_data['workTaskType']}, has not been implemented", 500

    provider = service_providers.find_one({'ExternalSystemSlug': new_work_task.tecnicianSystemSlug})

    mower = mowers.find_one({'ExternalSystemSlug': new_work_task.mowerSystemSlug})

    if (provider == None or mower == None):
        return "", 500

    print(mower)
    dueDate = datetime.now() + timedelta(days=14)
    service_tickets.insert_one({"MowerId": mower['_id'], "Content": new_work_task.workTaskType.value, "ProviderId": provider['_id'], "DateCreated": datetime.now(), "Completed": False, "DueDate": dueDate, "WorkTaskId": new_work_task.workTaskId, "TakeWorkUrl": new_work_task.takeWorkUrl})

    return "", 201