from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.enums import TelemetrySource
from app.db.session import get_db
from app.schemas.telemetry_source import TelemetrySourceConfigRead, TelemetrySourceSetActive
from app.services.mavlink_readonly_runtime import mavlink_readonly_provider
from app.services.telemetry_source_service import TelemetrySourceService

router = APIRouter(prefix="/api/telemetry-sources", tags=["telemetry-sources"])
service = TelemetrySourceService()


@router.get("", response_model=list[TelemetrySourceConfigRead])
def list_sources(db: Session = Depends(get_db)):
    return service.list_sources(db)


@router.get("/active", response_model=TelemetrySourceConfigRead)
def active_source(db: Session = Depends(get_db)):
    source = service.get_active_source(db)
    if not source:
        source = service.set_active_source(db, TelemetrySource.MOCK)
    return source


@router.post("/active")
def set_active_source(payload: TelemetrySourceSetActive, db: Session = Depends(get_db)):
    try:
        if payload.source_type == TelemetrySource.MAVLINK_READ_ONLY and not mavlink_readonly_provider.is_connected():
            service.record_source_switch_failed(db, "MAVLink source unavailable. Staying on MOCK.")
            selected = service.set_active_source(db, TelemetrySource.MOCK)
            return {
                "id": selected.id,
                "source_type": selected.source_type,
                "active_source": selected.source_type,
                "status": "ERROR",
                "name": selected.name,
                "host": selected.host,
                "port": selected.port,
                "protocol": selected.protocol,
                "read_only": True,
                "last_error": "MAVLink source unavailable. Staying on MOCK.",
                "created_at": selected.created_at,
                "updated_at": selected.updated_at,
                "message": "MAVLink source unavailable. Staying on MOCK.",
            }
        selected = service.set_active_source(db, payload.source_type)
        message = "MAVLink read-only telemetry source active." if payload.source_type == TelemetrySource.MAVLINK_READ_ONLY else "Mock telemetry source active."
        return {
            "id": selected.id,
            "source_type": selected.source_type,
            "active_source": selected.source_type,
            "status": selected.status,
            "name": selected.name,
            "host": selected.host,
            "port": selected.port,
            "protocol": selected.protocol,
            "read_only": selected.read_only,
            "last_error": selected.last_error,
            "created_at": selected.created_at,
            "updated_at": selected.updated_at,
            "message": message,
        }
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
