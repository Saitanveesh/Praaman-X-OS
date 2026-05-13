from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.vehicle_profile import VehicleProfileCreate, VehicleProfileRead
from app.services.vehicle_profile_service import VehicleProfileService

router = APIRouter(prefix="/api/profiles", tags=["profiles"])
service = VehicleProfileService()


@router.get("", response_model=list[VehicleProfileRead])
def list_profiles(db: Session = Depends(get_db)):
    return service.list_profiles(db)


@router.post("", response_model=VehicleProfileRead)
def create_profile(payload: VehicleProfileCreate, db: Session = Depends(get_db)):
    return service.create_profile(db, payload)
