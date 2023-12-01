from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = "secret"  # Change this to a secret key for secure session management

class User:
    def __init__(self, username, password, role):
        self.username = username
        self.password = password
        self.role = role

# Dummy users for demonstration purposes
users = [
    User(username="manufacturer", password="m1", role="manufacturer"),
    User(username="serviceprovider", password="s1", role="serviceprovider"),
    User(username="customer", password="c1", role="customer"),
]

manufacturers = {
    'husqvarna1': 'h1',
    'husqvarna2': 'h2'
}





@app.route('/')
def index():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
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
            session["username"] = user.username
            session["role"] = user.role
            return redirect(url_for("role_redirect"))

        error = "Invalid username or password"
    return render_template("login.html", error=error if "error" in locals() else None)

#redirects depending on the role of user
@app.route("/role_redirect")
def role_redirect():
    if "username" in session:
        role = session["role"]
        if role == "customer":
            return render_template("CusMain.html")
        if role == "serviceprovider":
            return render_template("SePrMain.html")
        if role == "manufacturer":
            return render_template("ManMain.html")
    return redirect(url_for("login"))
    
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/customer")
def customer():

    return render_template("CusMain.html")

@app.route("/serviceprovider")
def serviceprovider():
    return render_template("SePrMain.html")
    

@app.route("/manufacturer")
def manufacturer():
    return render_template("ManMain.html")


if __name__ == '__main__':
    app.run(debug=True)
