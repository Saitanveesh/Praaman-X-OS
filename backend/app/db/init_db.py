from app.core.enums import VehicleType
from app.db.session import Base, engine, SessionLocal
from app.models.audit import AuditLog  # noqa: F401
from app.models.command import Command  # noqa: F401
from app.models.drone import Drone
from app.models.telemetry import Telemetry  # noqa: F401
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
        db.commit()
