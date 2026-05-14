from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.sitl import SITLReadiness
from app.services.sitl_readiness_service import SITLReadinessService

router = APIRouter(prefix="/api/sitl", tags=["sitl"])
service = SITLReadinessService()


@router.get("/readiness", response_model=SITLReadiness)
def sitl_readiness(db: Session = Depends(get_db)):
    return service.get_readiness(db)
