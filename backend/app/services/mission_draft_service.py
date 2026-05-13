import math
from uuid import uuid4

from sqlalchemy.orm import Session

from app.core.enums import MissionDraftStatus, MissionEventType, VehicleType, WaypointAction
from app.models.drone import Drone
from app.models.mission import MapWaypoint, MissionDraft, MissionEvent
from app.models.vehicle_profile import VehicleProfile
from app.schemas.mission import MapWaypointCreate, MissionDraftCreate, MissionRouteSummary, MissionValidationRead


class MissionDraftService:
    def list_missions(self, db: Session) -> list[MissionDraft]:
        return db.query(MissionDraft).order_by(MissionDraft.created_at.desc()).all()

    def create_mission(self, db: Session, payload: MissionDraftCreate) -> MissionDraft:
        mission = MissionDraft(
            mission_id=payload.mission_id or f"mission-{uuid4().hex[:10]}",
            name=payload.name,
            drone_id=payload.drone_id,
            vehicle_type=payload.vehicle_type.value,
            status=MissionDraftStatus.DRAFT.value,
            default_altitude_m=payload.default_altitude_m,
            default_speed_mps=payload.default_speed_mps,
            lost_link_action=payload.lost_link_action,
        )
        db.add(mission)
        db.commit()
        db.refresh(mission)
        return mission

    def get_mission(self, db: Session, mission_id: str) -> MissionDraft | None:
        return db.query(MissionDraft).filter(MissionDraft.mission_id == mission_id).first()

    def add_waypoint(self, db: Session, mission_id: str, payload: MapWaypointCreate) -> MapWaypoint | None:
        mission = self.get_mission(db, mission_id)
        if not mission:
            return None
        next_sequence = payload.sequence
        if next_sequence is None:
            max_sequence = max((wp.sequence for wp in self.list_waypoints(db, mission_id)), default=0)
            next_sequence = max_sequence + 1
        waypoint = MapWaypoint(
            mission_id=mission_id,
            sequence=next_sequence,
            lat=payload.lat,
            lon=payload.lon,
            altitude_m=payload.altitude_m if payload.altitude_m is not None else mission.default_altitude_m,
            speed_mps=payload.speed_mps if payload.speed_mps is not None else mission.default_speed_mps,
            action=payload.action.value,
            loiter_seconds=payload.loiter_seconds,
            notes=payload.notes,
        )
        db.add(waypoint)
        db.commit()
        db.refresh(waypoint)
        return waypoint

    def list_waypoints(self, db: Session, mission_id: str) -> list[MapWaypoint]:
        return db.query(MapWaypoint).filter(MapWaypoint.mission_id == mission_id).order_by(MapWaypoint.sequence).all()

    def summarize_route(self, db: Session, mission_id: str) -> MissionRouteSummary | None:
        if not self.get_mission(db, mission_id):
            return None
        return self._build_summary(self.list_waypoints(db, mission_id))

    def validate_mission(self, db: Session, mission_id: str) -> MissionValidationRead | None:
        mission = self.get_mission(db, mission_id)
        if not mission:
            return None
        errors: list[str] = []
        warnings: list[str] = []
        if not mission.drone_id:
            errors.append("Mission draft requires a drone_id.")
        drone = db.get(Drone, mission.drone_id) if mission.drone_id else None
        if not drone:
            errors.append("Mission draft drone_id must match a registered vehicle.")
        profile = db.get(VehicleProfile, getattr(drone, "profile_id", None)) if drone and drone.profile_id else None
        if not profile:
            warnings.append("Vehicle profile validation is limited because no profile is assigned.")
        if mission.vehicle_type not in {VehicleType.QUADCOPTER.value, VehicleType.FIXED_WING.value}:
            errors.append("Mission draft vehicle_type must be supported.")
        if mission.default_altitude_m <= 0:
            errors.append("Default altitude must be positive.")
        if mission.default_speed_mps <= 0:
            errors.append("Default speed must be positive.")

        waypoints = self.list_waypoints(db, mission_id)
        if not waypoints:
            warnings.append("No waypoints added; route preview is empty.")
        previous_sequence = 0
        for waypoint in waypoints:
            if waypoint.sequence <= previous_sequence:
                errors.append(f"Waypoint {waypoint.sequence} sequence is not strictly ordered.")
            previous_sequence = waypoint.sequence
            if waypoint.altitude_m <= 0:
                errors.append(f"Waypoint {waypoint.sequence} altitude must be positive.")
            if waypoint.speed_mps <= 0:
                errors.append(f"Waypoint {waypoint.sequence} speed must be positive.")
            if not -90 <= waypoint.lat <= 90:
                errors.append(f"Waypoint {waypoint.sequence} latitude is outside valid range.")
            if not -180 <= waypoint.lon <= 180:
                errors.append(f"Waypoint {waypoint.sequence} longitude is outside valid range.")
        if mission.vehicle_type == VehicleType.FIXED_WING.value and not any(wp.action in {WaypointAction.LOITER.value, WaypointAction.RETURN_POINT.value} for wp in waypoints):
            warnings.append("Fixed-wing mission drafts should include LOITER or RETURN_POINT behavior for resilience.")
        warnings.append("Geofence is missing or draft-only; Stage 1.2 provides no hardware enforcement.")
        warnings.append("Mission is draft/simulation-only and cannot be uploaded to flight hardware.")

        mission.status = MissionDraftStatus.INVALID.value if errors else MissionDraftStatus.VALIDATED.value
        db.add(MissionEvent(
            mission_id=mission_id,
            drone_id=mission.drone_id,
            event_type=MissionEventType.MISSION_INVALID.value if errors else MissionEventType.MISSION_VALIDATED.value,
            severity="WARN" if errors else "INFO",
            message="Mission draft validation failed." if errors else "Mission draft validation passed for simulation-only use.",
            details="|".join(errors or warnings),
        ))
        db.commit()
        return MissionValidationRead(
            mission_id=mission_id,
            status=mission.status,
            valid=not errors,
            errors=errors,
            warnings=warnings,
            summary=self._build_summary(waypoints),
        )

    def _build_summary(self, waypoints: list[MapWaypoint]) -> MissionRouteSummary:
        altitudes = [waypoint.altitude_m for waypoint in waypoints]
        return MissionRouteSummary(
            waypoint_count=len(waypoints),
            estimated_distance_m=round(self._route_distance_m(waypoints), 2),
            max_altitude_m=max(altitudes) if altitudes else 0.0,
            min_altitude_m=min(altitudes) if altitudes else 0.0,
        )

    def _route_distance_m(self, waypoints: list[MapWaypoint]) -> float:
        return sum(
            self._haversine_m(start.lat, start.lon, end.lat, end.lon)
            for start, end in zip(waypoints, waypoints[1:])
        )

    def _haversine_m(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        earth_radius_m = 6_371_000
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        delta_phi = math.radians(lat2 - lat1)
        delta_lambda = math.radians(lon2 - lon1)
        a = math.sin(delta_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
        return earth_radius_m * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
