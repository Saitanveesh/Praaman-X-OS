from app.core.enums import C2ConnectionMode, MAVLinkBridgeStatus, VehicleType
from app.models.bridge import C2ConnectionConfig, MAVLinkEndpoint
from app.models.mission import GeofenceDraft, MapWaypoint, MissionDraft, MissionEvent  # noqa: F401
from app.services.connection_mode_service import ConnectionModeService
from app.services.telemetry_source_service import TelemetrySourceService
from app.db.session import Base, engine, SessionLocal
from app.models.audit import AuditLog  # noqa: F401
from app.models.command import Command  # noqa: F401
from app.models.drone import Drone
from app.models.telemetry import Telemetry  # noqa: F401
from app.models.telemetry_source import TelemetrySourceConfig  # noqa: F401
from app.models.vehicle_profile import VehicleProfile


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        if not db.get(VehicleProfile, "quad-basic"):
            db.add(VehicleProfile(
                profile_id="quad-basic",
                name="Quadcopter Profile",
                vehicle_type=VehicleType.QUADCOPTER.value,
                capabilities={"hover_capable": True, "default_lost_link_action": "HOLD_THEN_RTL", "vertical_landing": True},
                safety_limits={"max_altitude_m": 120, "max_speed_mps": 20},
            ))
        if not db.get(VehicleProfile, "fixed-wing-basic"):
            db.add(VehicleProfile(
                profile_id="fixed-wing-basic",
                name="Fixed-wing Profile",
                vehicle_type=VehicleType.FIXED_WING.value,
                capabilities={
                    "hover_capable": False,
                    "default_lost_link_action": "LOITER_THEN_RTL",
                    "requires_minimum_airspeed": True,
                    "landing_behavior": "PREDEFINED_CORRIDOR",
                },
                safety_limits={"minimum_airspeed_mps": 12, "max_altitude_m": 200},
            ))
        if not db.get(Drone, "PX-QD-001"):
            db.add(Drone(
                drone_id="PX-QD-001",
                name="Pramaan-X Quad Testbed",
                vehicle_type=VehicleType.QUADCOPTER.value,
                flight_stack="ARDUPILOT",
                firmware_version="SIM-0.1",
                status="CONNECTED",
                profile_id="quad-basic",
            ))

        if not db.query(MAVLinkEndpoint).filter(MAVLinkEndpoint.endpoint_id == "mavlink-sim-placeholder").first():
            db.add(MAVLinkEndpoint(
                endpoint_id="mavlink-sim-placeholder",
                name="Simulation MAVLink Bridge Placeholder",
                host="127.0.0.1",
                port=14550,
                protocol="UDP",
                status=MAVLinkBridgeStatus.SIMULATION_ONLY.value,
                read_only=True,
            ))
        if not db.query(C2ConnectionConfig).first():
            ConnectionModeService().set_mode(db, C2ConnectionMode.SETUP_MODE)
        TelemetrySourceService().ensure_defaults(db)
        db.commit()
