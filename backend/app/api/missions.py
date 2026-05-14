from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.mission import MapWaypointCreate, MapWaypointRead, MissionDraftCreate, MissionDraftRead, MissionEventRead, MissionExportRead, MissionImportPayload, MissionReportRead, MissionRouteSummary, MissionSimulationStatusRead, MissionValidationRead
from app.models.mission import MissionEvent
from app.services.mission_draft_service import MissionDraftService
from app.services.mission_simulation_service import mission_simulation_service

router = APIRouter(prefix="/api/missions", tags=["missions"])
service = MissionDraftService()


def _status_payload(result, db: Session, mission_id: str):
    return {"mission_id": result.mission_id, "state": result.state.value, "active_waypoint_index": result.active_waypoint_index, "waypoint_count": len(service.list_waypoints(db, mission_id)), "message": result.message}


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



@router.get("/{mission_id}/events", response_model=list[MissionEventRead])
def mission_events(mission_id: str, db: Session = Depends(get_db)):
    if not service.get_mission(db, mission_id):
        raise HTTPException(status_code=404, detail="Mission draft not found")
    return db.query(MissionEvent).filter(MissionEvent.mission_id == mission_id).order_by(MissionEvent.timestamp.desc()).limit(100).all()[::-1]


@router.post("/{mission_id}/simulate/start", response_model=MissionSimulationStatusRead)
def start_simulation(mission_id: str, db: Session = Depends(get_db)):
    result = mission_simulation_service.start_simulation(db, mission_id)
    if not result:
        raise HTTPException(status_code=404, detail="Mission draft not found")
    return _status_payload(result, db, mission_id)


@router.post("/{mission_id}/simulate/stop", response_model=MissionSimulationStatusRead)
def stop_simulation(mission_id: str, db: Session = Depends(get_db)):
    result = mission_simulation_service.stop_simulation(db, mission_id)
    if not result:
        raise HTTPException(status_code=404, detail="Mission draft not found")
    return _status_payload(result, db, mission_id)


@router.get("/{mission_id}/simulate/status", response_model=MissionSimulationStatusRead)
def simulation_status(mission_id: str, db: Session = Depends(get_db)):
    result = mission_simulation_service.get_simulation_status(db, mission_id)
    if not result:
        raise HTTPException(status_code=404, detail="Mission draft not found")
    return _status_payload(result, db, mission_id)


@router.post("/{mission_id}/simulate/pause", response_model=MissionSimulationStatusRead)
def pause_simulation(mission_id: str, db: Session = Depends(get_db)):
    result = mission_simulation_service.pause_simulation(db, mission_id)
    if not result:
        raise HTTPException(status_code=404, detail="Mission draft not found")
    return _status_payload(result, db, mission_id)


@router.post("/{mission_id}/simulate/resume", response_model=MissionSimulationStatusRead)
def resume_simulation(mission_id: str, db: Session = Depends(get_db)):
    result = mission_simulation_service.resume_simulation(db, mission_id)
    if not result:
        raise HTTPException(status_code=404, detail="Mission draft not found")
    return _status_payload(result, db, mission_id)


@router.post("/{mission_id}/simulate/reset", response_model=MissionSimulationStatusRead)
def reset_simulation(mission_id: str, db: Session = Depends(get_db)):
    result = mission_simulation_service.reset_simulation(db, mission_id)
    if not result:
        raise HTTPException(status_code=404, detail="Mission draft not found")
    return _status_payload(result, db, mission_id)


@router.get("/{mission_id}/export", response_model=MissionExportRead)
def export_mission(mission_id: str, db: Session = Depends(get_db)):
    result = service.export_mission(db, mission_id)
    if not result:
        raise HTTPException(status_code=404, detail="Mission draft not found")
    return result


@router.post("/import", response_model=MissionDraftRead)
def import_mission(payload: MissionImportPayload, db: Session = Depends(get_db)):
    result = service.import_mission(db, payload)
    if not result:
        raise HTTPException(status_code=400, detail="Unsupported mission draft import format")
    return result


@router.get("/{mission_id}/report", response_model=MissionReportRead)
def mission_report(mission_id: str, db: Session = Depends(get_db)):
    result = service.mission_report(db, mission_id)
    if not result:
        raise HTTPException(status_code=404, detail="Mission draft not found")
    return result
