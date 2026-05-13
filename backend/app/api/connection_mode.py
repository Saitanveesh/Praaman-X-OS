from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.bridge import C2ConnectionConfigRead, C2ConnectionModeUpdate
from app.services.connection_mode_service import ConnectionModeService

router = APIRouter(prefix="/api/connection-mode", tags=["connection-mode"])
service = ConnectionModeService()


@router.get("", response_model=C2ConnectionConfigRead)
def get_connection_mode(db: Session = Depends(get_db)):
    return service.get_current_mode(db)


@router.post("", response_model=C2ConnectionConfigRead)
def set_connection_mode(payload: C2ConnectionModeUpdate, db: Session = Depends(get_db)):
    return service.set_mode(db, payload.mode)
