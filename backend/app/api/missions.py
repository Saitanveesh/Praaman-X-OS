from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.mission import MapWaypointCreate, MapWaypointRead, MissionDraftCreate, MissionDraftRead, MissionRouteSummary, MissionValidationRead
from app.services.mission_draft_service import MissionDraftService

router = APIRouter(prefix="/api/missions", tags=["missions"])
service = MissionDraftService()


@router.get("", response_model=list[MissionDraftRead])
def list_missions(db: Session = Depends(get_db)):
    return service.list_missions(db)


@router.post("", response_model=MissionDraftRead)
def create_mission(payload: MissionDraftCreate, db: Session = Depends(get_db)):
    return service.create_mission(db, payload)


@router.get("/{mission_id}", response_model=MissionDraftRead)
def get_mission(mission_id: str, db: Session = Depends(get_db)):
    mission = service.get_mission(db, mission_id)
    if not mission:
        raise HTTPException(status_code=404, detail="Mission draft not found")
    return mission


@router.post("/{mission_id}/waypoints", response_model=MapWaypointRead)
def add_waypoint(mission_id: str, payload: MapWaypointCreate, db: Session = Depends(get_db)):
    waypoint = service.add_waypoint(db, mission_id, payload)
    if not waypoint:
        raise HTTPException(status_code=404, detail="Mission draft not found")
    return waypoint


@router.get("/{mission_id}/waypoints", response_model=list[MapWaypointRead])
def list_waypoints(mission_id: str, db: Session = Depends(get_db)):
    if not service.get_mission(db, mission_id):
        raise HTTPException(status_code=404, detail="Mission draft not found")
    return service.list_waypoints(db, mission_id)


@router.post("/{mission_id}/validate", response_model=MissionValidationRead)
def validate_mission(mission_id: str, db: Session = Depends(get_db)):
    result = service.validate_mission(db, mission_id)
    if not result:
        raise HTTPException(status_code=404, detail="Mission draft not found")
    return result


@router.get("/{mission_id}/summary", response_model=MissionRouteSummary)
def mission_summary(mission_id: str, db: Session = Depends(get_db)):
    result = service.summarize_route(db, mission_id)
    if not result:
        raise HTTPException(status_code=404, detail="Mission draft not found")
    return result
