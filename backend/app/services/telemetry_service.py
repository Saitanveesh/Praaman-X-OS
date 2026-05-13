from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app.models.telemetry import Telemetry
from app.schemas.telemetry import TelemetryRead


def telemetry_to_schema(row: Telemetry) -> TelemetryRead:
    data = {c.name: getattr(row, c.name) for c in row.__table__.columns if c.name != "id"}
    data["warnings"] = [w for w in (row.warnings or "").split("|") if w]
    return TelemetryRead(**data)


class TelemetryService:
    def latest(self, db: Session, drone_id: str) -> Telemetry | None:
        return db.query(Telemetry).filter(Telemetry.drone_id == drone_id).order_by(Telemetry.timestamp.desc()).first()

    def history(self, db: Session, drone_id: str, limit: int = 200) -> list[Telemetry]:
        rows = db.query(Telemetry).filter(Telemetry.drone_id == drone_id).order_by(Telemetry.timestamp.desc()).limit(limit).all()
        return list(reversed(rows))

    def save(self, db: Session, payload: dict) -> Telemetry:
        data = dict(payload)
        warnings = data.pop("warnings", [])
        if isinstance(warnings, list):
            warnings = "|".join(warnings)
        if isinstance(data.get("timestamp"), str):
            data["timestamp"] = datetime.fromisoformat(data["timestamp"].replace("Z", "+00:00"))
        data.setdefault("timestamp", datetime.now(timezone.utc))
        obj = Telemetry(**data, warnings=warnings)
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return obj
