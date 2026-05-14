from pydantic import BaseModel
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.enums import TelemetrySource
from app.db.session import get_db
from app.models.mission import MissionEvent
from app.core.enums import MissionEventType
from app.services.mavlink_readonly_runtime import mavlink_readonly_provider
from app.services.telemetry_source_service import TelemetrySourceService

router = APIRouter(prefix="/api/mavlink-readonly", tags=["mavlink-readonly"])
source_service = TelemetrySourceService()


class MAVLinkConnectRequest(BaseModel):
    host: str = "127.0.0.1"
    port: int = 14550
    protocol: str = "UDP"


def _audit(db: Session, event_type: MissionEventType, message: str, severity: str = "INFO", details: str | None = None) -> None:
    db.add(MissionEvent(mission_id="SYSTEM", drone_id="PX-QD-001", event_type=event_type.value, severity=severity, message=message, details=details))
    db.commit()


@router.get("/status")
def status():
    return mavlink_readonly_provider.get_status()


@router.post("/connect")
def connect(payload: MAVLinkConnectRequest | None = None, db: Session = Depends(get_db)):
    request = payload or MAVLinkConnectRequest()
    status_payload = mavlink_readonly_provider.connect(host=request.host, port=request.port, protocol=request.protocol)
    source_service.update_source_endpoint(db, TelemetrySource.MAVLINK_READ_ONLY, request.host, request.port, request.protocol)
    if not status_payload["connected"]:
        error = status_payload.get("last_error") or "Unknown MAVLink read-only connection error"
        source_service.set_source_error(db, TelemetrySource.MAVLINK_READ_ONLY, error)
        return {"ok": False, **status_payload}
    source_service.mark_source_inactive_ready(db, TelemetrySource.MAVLINK_READ_ONLY)
    _audit(db, MissionEventType.MAVLINK_READONLY_CONNECTED, f"MAVLink read-only listener connected on {status_payload['endpoint']}", details=str(status_payload))
    return {"ok": True, **status_payload}


@router.post("/disconnect")
def disconnect(db: Session = Depends(get_db)):
    status_payload = mavlink_readonly_provider.disconnect()
    _audit(db, MissionEventType.MAVLINK_READONLY_DISCONNECTED, "MAVLink read-only listener disconnected.", details=str(status_payload))
    return {"ok": True, **status_payload}
