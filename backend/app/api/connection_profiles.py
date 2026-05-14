from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.connection_profile import ConnectionProfileCreate, ConnectionProfileRead
from app.services.connection_profile_service import ConnectionProfileService

router = APIRouter(prefix="/api/connection-profiles", tags=["connection-profiles"])
service = ConnectionProfileService()


@router.get("", response_model=list[ConnectionProfileRead])
def list_connection_profiles(db: Session = Depends(get_db)):
    return service.list_profiles(db)


@router.post("", response_model=ConnectionProfileRead)
def create_connection_profile(payload: ConnectionProfileCreate, db: Session = Depends(get_db)):
    existing = service.get_profile(db, payload.profile_id)
    if existing:
        raise HTTPException(status_code=409, detail="Connection profile already exists")
    return service.create_profile(db, payload)


@router.get("/{profile_id}", response_model=ConnectionProfileRead)
def get_connection_profile(profile_id: str, db: Session = Depends(get_db)):
    profile = service.get_profile(db, profile_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Connection profile not found")
    return profile
