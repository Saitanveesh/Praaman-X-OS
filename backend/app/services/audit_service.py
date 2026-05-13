from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app.models.audit import AuditLog


class AuditService:
    def record(self, db: Session, *, operator_id: str, drone_id: str, event_type: str, decision: str, reason: str, command_id: str | None = None) -> AuditLog:
        entry = AuditLog(
            timestamp=datetime.now(timezone.utc),
            operator_id=operator_id,
            drone_id=drone_id,
            event_type=event_type,
            command_id=command_id,
            decision=decision,
            reason=reason,
        )
        db.add(entry)
        db.commit()
        db.refresh(entry)
        return entry
