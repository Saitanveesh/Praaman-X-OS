from app.core.enums import MissionState


class MissionStateMachine:
    def can_transition(self, current: MissionState, new: MissionState) -> bool:
        allowed = {
            MissionState.IDLE: {MissionState.PLANNED, MissionState.RUNNING},
            MissionState.PLANNED: {MissionState.VALIDATED, MissionState.ABORTED},
            MissionState.VALIDATED: {MissionState.RUNNING, MissionState.ABORTED},
            MissionState.RUNNING: {MissionState.PAUSED, MissionState.COMPLETED, MissionState.ABORTED},
            MissionState.PAUSED: {MissionState.RUNNING, MissionState.ABORTED},
        }
        return new in allowed.get(current, set())
