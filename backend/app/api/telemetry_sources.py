from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.enums import TelemetrySource
from app.db.session import get_db
from app.schemas.telemetry_source import TelemetrySourceConfigRead, TelemetrySourceSetActive
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


@router.post("/active", response_model=TelemetrySourceConfigRead)
def set_active_source(payload: TelemetrySourceSetActive, db: Session = Depends(get_db)):
    try:
        return service.set_active_source(db, payload.source_type)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
