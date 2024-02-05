from flask import Flask, render_template, request, redirect, url_for, session, Blueprint
serviceprovider_bp = Blueprint('serviceprovider', __name__ , template_folder='templates', static_folder='static')

from pymongo import MongoClient
from bson.objectid import ObjectId
import sys

# Setting up/connecting to database
client = MongoClient('localhost', 27017)
db = client.MowerDB

# Single definition for table, change later
areas = db.Areas    # SePrAreas
mowers = db.Mowers  # SePrMowers
# SePrAreas & SePrMowers are old collections. Delete if you still have it!


@serviceprovider_bp.route("/", methods=["GET", "POST"])
def serviceprovider():
    #verifies that logged in user is a serviceprovider
    role = session["role"]
    if role != "serviceprovider":
        return redirect("/logout")
    
    all_areas = areas.find()   # get entire collection
    all_mowers = mowers.find()   # get entire collection
    return render_template("SePrMain.html", areas = all_areas, mowers = all_mowers)


@serviceprovider_bp.route("/add_area", methods=["POST"])
def addArea():
    #verifies that logged in user is a serviceprovider
    role = session["role"]
    if role != "serviceprovider":
        return redirect("/logout")
    
    #print(request.form, file=sys.stderr)
    if request.method == "POST":
        if ("address" in request.form): # if all needed keys are present
            print(request.form, file=sys.stderr)
            serviceId = None
            grassLength = None
            address = request.form["address"]
            homeX = None
            homeY = None
            customerId = 0 # placeholder for session
            status = "Unconfirmed"
            objId = ObjectId()
            areas.insert_one({"ServiceId": serviceId, "GrassLength": grassLength, "CustomerId": customerId, "HomeX": homeX, "HomeY": homeY, "Address": address, "Status": status, "_id": objId}) 
            session["area_id"] = str(objId)  
            return redirect(url_for("serviceprovider.settings"))
    return redirect(url_for("serviceprovider.serviceprovider"))   


@serviceprovider_bp.route("/enter", methods = ["GET", "POST"])
def enterArea():
    print(request.form, file=sys.stderr)
    if "areaId" in request.form:
        areaId = request.form["areaId"]
        # find area where id is the same as area clicked
        #print(area, file=sys.stderr)
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
        area = areas.find({"_id": ObjectId(areaId)})[0]    # find area where id is the same as area clicked

        lawnmower = mowers.find()

        return render_template("SePrArea.html", area=area, lawnmower=lawnmower)
    else:
        return redirect(url_for("serviceprovider.serviceprovider"))


@serviceprovider_bp.route("/area/mower", methods = ["GET", "POST"])
def mower():
    #verifies that logged in user is a serviceprovider
    role = session["role"]
    if role != "serviceprovider":
        return redirect("/logout")
    
    #print(request.form, file=sys.stderr)
    if "area_id" in session:
        areaId = session["area_id"]
        area = areas.find({"_id": ObjectId(areaId)})[0]    # find area where id is the same as area clicked
        #print(area, file=sys.stderr)

        lawnmower = mowers.find()

        return render_template("SePrMower.html", area=area, lawnmower=lawnmower)
    else:
        return redirect(url_for("serviceprovider.area"))


@serviceprovider_bp.route("/area/add_mower", methods=["POST"])
def addMower():
    #print(request.form, file=sys.stderr)
    if request.method == "POST":
        if ("Xpos" in request.form and "Ypos" in request.form): # if all needed keys are present
            print(request.form, file=sys.stderr)


            area_id = session["area_id"]
            area = areas.find({"_id": ObjectId(area_id)})[0]
            print("AREA: ", area)

            providerId = 0
            areaId = area['CustomerId']
            productId = 0
            Xpos = request.form["Xpos"]
            Ypos = request.form["Ypos"]
            objId = ObjectId()

            mowers.insert_one({"ProviderId": providerId, "AreaId": areaId, "ProductId": productId, "Xpos": Xpos, "Ypos": Ypos, "_id": objId})
            #session["area_id"] = 

            return redirect(url_for("serviceprovider.mower"))
    return redirect(url_for("serviceprovider.area")) 


@serviceprovider_bp.route("/area/enter_mower", methods = ["GET", "POST"])
def enterMower():
    print(request.form, file=sys.stderr)
    if ("areaId" in request.form and "mowerId" in request.form):

        areaId = request.form["areaId"]
        mowerId = request.form["mowerId"]

        # find area where id is the same as area clicked

        #print(area, file=sys.stderr)

        session["area_id"] = areaId

        return redirect(url_for("serviceprovider.mower"))
    else:
        return redirect(url_for("serviceprovider.area"))


@serviceprovider_bp.route("/area/nav", methods = ["GET", "POST"])  # Depending on which button was clicked from navigation form, navigate
def areaNav():
    print(request.form, file=sys.stderr)
    page = request.form["navBar"]
    if page == "map":
        return redirect(url_for("serviceprovider.map"))
    elif page == "schedule":
        return redirect(url_for("serviceprovider.schedule"))
    elif page == "settings":
        return redirect(url_for("serviceprovider.settings"))
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
        area = areas.find({"_id": ObjectId(areaId)})[0]    # find area where id is the same as area clicked
        #print(area, file=sys.stderr)

        lawnmower = mowers.find()

        return render_template("SePrMap.html", area=area, lawnmower=lawnmower)
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
        area = areas.find({"_id": ObjectId(areaId)})[0]    # find area where id is the same as area clicked
        #print(area, file=sys.stderr)

        lawnmower = mowers.find()

        return render_template("SePrSchedule.html", area=area, lawnmower=lawnmower)
    else:
        return redirect(url_for("serviceprovider.serviceprovider"))


@serviceprovider_bp.route("/area/settings", methods = ["GET", "POST"])
def settings():
    #verifies that logged in user is a serviceprovider
    role = session["role"]
    if role != "serviceprovider":
        return redirect("/logout")
    
    print(request.form, file=sys.stderr)
    if "area_id" in session:
        areaId = session["area_id"]
        area = areas.find({"_id": ObjectId(areaId)})[0]    # find area where id is the same as area clicked
        #print(area, file=sys.stderr)

        lawnmower = mowers.find()

        return render_template("SePrSett.html", area=area, lawnmower=lawnmower)
    else:
        return redirect(url_for("serviceprovider.serviceprovider"))
