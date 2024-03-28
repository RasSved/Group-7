from bson import ObjectId
from pymongo import MongoClient

client = MongoClient('localhost', 27017)
db = client.MowerDB
taskAssignements = db.TaskAssignments

SERVICE_TICKET_KEY = "ServiceTicket"
ASSIGNED_SERVICE_PROVIDER_KEY = "AssignedServiceProvider"

taskAssignements.create_index(SERVICE_TICKET_KEY, unique = True)

class TaskAssignment:
    def __init__(self, providerId: ObjectId, serviceTicketId: ObjectId):
        self.providerId = providerId
        self.serviceTicketId = serviceTicketId

    def get_json_object(self) -> dict[str, any]:
        return {
            SERVICE_TICKET_KEY: self.serviceTicketId,
            ASSIGNED_SERVICE_PROVIDER_KEY: self.providerId,
        }

def assignment_to_ticket_exist(serviceTicketId: ObjectId) -> bool: 
    result = taskAssignements.find_one({SERVICE_TICKET_KEY: serviceTicketId})
    return result != None

def assign_task(providerId: ObjectId, serviceTicketId: ObjectId):
    taskAssignment = TaskAssignment(providerId=providerId, serviceTicketId=serviceTicketId)
    taskAssignements.insert_one(taskAssignment.get_json_object())
    return taskAssignements.find_one(taskAssignment.get_json_object())


def is_provider_assigned(providerId: ObjectId, serviceTicketId: ObjectId) -> bool:
    result = taskAssignements.find_one({SERVICE_TICKET_KEY: serviceTicketId})
    if assignment_to_ticket_exist(serviceTicketId=serviceTicketId) == False:
        return False
    
    if result == None:
        return False
    
    return result[ASSIGNED_SERVICE_PROVIDER_KEY] == providerId
