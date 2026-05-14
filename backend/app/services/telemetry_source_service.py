from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.core.enums import MissionEventType, TelemetrySource, TelemetrySourceStatus
from app.models.mission import MissionEvent
from app.models.telemetry_source import TelemetrySourceConfig


class TelemetrySourceService:
    def ensure_defaults(self, db: Session) -> None:
        defaults = [TelemetrySourceConfig.mock_default(), TelemetrySourceConfig.sitl_placeholder(), TelemetrySourceConfig.playback_placeholder()]
        for default in defaults:
            if not db.query(TelemetrySourceConfig).filter(TelemetrySourceConfig.source_type == default.source_type).first():
                db.add(default)
        db.commit()
        if not self.get_active_source(db):
            self.set_active_source(db, TelemetrySource.MOCK)

    def get_active_source(self, db: Session) -> TelemetrySourceConfig | None:
        return db.query(TelemetrySourceConfig).filter(TelemetrySourceConfig.status == TelemetrySourceStatus.ACTIVE.value).first()

    def list_sources(self, db: Session) -> list[TelemetrySourceConfig]:
        self.ensure_defaults(db)
        return db.query(TelemetrySourceConfig).order_by(TelemetrySourceConfig.id).all()

    def set_active_source(self, db: Session, source_type: TelemetrySource) -> TelemetrySourceConfig:
        self.ensure_defaults_without_recursion(db)
        selected = db.query(TelemetrySourceConfig).filter(TelemetrySourceConfig.source_type == source_type.value).first()
        if not selected:
            raise ValueError(f"Unknown telemetry source: {source_type}")
        for source in db.query(TelemetrySourceConfig).all():
            source.status = TelemetrySourceStatus.ACTIVE.value if source.source_type == source_type.value else TelemetrySourceStatus.INACTIVE.value
            source.updated_at = datetime.now(timezone.utc)
        selected.last_error = None if source_type == TelemetrySource.MOCK else selected.last_error
        db.add(MissionEvent(
            mission_id="SYSTEM",
            drone_id="PX-QD-001",
            event_type=(MissionEventType.TELEMETRY_SOURCE_SWITCHED_TO_MOCK.value if source_type == TelemetrySource.MOCK else MissionEventType.TELEMETRY_SOURCE_SWITCHED_TO_MAVLINK_READ_ONLY.value if source_type == TelemetrySource.MAVLINK_READ_ONLY else MissionEventType.TELEMETRY_SOURCE_SWITCHED.value),
            severity="INFO",
            message=f"Telemetry source switched to {source_type.value}. Read-only mode remains enforced.",
            details=f"source_type={source_type.value}",
        ))
        db.commit()
        db.refresh(selected)
        return selected

    def ensure_defaults_without_recursion(self, db: Session) -> None:
        defaults = [TelemetrySourceConfig.mock_default(), TelemetrySourceConfig.sitl_placeholder(), TelemetrySourceConfig.playback_placeholder()]
        for default in defaults:
            if not db.query(TelemetrySourceConfig).filter(TelemetrySourceConfig.source_type == default.source_type).first():
                db.add(default)
        db.commit()

    def get_source_status(self, db: Session, source_type: TelemetrySource | None = None) -> TelemetrySourceConfig | list[TelemetrySourceConfig] | None:
        self.ensure_defaults(db)
        if source_type is None:
            return self.list_sources(db)
        return db.query(TelemetrySourceConfig).filter(TelemetrySourceConfig.source_type == source_type.value).first()

    def set_source_error(self, db: Session, source_type: TelemetrySource, error: str) -> TelemetrySourceConfig | None:
        source = db.query(TelemetrySourceConfig).filter(TelemetrySourceConfig.source_type == source_type.value).first()
        if not source:
            return None
        source.status = TelemetrySourceStatus.ERROR.value
        source.last_error = error[:512]
        source.updated_at = datetime.now(timezone.utc)
        db.add(MissionEvent(
            mission_id="SYSTEM",
            drone_id="PX-QD-001",
            event_type=MissionEventType.MAVLINK_READONLY_ERROR.value,
            severity="WARN",
            message=f"Read-only MAVLink provider error: {error[:180]}",
            details=error[:512],
        ))
        db.commit()
        db.refresh(source)
        return source
    def update_source_endpoint(self, db: Session, source_type: TelemetrySource, host: str, port: int, protocol: str) -> TelemetrySourceConfig | None:
        self.ensure_defaults_without_recursion(db)
        source = db.query(TelemetrySourceConfig).filter(TelemetrySourceConfig.source_type == source_type.value).first()
        if not source:
            return None
        source.host = host
        source.port = port
        source.protocol = protocol.upper()
        source.read_only = True
        source.updated_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(source)
        return source

    def mark_source_inactive_ready(self, db: Session, source_type: TelemetrySource) -> TelemetrySourceConfig | None:
        self.ensure_defaults_without_recursion(db)
        source = db.query(TelemetrySourceConfig).filter(TelemetrySourceConfig.source_type == source_type.value).first()
        if not source:
            return None
        if source.status != TelemetrySourceStatus.ACTIVE.value:
            source.status = TelemetrySourceStatus.INACTIVE.value
        source.last_error = None
        source.read_only = True
        source.updated_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(source)
        return source

    def record_source_switch_failed(self, db: Session, message: str) -> None:
        db.add(MissionEvent(
            mission_id="SYSTEM",
            drone_id="PX-QD-001",
            event_type=MissionEventType.TELEMETRY_SOURCE_SWITCH_FAILED.value,
            severity="WARN",
            message=message,
            details="read_only=true",
        ))
        db.commit()
