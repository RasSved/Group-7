#run this to setup database with dummy data

from itertools import count
import os

from pymongo import MongoClient
from bson.objectid import ObjectId
import sys

# Setting up/connecting to database
database_address = os.environ.get("DATABASE_ADDRESS", "localhost")
database_port = os.environ.get("DATABASE_PORT", "27017")
client = MongoClient(database_address, int(database_port))
db = client.MowerDB

#creating "Service_Provider" table, accounts table and customer table
Service_Provider = db.Service_Provider
Accounts = db.Accounts
Customer = db.Customer
mowers = db.Mower

account = Accounts.find_one()

if account != None:
    print("database is already setup")
    exit(0)
print("seting up database")


mowers.create_index("ExternalSystemSlug", unique = True)


#putting serviceproviders into accounts -->
Service_Provider_dict = [
    {"Name":"Ulf Olovsson", "Email": "Ulol@serviceprovider.com", "Phone": "075 555 555", "ExternalSystemSlug": "technician-1"},
    {"Name":"Bingus Dingus", "Email": "BingDing@serviceprovider.com", "Phone": "075 555 515", "ExternalSystemSlug": "technician-2"},
]

Service_Provider.create_index("ExternalSystemSlug", unique = True)
for n in Service_Provider_dict:
    Service_Provider.insert_one(n)

    searchedForID = Service_Provider.find_one(n, {"_id": 1})

    #Password becomes string before @ in Email
    Accounts.insert_one({"CustomerId":None, "ProviderId":searchedForID["_id"], "Email":n["Email"], "Password":(n["Email"]).split('@')[0], "Role":"serviceprovider"})

#<--
    
#putting customers into accounts -->
customer_dict = [{"Name":"customer1", "Email": "customer1@customer.com", "Phone": "075 559 555", "PaymentMethod": "Pappa"},
                    {"Name":"customer2", "Email": "customer2@customer.com", "Phone": "075 155 515", "PaymentMethod": "American Express"}]

for n in customer_dict:
    Customer.insert_one(n)

    searchedForID = Customer.find_one(n, {"_id": 1})

    #Password becomes string before @ in Email
    Accounts.insert_one({"CustomerId":searchedForID["_id"], "ProviderId":None, "Email":n["Email"], "Password":(n["Email"]).split('@')[0], "Role":"customer"})

#<--
    
#putting in manufactuter accounts
Accounts.insert_one({"CustomerId":None, "ProviderId":None, "Email":"manufacturer@manufacturer.com", "Password":"manufacturer", "Role":"manufacturer"})


#creating and inserting services
Services = db.Services
Services.insert_one({"ServiceName": "basic", "FreePushes": 10, "InspectionsPerYear": 2, "MaxVariation": 2, "InterventionPriority": "low"})
Services.insert_one({"ServiceName": "gold", "FreePushes": 20, "InspectionsPerYear": 4, "MaxVariation": 1, "InterventionPriority": "medium"})
Services.insert_one({"ServiceName": "supreme", "FreePushes": 30, "InspectionsPerYear": 6, "MaxVariation": 1, "InterventionPriority": "high"})