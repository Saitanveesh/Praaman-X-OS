from app.core.enums import DroneState, LinkState


class DroneStateMachine:
    def from_telemetry(self, telemetry) -> DroneState:
        if telemetry is None:
            return DroneState.UNSEEN
        if telemetry.link_state == LinkState.LOST_LINK:
            return DroneState.LOST_LINK
        if telemetry.battery_percent < 20 or telemetry.link_state in {LinkState.DEGRADED_LINK, LinkState.INTERMITTENT_LINK}:
            return DroneState.DEGRADED
        return DroneState.READY
