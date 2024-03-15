### Micro-services for lawn-mower zero/low administration service delivery
## About the project

This projects is a prototype of a portal used for communication between customers, service providers and Husqvarna, the manufacturer of lawnmowers. The prototype is supposed to demonstrate a proof of concept for husqvarna and give ideas to potentially use in a fully developed system. It strives to reduce the amount of administration needed in the process by giving a framework for customers and service providers to send request to husqvarna that are to be handled by any method of the manufacturers choice. These are then either resolved by husqvarna or sent to a service provider as a service ticket to handle.

The content of the project can be further improved in several ways. One is to complete project according to statechart and databaseschema 

## Built with

Python-flask

MongoDB

## Requirements

To run the project, it is required that python is installed on the host machine. Specifically python 3.10 or a later version. Python can be installed from the following link https://www.python.org/downloads/.



## Installation

To set up the project locally you first need to install a number of dependencies. One of the most important ones is the MongoDB. This can be installed locally by following the following guide https://www.mongodb.com/docs/manual/installation/. Alternatively, it can be run in the cloud using MongoDB atlas https://www.mongodb.com/atlas/database?tck=docs_mongos. This has however not been tested in this project and some information about the mongo client may need to be updated in the program.

Additionally, a few packages need to be installed to run the project correctly.
These are:

python-flask

```
pip install Flask
```
pymongo
```
pip install pymongo
```
werkzeug
```
pip install werkzeug
```
flask_wtf
```
pip install flask_wtf
```

Download the git repository.

## Example: Start server and create new area in customer-page

# Start database and setup database

Windows:
https://www.mongodb.com/docs/manual/installation/

Linux:
```
sudo mongod
```

Run provided db_setup.py to setup database with example data (change port at "client" declaration from "27017" if you want to use something else)

# Run project

Enter one of following lines into a command line that is in the "code" directory

Windows:
```
python3 -m flask --app app run
```

Linux:
```
python3 app.py
```

# Login and create area

An address should have appeared in command line in the form "http://127.0.0.1:5000", access it with webbrowser.

Login with a customer account (db_setup.py provides, among others, "customer1@customer.com" with password "customer1") 

Click on "+" symbol to add new area

Write in relevant address for area

Get redirected to area settings page and fill in information to finish customer setup of area. 

Success can be seen at area in Customer Mainpage when status for area is "Pending". One must now wait for manufacturer and serviceprovider to complete their parts. 

## Documentation
# Moqup
The moqup is an easly stage moqup that somewhat illustrates the look of the website. This has been changed a lot during development and does not represent the final result.
https://www.figma.com/file/kHqxsPFkOk561WTRrtqmez/Project-7?type=design&node-id=0-1&mode=design&t=vyM2DaXzGo8gs9QP-0 

# State chart
The state chart is a diagram that describes the different states that the portal can have depending on user input. These states represent windows and pages on the website and solely describe what the user will see when using the platform.
https://excalidraw.com/#json=HneRJxFdTy7hXLBE7d1bt,gerfiUZiEXEDCRee2FAZyA


# Database Schema
The database schema describes the schema used for MongoDB with the name of the table being the collection name and each entry in the table represents a key with the type of it's value. Since MongoDB is a document database, every document does not need to contain all the values and thus some documents are missing values shown in the schema. For more information about what requests, service-tickets and notifications contain what fields, see the documentation.
https://dbdiagram.io/d/Data-Schema-65673b903be1495787f97f4d
