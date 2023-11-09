from flask import Flask	# Import the Flask class. An instance of this class will be our WSGI application.

app = Flask(__name__)		# Create an instance of this class
# The first argument is the name of the application’s module or package. __name__ is a convenient shortcut for this that is appropriate for most cases. This is needed so that Flask knows where to look for resources such as templates and static files.

@app.route("/")		# We then use the route() decorator to tell Flask what URL should trigger our function.
def hello_world():
	test1 = "<h1>Hello, World!</h1> <p>This is my first paragraf!!</p>"
	test2 = "<h2>More HEADINGS!!</h2>"
	return test1 + test2	# Return the message we want to display in the user's browser
# The default content type is HTML, so HTML in the string will be rendered by the browser.
