#run this to setup accounts part of database with dummy-users

from itertools import count

from pymongo import MongoClient
from bson.objectid import ObjectId
import sys

# Setting up/connecting to database
client = MongoClient('localhost', 27017)
db = client.MowerDB

#creating "Service_Provider" table, accounts table and customer table
Service_Provider = db.Service_Provider
Accounts = db.Accounts
Customer = db.Customer


#putting serviceproviders into accounts -->
Service_Provider_dict = [{"Name":"Ulf Olovsson", "Email": "Ulol@serviceprovider.com", "Phone": "075 555 555"},
                         {"Name":"Bingus Dingus", "Email": "BingDing@serviceprovider.com", "Phone": "075 555 515"}]


for n in Service_Provider_dict:
    Service_Provider.insert_one(n)

    searchedForID = Service_Provider.find_one(n, {"_id": 1})

    Accounts.insert_one({"CustomerId":None, "ProviderId":searchedForID["_id"], "Email":n["Email"], "Password":(n["Email"]).split('@')[0], "Role":"serviceprovider"})

#<--
    
#putting customers into accounts -->
customer_dict = [{"Name":"customer1", "Email": "customer1@customer.com", "Phone": "075 559 555", "PaymentMethod": "Pappa"},
                    {"Name":"customer2", "Email": "customer2@customer.com", "Phone": "075 155 515", "PaymentMethod": "American Express"}]

for n in customer_dict:
    Customer.insert_one(n)

    searchedForID = Customer.find_one(n, {"_id": 1})

    Accounts.insert_one({"CustomerId":searchedForID["_id"], "ProviderId":None, "Email":n["Email"], "Password":(n["Email"]).split('@')[0], "Role":"customer"})

#<--
    
#putting in manufactuter accounts
Accounts.insert_one({"CustomerId":None, "ProviderId":None, "Email":"manufacturer@manufacturer.com", "Password":"m1", "Role":"manufacturer"})


#creating and inserting services
Services = db.Services
Services.insert_one({"ServiceName": "basic", "FreePushes": 10, "InspectionsPerYear": 2, "MaxVariation": 2, "InterventionPriority": "low"})
Services.insert_one({"ServiceName": "gold", "FreePushes": 20, "InspectionsPerYear": 4, "MaxVariation": 1, "InterventionPriority": "medium"})
Services.insert_one({"ServiceName": "supreme", "FreePushes": 30, "InspectionsPerYear": 6, "MaxVariation": 1, "InterventionPriority": "high"})