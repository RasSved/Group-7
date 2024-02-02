#run this to setup accounts part of database with dummy-users

from itertools import count

from pymongo import MongoClient
from bson.objectid import ObjectId
import sys

# Setting up/connecting to database
client = MongoClient('localhost', 27017)
db = client.MowerDB

#setting up counter as Id-creator
ACCId_counter = count()
CustomerId_counter = count()
ProviderId_counter = count()

#creating table and putting in accounts
accounts = db.Accounts
accounts.insert_one({"ACCId": next(ACCId_counter), "CustomerId":None, "ProviderId":None, "Username":"manufacturer", "Password":"m1", "Role":"manufacturer"})
accounts.insert_one({"ACCId": next(ACCId_counter), "CustomerId":None, "ProviderId":next(ProviderId_counter), "Username":"serviceprovider", "Password":"s1", "Role":"serviceprovider"})
accounts.insert_one({"ACCId": next(ACCId_counter), "CustomerId":next(CustomerId_counter), "ProviderId":None, "Username":"customer", "Password":"c1", "Role":"customer"})
