import os
from bson import ObjectId
from pymongo import MongoClient
import requests

database_address = os.environ.get("DATABASE_ADDRESS", "localhost")
database_port = os.environ.get("DATABASE_PORT", "27017")
client = MongoClient(database_address, int(database_port))
db = client.MowerDB
taskAssignements = db.TaskAssignments

WORK_TASK_ID_KEY = "WorkTaskId"
ASSIGNED_SERVICE_PROVIDER_KEY = "AssignedServiceProvider"

taskAssignements.create_index(WORK_TASK_ID_KEY, unique = True)

class TaskAssignment:
    def __init__(self, providerId: ObjectId, workTaskId: str):
        self.providerId = providerId
        self.workTaskId = workTaskId

    def get_json_object(self) -> dict[str, any]:
        return {
            WORK_TASK_ID_KEY: self.workTaskId,
            ASSIGNED_SERVICE_PROVIDER_KEY: self.providerId,
        }

def assignment_to_task_exist(workTaskId: ObjectId) -> bool: 
    result = taskAssignements.find_one({WORK_TASK_ID_KEY: workTaskId})
    return result != None

def assign_task(providerId: ObjectId, workTaskId: str, takeTaskUrl: str) -> (TaskAssignment | None):
    taskAssignment = TaskAssignment(providerId=providerId, workTaskId=workTaskId)
    taskAssignements.insert_one(taskAssignment.get_json_object())

    result = taskAssignements.find_one(taskAssignment.get_json_object())

    if (result != None):
        # data to be sent to api
        data = {
            'workId': workTaskId,
        }
        
        # sending post request and saving response as response object
        r = requests.post(url=takeTaskUrl, json=data)
        print(r.json())
        if r.ok == False: 
            return None

    return result

def complete_task(providerId: ObjectId, workTaskId: str) -> bool: 
    if (is_provider_assigned(providerId=providerId, workTaskId=workTaskId) == False):
        return False
    
    taskAssignment = TaskAssignment(providerId=providerId, workTaskId=workTaskId)
    result = taskAssignements.delete_one(taskAssignment.get_json_object())
    print(result)

    # Insert external complete work code here!

    return True


def is_provider_assigned(providerId: ObjectId, workTaskId: str) -> bool:
    result = taskAssignements.find_one({WORK_TASK_ID_KEY: workTaskId})
    if assignment_to_task_exist(workTaskId=workTaskId) == False:
        return False
    
    if result == None:
        return False
    
    return result[ASSIGNED_SERVICE_PROVIDER_KEY] == providerId
