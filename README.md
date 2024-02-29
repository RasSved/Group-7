### Micro-services for lawn-mower zero/low administration service delivery
## About the project:

This projects is a prototype of a portal used for communication between customers, service providers and Husqvarna, the manufacturer of lawnmowers. The prototype is supposed to demonstrate a proof of concept for husqvarna and give ideas to potentially use in a fully developed system. It strives to reduce the amount of administration needed in the process by giving a framework for customers and service providers to send request to husqvarna that are to be handled by any method of the manufacturers choice. These are then either resolved by husqvarna or sent to a service provider as a service ticket to handle.

## Built with:

Python-flask

MongoDB

## Requirements:

To run the project, it is required that python is installed on the host machine. Specifically python 3.10 or a later version. Python can be installed from the following link https://www.python.org/downloads/.



## Installation:

To set up the project locally you first need to install a number of dependencies. One of the most important ones is the MongoDB. This can be installed locally by following the following guide https://www.mongodb.com/docs/manual/installation/. Alternatively, it can be run in the cloud using MongoDB atlas https://www.mongodb.com/atlas/database?tck=docs_mongos. This has however not been tested in this project and some information about the mongo client may need to be updated in the program.

Additionally, a few packages need to be installed to run the project correctly.
These are:

python-flask

pip install Flask

pymongo

pip install pymongo

werkzeug

pip install werkzeug

flask_wtf

pip install flask_wtf

To run the project, download the git repository and enter the following line into a command line open in the "code" directory

python3 -m flask --app app run

## Documentation:

Moqup: https://www.figma.com/file/kHqxsPFkOk561WTRrtqmez/Project-7?type=design&node-id=0-1&mode=design&t=vyM2DaXzGo8gs9QP-0 

State Chart: https://excalidraw.com/#json=HneRJxFdTy7hXLBE7d1bt,gerfiUZiEXEDCRee2FAZyA

Database Schema: https://dbdiagram.io/d/Data-Schema-65673b903be1495787f97f4d
