from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# Dummy user data (replace this with a database in a real application)
customers = {
    'user1': 'u1',
    'user2': 'u2'
}

serviceproviders = {
    "samhall1": "s1",
    "samhall2": "s2"
}

manufacturers = {
    'husqvarna1': 'h1',
    'husqvarna2': 'h2'
}





@app.route('/')
def index():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    # Successful login, redirect to a different page
    if username in customers and customers[username] == password:
        return redirect(url_for("customer"))
    elif username in serviceproviders and serviceproviders[username] == password:
        return redirect(url_for("serviceprovider"))
    elif username in manufacturers and manufacturers[username] == password:
        return redirect(url_for("manufacturer"))
    
    # Failed login, redirect back to the login page with an error message
    else:
        return render_template('login.html', error='Invalid username or password')

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