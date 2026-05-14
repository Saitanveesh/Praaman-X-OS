from sqlalchemy.orm import Session

from app.core.enums import TelemetrySource
from app.schemas.sitl import SITLReadiness
from app.services.telemetry_source_service import TelemetrySourceService


class SITLReadinessService:
    def __init__(self) -> None:
        self._sources = TelemetrySourceService()

    def get_readiness(self, db: Session) -> SITLReadiness:
        active = self._sources.get_active_source(db)
        mavlink = self._sources.get_source_status(db, TelemetrySource.MAVLINK_READ_ONLY)
        return SITLReadiness(
            status="READY_FOR_FUTURE_SITL",
            read_only=True,
            command_sending_enabled=False,
            expected_host="127.0.0.1",
            expected_port=14550,
            telemetry_source=active.source_type if active else TelemetrySource.MOCK.value,
            mavlink_provider_status=getattr(mavlink, "status", "INACTIVE"),
            mission_planner_role="Calibration, firmware setup, frame setup, radio/compass/accelerometer calibration, ESC/motor testing, parameters, and initial failsafes.",
            pramaanx_role="Operational intelligence, telemetry supervision, command governance, audit logging, vehicle profiles, mission draft planning, and future secure C2 integration.",
            checklist=[
                "Keep Mission Planner for setup/calibration.",
                "Use MAVProxy or MAVLink Router later to split telemetry.",
                "Keep Pramaan-X OS read-only during SITL telemetry testing.",
                "Verify telemetry freshness before enabling any future governed command mode.",
                "Do not enable hardware command execution in Stage 1.",
            ],
            warnings=[
                "Documentation/checklist only: Pramaan-X OS does not launch SITL in Stage 2.0.",
                "MAVLink command sending and mission upload remain disabled.",
            ],
            recommended_next_step="Start SITL externally, route UDP MAVLink to 127.0.0.1:14550, then connect MAVLink Read-Only from Pramaan-X OS.",
            sitl_supported=True,
            mavlink_readonly_supported=True,
            recommended_sitl_out="127.0.0.1:14550",
            mission_planner_coexistence=True,
            documentation_only_commands=[
                "sim_vehicle.py -v ArduCopter --console --map --out=127.0.0.1:14550",
                "mavproxy.py --master=udp:127.0.0.1:14550 --out=127.0.0.1:14551",
            ],
        )
