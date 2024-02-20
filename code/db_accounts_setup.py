#run this to setup accounts part of database with dummy-users

from itertools import count

from pymongo import MongoClient
from bson.objectid import ObjectId
import sys

# Setting up/connecting to database
client = MongoClient('localhost', 27017)
db = client.MowerDB

#creating "Service_Provider" table and accounts table
Service_Provider = db.Service_Provider
accounts = db.Accounts

#setting up counter as Id-creator
ACCId_counter = count()
CustomerId_counter = count()
ProviderId_counter = count()

#putting serviceproviders into accounts -->
Service_Provider_dict = [{"Name":"Ulf Olovsson", "Email": "Ulol@serviceprovider@com", "Phone": "075 555 555"},
                         {"Name":"Bingus Dingus", "Email": "BingDing@serviceprovider@com", "Phone": "075 555 515"}]

for n in Service_Provider_dict:
    Service_Provider.insert_one(n)

    searchedForID = Service_Provider.find_one(n, {"_id": 1})

    accounts.insert_one({"CustomerId":None, "ProviderId":searchedForID, "Email":n["Email"], "Password":(n["Email"]).split('@')[0], "Role":"serviceprovider"})


#<--

    
#putting in accounts
accounts.insert_one({"CustomerId":None, "ProviderId":None, "Email":"manufacturer@manufacturer.com", "Password":"m1", "Role":"manufacturer"})
#accounts.insert_one({"CustomerId":None, "ProviderId":next(ProviderId_counter), "Email":, "Password":"s1", "Role":"serviceprovider"})
accounts.insert_one({"CustomerId":next(CustomerId_counter), "ProviderId":None, "Email":"customer@customer.com", "Password":"c1", "Role":"customer"})

