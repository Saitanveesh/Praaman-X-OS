from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.mission import GeofenceDraftCreate, GeofenceDraftRead
from app.services.geofence_service import GeofenceService

router = APIRouter(prefix="/api/geofences", tags=["geofences"])
service = GeofenceService()


@router.get("", response_model=list[GeofenceDraftRead])
def list_geofences(db: Session = Depends(get_db)):
    return service.list_geofences(db)


@router.post("", response_model=GeofenceDraftRead)
def create_geofence(payload: GeofenceDraftCreate, db: Session = Depends(get_db)):
    return service.create_geofence(db, payload)
