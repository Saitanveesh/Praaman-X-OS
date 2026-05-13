from app.core.enums import LinkState


class LinkStateMachine:
    def classify(self, packet_age_seconds: float) -> LinkState:
        if packet_age_seconds < 3:
            return LinkState.FULL_LINK
        if packet_age_seconds < 8:
            return LinkState.DEGRADED_LINK
        if packet_age_seconds < 15:
            return LinkState.INTERMITTENT_LINK
        return LinkState.LOST_LINK
