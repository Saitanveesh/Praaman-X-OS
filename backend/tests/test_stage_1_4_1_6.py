from app.core.enums import LinkState, VehicleType, WaypointAction
from app.db.init_db import init_db
from app.db.session import SessionLocal
from app.schemas.mission import MapWaypointCreate, MissionDraftCreate, MissionImportPayload
from app.services.link_intelligence_service import LinkIntelligenceService
from app.services.mission_draft_service import MissionDraftService
from app.services.mission_simulation_service import mission_simulation_service
from app.services.sitl_readiness_service import SITLReadinessService
from app.services.telemetry_intelligence_service import TelemetryIntelligenceService
from app.services.telemetry_service import TelemetryService


def _mission_with_waypoints(db):
    service = MissionDraftService()
    mission = service.create_mission(
        db,
        MissionDraftCreate(
            name="Stage 1.6 test mission",
            drone_id="PX-QD-001",
            vehicle_type=VehicleType.QUADCOPTER,
            default_altitude_m=40,
            default_speed_mps=5,
            lost_link_action="HOLD_THEN_RTL",
        ),
    )
    service.add_waypoint(db, mission.mission_id, MapWaypointCreate(lat=12.9716, lon=77.5946, altitude_m=40, speed_mps=5, action=WaypointAction.NAVIGATE))
    service.add_waypoint(db, mission.mission_id, MapWaypointCreate(lat=12.9726, lon=77.5956, altitude_m=45, speed_mps=5, action=WaypointAction.RETURN_POINT))
    return service, mission


def test_sitl_readiness_is_documentation_only():
    init_db()
    with SessionLocal() as db:
        readiness = SITLReadinessService().get_readiness(db)
    assert readiness.status == "READY_FOR_FUTURE_SITL"
    assert readiness.read_only is True
    assert readiness.command_sending_enabled is False
    assert readiness.expected_host == "127.0.0.1"
    assert readiness.expected_port == 14550
    assert any("Do not enable hardware command execution" in item for item in readiness.checklist)


def test_telemetry_and_link_intelligence_do_not_trigger_commands():
    init_db()
    with SessionLocal() as db:
        TelemetryService().save(db, {
            "drone_id": "PX-QD-001",
            "lat": 12.9716,
            "lon": 77.5946,
            "altitude_m": 50,
            "speed_mps": 6,
            "heading_deg": 90,
            "battery_percent": 21,
            "mode": "MOCK",
            "armed": False,
            "gps_status": "GOOD",
            "link_state": LinkState.INTERMITTENT_LINK.value,
            "mission_state": "IDLE",
            "warnings": [],
        })
        telemetry = TelemetryIntelligenceService().evaluate(db, "PX-QD-001")
        link = LinkIntelligenceService().evaluate(db, "PX-QD-001")
    assert telemetry.battery_risk == "RETURN_SOON"
    assert telemetry.recommended_action == "Prepare return or mission stop."
    assert link.risk_level == "HIGH"
    assert "Avoid high-risk actions" in link.operator_message


def test_mission_replay_export_import_and_report_are_draft_only():
    init_db()
    with SessionLocal() as db:
        service, mission = _mission_with_waypoints(db)
        paused = mission_simulation_service.pause_simulation(db, mission.mission_id)
        reset = mission_simulation_service.reset_simulation(db, mission.mission_id)
        exported = service.export_mission(db, mission.mission_id)
        report = service.mission_report(db, mission.mission_id)
        imported = service.import_mission(db, MissionImportPayload(format=exported.format, mission=exported.mission.model_dump(mode="json"), waypoints=[waypoint.model_dump(mode="json") for waypoint in exported.waypoints]))
    assert paused is not None
    assert reset is not None
    assert exported is not None
    assert exported.format == "PRAMAAN_X_MISSION_DRAFT_V1"
    assert exported.hardware_upload_enabled is False
    assert report is not None
    assert report.simulation_only is True
    assert report.hardware_upload_enabled is False
    assert report.estimated_duration_s > 0
    assert imported is not None
    assert imported.status in {"VALIDATED", "DRAFT"}
