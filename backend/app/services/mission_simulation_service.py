import math
from dataclasses import dataclass
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.core.enums import MissionEventType, MissionSimulationState, TelemetrySource
from app.models.mission import MapWaypoint, MissionDraft, MissionEvent
from app.models.telemetry import Telemetry
from app.services.audit_service import AuditService
from app.services.telemetry_service import TelemetryService
from app.services.telemetry_source_service import TelemetrySourceService


@dataclass
class SimulationRuntime:
    mission_id: str
    state: MissionSimulationState
    active_waypoint_index: int = 0
    message: str = ""


class MissionSimulationService:
    def __init__(self) -> None:
        self._runs: dict[str, SimulationRuntime] = {}
        self._telemetry = TelemetryService()
        self._sources = TelemetrySourceService()
        self._audit = AuditService()

    def start_simulation(self, db: Session, mission_id: str) -> SimulationRuntime | None:
        mission = db.query(MissionDraft).filter(MissionDraft.mission_id == mission_id).first()
        if not mission:
            return None
        active = self._sources.get_active_source(db)
        if not active or active.source_type != TelemetrySource.MOCK.value:
            runtime = SimulationRuntime(mission_id, MissionSimulationState.ERROR, 0, "Mission simulation only runs with MOCK telemetry active.")
            self._runs[mission_id] = runtime
            self._record_event(db, mission, MissionEventType.MISSION_INVALID.value, "WARN", runtime.message)
            return runtime
        waypoints = self._waypoints(db, mission_id)
        if not waypoints:
            runtime = SimulationRuntime(mission_id, MissionSimulationState.ERROR, 0, "Mission simulation requires at least one draft waypoint.")
            self._runs[mission_id] = runtime
            self._record_event(db, mission, MissionEventType.MISSION_INVALID.value, "WARN", runtime.message)
            return runtime
        runtime = SimulationRuntime(mission_id, MissionSimulationState.RUNNING, 0, "Simulation running over draft waypoints only.")
        self._runs[mission_id] = runtime
        self._record_event(db, mission, MissionEventType.MISSION_SIM_STARTED.value, "INFO", "Mission simulation started; no hardware upload or MAVLink command was sent.")
        self._audit.record(db, operator_id="system", drone_id=mission.drone_id, event_type="MISSION_SIMULATION", decision="ALLOW", reason="Simulation-only mission runner started after MOCK source check.")
        return runtime

    def stop_simulation(self, db: Session, mission_id: str) -> SimulationRuntime | None:
        mission = db.query(MissionDraft).filter(MissionDraft.mission_id == mission_id).first()
        if not mission:
            return None
        runtime = self._runs.get(mission_id, SimulationRuntime(mission_id, MissionSimulationState.IDLE, 0, "Simulation idle."))
        runtime.state = MissionSimulationState.IDLE
        runtime.message = "Simulation stopped."
        self._runs[mission_id] = runtime
        self._record_event(db, mission, MissionEventType.MISSION_SIM_STOPPED.value, "INFO", "Mission simulation stopped; no hardware command was sent.")
        self._audit.record(db, operator_id="system", drone_id=mission.drone_id, event_type="MISSION_SIMULATION", decision="ALLOW", reason="Simulation-only mission runner stopped.")
        return runtime


    def pause_simulation(self, db: Session, mission_id: str) -> SimulationRuntime | None:
        mission = db.query(MissionDraft).filter(MissionDraft.mission_id == mission_id).first()
        if not mission:
            return None
        runtime = self._runs.get(mission_id, SimulationRuntime(mission_id, MissionSimulationState.IDLE, 0, "Simulation idle."))
        if runtime.state == MissionSimulationState.RUNNING:
            runtime.state = MissionSimulationState.PAUSED
            runtime.message = "Simulation paused."
            self._record_event(db, mission, "MISSION_SIM_PAUSED", "INFO", "Mission simulation paused; no hardware command was sent.")
            self._audit.record(db, operator_id="system", drone_id=mission.drone_id, event_type="MISSION_SIMULATION", decision="ALLOW", reason="Simulation-only mission runner paused.")
        else:
            runtime.message = f"Pause ignored because simulation is {runtime.state.value}."
        self._runs[mission_id] = runtime
        return runtime

    def resume_simulation(self, db: Session, mission_id: str) -> SimulationRuntime | None:
        mission = db.query(MissionDraft).filter(MissionDraft.mission_id == mission_id).first()
        if not mission:
            return None
        runtime = self._runs.get(mission_id, SimulationRuntime(mission_id, MissionSimulationState.IDLE, 0, "Simulation idle."))
        if runtime.state == MissionSimulationState.PAUSED:
            runtime.state = MissionSimulationState.RUNNING
            runtime.message = "Simulation resumed over draft waypoints only."
            self._record_event(db, mission, "MISSION_SIM_RESUMED", "INFO", "Mission simulation resumed; no hardware command was sent.")
            self._audit.record(db, operator_id="system", drone_id=mission.drone_id, event_type="MISSION_SIMULATION", decision="ALLOW", reason="Simulation-only mission runner resumed.")
        else:
            runtime.message = f"Resume ignored because simulation is {runtime.state.value}."
        self._runs[mission_id] = runtime
        return runtime

    def reset_simulation(self, db: Session, mission_id: str) -> SimulationRuntime | None:
        mission = db.query(MissionDraft).filter(MissionDraft.mission_id == mission_id).first()
        if not mission:
            return None
        runtime = SimulationRuntime(mission_id, MissionSimulationState.IDLE, 0, "Simulation reset to first draft waypoint.")
        self._runs[mission_id] = runtime
        self._record_event(db, mission, "MISSION_SIM_RESET", "INFO", "Mission simulation reset; no hardware command was sent.")
        self._audit.record(db, operator_id="system", drone_id=mission.drone_id, event_type="MISSION_SIMULATION", decision="ALLOW", reason="Simulation-only mission runner reset.")
        return runtime

    def get_simulation_status(self, db: Session, mission_id: str) -> SimulationRuntime | None:
        if not db.query(MissionDraft).filter(MissionDraft.mission_id == mission_id).first():
            return None
        return self._runs.get(mission_id, SimulationRuntime(mission_id, MissionSimulationState.IDLE, 0, "Simulation idle."))

    def step_simulation(self, db: Session) -> Telemetry | None:
        active = self._sources.get_active_source(db)
        if not active or active.source_type != TelemetrySource.MOCK.value:
            return None
        for mission_id, runtime in list(self._runs.items()):
            if runtime.state != MissionSimulationState.RUNNING:
                continue
            mission = db.query(MissionDraft).filter(MissionDraft.mission_id == mission_id).first()
            if not mission:
                runtime.state = MissionSimulationState.ERROR
                runtime.message = "Mission draft disappeared."
                continue
            waypoints = self._waypoints(db, mission_id)
            if runtime.active_waypoint_index >= len(waypoints):
                runtime.state = MissionSimulationState.COMPLETED
                runtime.message = "Mission simulation completed."
                self._record_event(db, mission, MissionEventType.MISSION_SIM_STOPPED.value, "INFO", "Mission simulation completed all draft waypoints.")
                return None
            target = waypoints[runtime.active_waypoint_index]
            latest = self._telemetry.latest(db, mission.drone_id)
            current_lat = latest.lat if latest else target.lat
            current_lon = latest.lon if latest else target.lon
            current_alt = latest.altitude_m if latest else target.altitude_m
            next_lat = self._approach(current_lat, target.lat, 0.00018)
            next_lon = self._approach(current_lon, target.lon, 0.00018)
            next_alt = self._approach(current_alt, target.altitude_m, 3.0)
            distance = self._distance_m(next_lat, next_lon, target.lat, target.lon)
            if distance < 8:
                self._record_event(db, mission, MissionEventType.WAYPOINT_REACHED.value, "INFO", f"Waypoint {target.sequence} reached in simulation.", details=f"sequence={target.sequence}")
                runtime.active_waypoint_index += 1
                if runtime.active_waypoint_index >= len(waypoints):
                    runtime.state = MissionSimulationState.COMPLETED
                    runtime.message = "Mission simulation completed."
            return self._telemetry.save(db, {
                "drone_id": mission.drone_id,
                "lat": round(next_lat, 7),
                "lon": round(next_lon, 7),
                "altitude_m": round(next_alt, 1),
                "speed_mps": target.speed_mps,
                "heading_deg": self._bearing(current_lat, current_lon, target.lat, target.lon),
                "battery_percent": max(20, (latest.battery_percent if latest else 82) - 1),
                "mode": "SIM_MISSION",
                "armed": False,
                "gps_status": "GOOD",
                "link_state": "FULL_LINK",
                "mission_state": "RUNNING" if runtime.state == MissionSimulationState.RUNNING else "COMPLETED",
                "warnings": ["MISSION_SIMULATION_ONLY", "NO_HARDWARE_UPLOAD"],
                "timestamp": datetime.now(timezone.utc),
            })
        return None

    def _waypoints(self, db: Session, mission_id: str) -> list[MapWaypoint]:
        return db.query(MapWaypoint).filter(MapWaypoint.mission_id == mission_id).order_by(MapWaypoint.sequence).all()

    def _record_event(self, db: Session, mission: MissionDraft, event_type: str, severity: str, message: str, details: str | None = None) -> None:
        db.add(MissionEvent(mission_id=mission.mission_id, drone_id=mission.drone_id, event_type=event_type, severity=severity, message=message, details=details))
        db.commit()

    def _approach(self, current: float, target: float, max_step: float) -> float:
        delta = target - current
        if abs(delta) <= max_step:
            return target
        return current + max_step * (1 if delta > 0 else -1)

    def _distance_m(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        earth_radius_m = 6_371_000
        phi1, phi2 = math.radians(lat1), math.radians(lat2)
        d_phi = math.radians(lat2 - lat1)
        d_lambda = math.radians(lon2 - lon1)
        a = math.sin(d_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2) ** 2
        return earth_radius_m * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    def _bearing(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        d_lon = math.radians(lon2 - lon1)
        y = math.sin(d_lon) * math.cos(math.radians(lat2))
        x = math.cos(math.radians(lat1)) * math.sin(math.radians(lat2)) - math.sin(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.cos(d_lon)
        return round((math.degrees(math.atan2(y, x)) + 360) % 360, 1)


mission_simulation_service = MissionSimulationService()
