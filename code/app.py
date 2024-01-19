from flask import Flask, render_template, request, redirect, url_for, session, Blueprint
from customer.customer import customer_bp
from serviceprovider.serviceprovider import serviceprovider_bp
from manufacturer.manufacturer import manufacturer_bp

from itertools import count


app = Flask(__name__)
app.secret_key = "secret"  # Change this to a secret key for secure session management

app.register_blueprint(customer_bp, url_prefix='/customer')
app.register_blueprint(serviceprovider_bp, url_prefix='/serviceprovider')
app.register_blueprint(manufacturer_bp, url_prefix='/manufacturer')

class User:
    def __init__(self, username, password, role, user_id):
        self.username = username
        self.password = password
        self.role = role
        self.user_id = user_id


# Dummy users for demonstration purposes
user_id_counter = count(start=1)
users = [
    User(username="manufacturer", password="m1", role="manufacturer", user_id=next(user_id_counter)),
    User(username="serviceprovider", password="s1", role="serviceprovider", user_id=next(user_id_counter)),
    User(username="customer", password="c1", role="customer", user_id=next(user_id_counter)),
]

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        #identifies which user credentials was presented
        user = None
        for u in users:
            if u.username == username and u.password == password:
                user = u
                break

        #sets session data for data regarding that user, before sending onwards
        if user:
            session['user_id'] = user.user_id
            session["username"] = user.username
            session["role"] = user.role
            return redirect(url_for("role_redirect"))

        error = "Invalid username or password"
        return render_template("login.html", error=error)
    
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

