from enum import Enum

class WorkTaskType(Enum):
    STUCK = 'stuck'
    BLADE_CHANGE = 'blade-change'
    BUMPT_TERRAIN = 'bumpy-terrain'
    TRAPPED = 'trapped'
    REPLACE_BATTERY = 'replace-battery'

    @staticmethod
    def from_str(wotkTask):
        match wotkTask:
            case WorkTaskType.STUCK.value:
                return WorkTaskType.STUCK
            case WorkTaskType.BLADE_CHANGE.value:
                return WorkTaskType.BLADE_CHANGE
            case WorkTaskType.BUMPT_TERRAIN.value:
                return WorkTaskType.BUMPT_TERRAIN
            case WorkTaskType.TRAPPED.value:
                return WorkTaskType.STUCK
            case WorkTaskType.REPLACE_BATTERY.value:
                return WorkTaskType.REPLACE_BATTERY
            case _:
                raise NotImplementedError
    