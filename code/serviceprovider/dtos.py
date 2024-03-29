from enum import Enum
import serviceprovider.work_tasks as work_tasks

class NewWorkTask:
    def __init__(self, workTask: work_tasks.WorkTaskType, tecnicianSystemSlug: str, mowerSystemSlug: str, workTaskId: str) -> None:
        self.workTaskType = workTask
        self.tecnicianSystemSlug = tecnicianSystemSlug
        self.mowerSystemSlug = mowerSystemSlug
        self.workTaskId = workTaskId
