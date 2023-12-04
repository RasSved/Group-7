from flask import Flask, render_template, request, redirect, url_for	# Import the Flask class. An instance of this class will be our WSGI application.

app = Flask(__name__)		# Create an instance of this class

@app.route("/serviceprovider")
def serviceprovider():
    return render_template("SePrMain.html")


# Markus safty place, all are welcome!