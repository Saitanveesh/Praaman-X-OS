from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.schemas.intelligence import TelemetryIntelligence
from app.services.telemetry_service import TelemetryService


class TelemetryIntelligenceService:
    def __init__(self) -> None:
        self._telemetry = TelemetryService()

    def evaluate(self, db: Session, drone_id: str) -> TelemetryIntelligence:
        latest = self._telemetry.latest(db, drone_id)
        now = datetime.now(timezone.utc)
        if latest is None:
            return TelemetryIntelligence(
                drone_id=drone_id,
                battery_level=0,
                battery_risk="UNKNOWN",
                altitude_status="UNKNOWN",
                speed_status="UNKNOWN",
                gps_status="UNKNOWN",
                telemetry_freshness="LOST_OR_STALE",
                recommended_action="Start or verify mock telemetry before demo operations.",
                warnings=["No telemetry sample is available for this drone."],
                summary="Telemetry unavailable; no command action is triggered.",
                timestamp=now,
            )

        battery = int(latest.battery_percent) if latest.battery_percent is not None else 0
        if latest.battery_percent is None:
            risk = "UNKNOWN"
            action = "Battery percentage unavailable in MAVLink stream; continue read-only monitoring."
        elif battery >= 60:
            risk = "NORMAL"
            action = "Continue monitoring."
        elif battery >= 35:
            risk = "WATCH"
            action = "Monitor battery trend."
        elif battery >= 20:
            risk = "RETURN_SOON"
            action = "Prepare return or mission stop."
        else:
            risk = "CRITICAL"
            action = "Simulation warning only: landing/RTL should be considered."

        sample_time = latest.timestamp
        if sample_time.tzinfo is None:
            sample_time = sample_time.replace(tzinfo=timezone.utc)
        age = (now - sample_time).total_seconds()
        if age <= 3:
            freshness = "FRESH"
        elif age <= 10:
            freshness = "STALE"
        else:
            freshness = "LOST_OR_STALE"

        warnings = [w for w in (latest.warnings or "").split("|") if w]
        if risk in {"RETURN_SOON", "CRITICAL"}:
            warnings.append(f"Battery risk is {risk}; no automatic command will be sent.")
        if freshness != "FRESH":
            warnings.append(f"Telemetry is {freshness}; verify source before decisions.")
        if latest.gps_status != "GOOD":
            warnings.append("Position reliability degraded.")

        altitude_status = "NOMINAL" if 0 <= latest.altitude_m <= 120 else "CHECK_ALTITUDE_LIMITS"
        speed_status = "NOMINAL" if 0 <= latest.speed_mps <= 20 else "CHECK_SPEED_LIMITS"
        gps_status = "Position reliable." if latest.gps_status == "GOOD" else "Position reliability degraded."

        return TelemetryIntelligence(
            drone_id=drone_id,
            battery_level=battery,
            battery_risk=risk,
            altitude_status=altitude_status,
            speed_status=speed_status,
            gps_status=gps_status,
            telemetry_freshness=freshness,
            recommended_action=action,
            warnings=warnings,
            summary=f"Battery {battery}% is {risk}; telemetry is {freshness}. {action}",
            timestamp=now,
        )
