from enum import Enum

class WorkTaskType(Enum):
    STUCK = 'stuck'
    BLADE_CHANGE = 'blade-change'
    BUMPT_TERRAIN = 'bumpy-terrain'

    @staticmethod
    def from_str(wotkTask):
        match wotkTask:
            case WorkTaskType.STUCK.value:
                return WorkTaskType.STUCK
            case WorkTaskType.BLADE_CHANGE.value:
                return WorkTaskType.BLADE_CHANGE
            case WorkTaskType.BUMPT_TERRAIN.value:
                return WorkTaskType.BUMPT_TERRAIN
            case _:
                raise NotImplementedError
    