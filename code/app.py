from flask import Flask, render_template, request, redirect, url_for, session, Blueprint
from customer.customer import customer_bp
from serviceprovider.serviceprovider import serviceprovider_bp
from manufacturer.manufacturer import manufacturer_bp

from itertools import count

from pymongo import MongoClient
from bson.objectid import ObjectId
import sys

# Setting up/connecting to database
client = MongoClient('localhost', 27017)
db = client.MowerDB
accounts = db.Accounts


app = Flask(__name__)
app.secret_key = "secret"  # Change this to a secret key for secure session management

app.register_blueprint(customer_bp, url_prefix='/customer')
app.register_blueprint(serviceprovider_bp, url_prefix='/serviceprovider')
app.register_blueprint(manufacturer_bp, url_prefix='/manufacturer')


@app.route('/')
def index():
    return render_template('login.html')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        #identifies if tuple of username and password exists in database
        
        #debugging -->
        cursor = accounts.find()
        for occ in cursor:
            print("occurences: ")
            print(occ)

        #<--

        user_tuple = accounts.find_one({"Username": username, "Password":password})
        if not user_tuple:
            return render_template("login.html", error="Invalid username or password")

        #sets session data for data regarding that user, before sending onwards
        #print("tuple: ", user_tuple)
        session['user_id'] = user_tuple["ACCId"]       
        session["username"] = user_tuple["Username"]
        session["role"] = user_tuple["Role"]
        return redirect(url_for("role_redirect"))

        
    
    # If it's a GET request, render the login form
    return render_template('login.html', error=None)

#redirects depending on the role of user
@app.route("/role_redirect")
def role_redirect():
    if "username" in session:
        role = session["role"]
        if role == "customer":
            return redirect(url_for("customer.customer"))
        if role == "serviceprovider":
            return redirect(url_for("serviceprovider.serviceprovider"))
        if role == "manufacturer":
            return redirect(url_for("manufacturer.manufacturer"))
    return redirect(url_for("login"))

@app.route("/logout", methods=["GET"])
def logout():
    session.clear()                     # clears everything from session
    return redirect(url_for("login"))

if __name__ == '__main__':
    app.run(debug=True)

