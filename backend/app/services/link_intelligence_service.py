from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.schemas.intelligence import LinkIntelligence
from app.services.telemetry_service import TelemetryService


class LinkIntelligenceService:
    def __init__(self) -> None:
        self._telemetry = TelemetryService()

    def evaluate(self, db: Session, drone_id: str) -> LinkIntelligence:
        latest = self._telemetry.latest(db, drone_id)
        link_state = latest.link_state if latest else "LOST_LINK"
        mapping = {
            "FULL_LINK": ("HIGH", "LOW", "Link healthy.", "Continue monitoring."),
            "DEGRADED_LINK": ("REDUCED", "MEDIUM", "Link degraded. Reduce bandwidth and monitor.", "Avoid nonessential actions and monitor telemetry freshness."),
            "INTERMITTENT_LINK": ("UNSTABLE", "HIGH", "Link intermittent. Avoid high-risk actions.", "Hold simulation-only operations until link stabilizes."),
            "LOST_LINK": ("NONE", "CRITICAL", "Link lost. Only onboard failsafe/simulation policy applies.", "Do not initiate operator-driven actions; verify telemetry source."),
            "RECOVERED_LINK": ("RECOVERING", "MEDIUM", "Link recovered. Re-check telemetry freshness.", "Confirm fresh telemetry before continuing supervision."),
        }
        link_quality, risk, message, action = mapping.get(link_state, ("UNKNOWN", "HIGH", "Unknown link state. Treat as degraded.", "Verify source and continue read-only monitoring."))
        return LinkIntelligence(
            drone_id=drone_id,
            link_state=link_state,
            link_quality=link_quality,
            operator_message=message,
            risk_level=risk,
            recommended_action=action,
            timestamp=datetime.now(timezone.utc),
        )
