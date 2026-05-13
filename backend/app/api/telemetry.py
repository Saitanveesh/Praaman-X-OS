from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.telemetry import TelemetryRead
from app.services.telemetry_service import TelemetryService, telemetry_to_schema

router = APIRouter(prefix="/api/telemetry", tags=["telemetry"])
service = TelemetryService()


@router.get("/latest/{drone_id}", response_model=TelemetryRead)
def latest_telemetry(drone_id: str, db: Session = Depends(get_db)):
    row = service.latest(db, drone_id)
    if not row:
        raise HTTPException(status_code=404, detail="Telemetry not found")
    return telemetry_to_schema(row)



@router.get("/history/{drone_id}", response_model=list[TelemetryRead])
def telemetry_history(drone_id: str, limit: int = 200, db: Session = Depends(get_db)):
    limit = max(1, min(limit, 1000))
    return [telemetry_to_schema(row) for row in service.history(db, drone_id, limit)]
