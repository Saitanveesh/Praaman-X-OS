from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.drone import Drone
from app.schemas.drone import DroneCreate, DroneRead

router = APIRouter(prefix="/api/drones", tags=["drones"])


@router.get("", response_model=list[DroneRead])
def list_drones(db: Session = Depends(get_db)):
    return db.query(Drone).order_by(Drone.drone_id).all()


@router.get("/{drone_id}", response_model=DroneRead)
def get_drone(drone_id: str, db: Session = Depends(get_db)):
    drone = db.get(Drone, drone_id)
    if not drone:
        raise HTTPException(status_code=404, detail="Drone not found")
    return drone


@router.post("", response_model=DroneRead)
def create_drone(payload: DroneCreate, db: Session = Depends(get_db)):
    drone = Drone(**payload.model_dump(mode="json"))
    db.merge(drone)
    db.commit()
    return db.get(Drone, payload.drone_id)
