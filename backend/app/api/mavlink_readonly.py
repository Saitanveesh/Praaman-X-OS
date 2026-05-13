from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.enums import TelemetrySource
from app.db.session import get_db
from app.plugins.mavlink_readonly_provider import MAVLinkReadOnlyProvider
from app.services.telemetry_source_service import TelemetrySourceService

router = APIRouter(prefix="/api/mavlink-readonly", tags=["mavlink-readonly"])
source_service = TelemetrySourceService()
provider = MAVLinkReadOnlyProvider()


@router.get("/status")
def status():
    return provider.get_status()


@router.post("/connect")
def connect(db: Session = Depends(get_db)):
    source = source_service.get_source_status(db, TelemetrySource.MAVLINK_READ_ONLY)
    host = getattr(source, "host", None) or "127.0.0.1"
    port = getattr(source, "port", None) or 14550
    protocol = getattr(source, "protocol", None) or "UDP"
    global provider
    provider = MAVLinkReadOnlyProvider(host=host, port=port, protocol=protocol)
    ok = provider.connect()
    if not ok:
        status_payload = provider.get_status()
        source_service.set_source_error(db, TelemetrySource.MAVLINK_READ_ONLY, status_payload.get("last_error") or "Unknown MAVLink read-only connection error")
        return {"ok": False, **status_payload}
    return {"ok": True, **provider.get_status()}


@router.post("/disconnect")
def disconnect():
    provider.disconnect()
    return {"ok": True, **provider.get_status()}
