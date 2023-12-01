from flask import Flask, render_template, request, redirect, url_for	# Import the Flask class. An instance of this class will be our WSGI application.
from pymongo import MongoClient

app = Flask(__name__)		# Create an instance of this class
# The first argument is the name of the application’s module or package. __name__ is a convenient shortcut for this that is appropriate for most cases. This is needed so that Flask knows where to look for resources such as templates and static files.

client = MongoClient('localhost', 27017)

db = client.NewCluster

guides = db.sample_guides

@app.route("/", methods=('GET', 'POST'))		# We then use the route() decorator to tell Flask what URL should trigger our function.
def hello_world():
	if request.method=='POST':
		content = request.form['content']
		guides.insert_one({'content': content})
		return redirect(url_for('hello_world'))

	all_guides = guides.find()

	return render_template("input.html", guides = all_guides)

# The default content type is HTML, so HTML in the string will be rendered by the browser.


