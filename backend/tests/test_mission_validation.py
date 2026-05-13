from app.core.enums import VehicleType, WaypointAction
from app.db.init_db import init_db
from app.db.session import SessionLocal
from app.schemas.mission import MapWaypointCreate, MissionDraftCreate
from app.services.mission_draft_service import MissionDraftService


def test_mission_validation_returns_summary_and_simulation_warning():
    init_db()
    service = MissionDraftService()
    with SessionLocal() as db:
        mission = service.create_mission(
            db,
            MissionDraftCreate(
                name="Validation summary test",
                drone_id="PX-QD-001",
                vehicle_type=VehicleType.QUADCOPTER,
                default_altitude_m=40,
                default_speed_mps=6,
                lost_link_action="HOLD_THEN_RTL",
            ),
        )
        service.add_waypoint(db, mission.mission_id, MapWaypointCreate(lat=12.9716, lon=77.5946, altitude_m=40, speed_mps=6, action=WaypointAction.NAVIGATE))
        service.add_waypoint(db, mission.mission_id, MapWaypointCreate(lat=12.9726, lon=77.5956, altitude_m=55, speed_mps=7, action=WaypointAction.RETURN_POINT))

        result = service.validate_mission(db, mission.mission_id)

    assert result is not None
    assert result.valid is True
    assert result.summary.waypoint_count == 2
    assert result.summary.estimated_distance_m > 0
    assert result.summary.max_altitude_m == 55
    assert result.summary.min_altitude_m == 40
    assert any("simulation-only" in warning for warning in result.warnings)


def test_mission_validation_rejects_bad_waypoint_values():
    init_db()
    service = MissionDraftService()
    with SessionLocal() as db:
        mission = service.create_mission(
            db,
            MissionDraftCreate(
                name="Invalid waypoint test",
                drone_id="PX-QD-001",
                vehicle_type=VehicleType.QUADCOPTER,
                default_altitude_m=40,
                default_speed_mps=6,
                lost_link_action="HOLD_THEN_RTL",
            ),
        )
        service.add_waypoint(db, mission.mission_id, MapWaypointCreate(lat=91, lon=181, altitude_m=0, speed_mps=0, action=WaypointAction.NAVIGATE))

        result = service.validate_mission(db, mission.mission_id)

    assert result is not None
    assert result.valid is False
    assert result.status == "INVALID"
    assert any("latitude" in error for error in result.errors)
    assert any("longitude" in error for error in result.errors)
    assert any("altitude" in error for error in result.errors)
    assert any("speed" in error for error in result.errors)
