from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.bridge import BridgeStatusRead, MAVLinkEndpointCreate, MAVLinkEndpointRead
from app.services.mavlink_bridge_service import MAVLinkBridgeService

router = APIRouter(prefix="/api/bridge", tags=["Mission Planner Bridge"])
service = MAVLinkBridgeService()


@router.get("/status", response_model=BridgeStatusRead)
def get_bridge_status(db: Session = Depends(get_db)):
    return service.get_bridge_status(db)


@router.get("/endpoints", response_model=list[MAVLinkEndpointRead])
def get_endpoints(db: Session = Depends(get_db)):
    return service.get_endpoints(db)


@router.post("/endpoints", response_model=MAVLinkEndpointRead)
def create_endpoint(payload: MAVLinkEndpointCreate, db: Session = Depends(get_db)):
    return service.create_endpoint(db, payload)
