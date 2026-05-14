from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.core.enums import MissionDraftStatus, VehicleType, WaypointAction


class MissionDraftCreate(BaseModel):
    mission_id: str | None = None
    name: str
    drone_id: str
    vehicle_type: VehicleType
    default_altitude_m: float = 40.0
    default_speed_mps: float = 6.0
    lost_link_action: str = "HOLD_THEN_RTL"


class MissionDraftRead(BaseModel):
    id: int
    mission_id: str
    name: str
    drone_id: str
    vehicle_type: VehicleType
    status: MissionDraftStatus
    default_altitude_m: float
    default_speed_mps: float
    lost_link_action: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MapWaypointCreate(BaseModel):
    sequence: int | None = None
    lat: float
    lon: float
    altitude_m: float | None = None
    speed_mps: float | None = None
    action: WaypointAction = WaypointAction.NAVIGATE
    loiter_seconds: int | None = None
    notes: str | None = None


class MapWaypointRead(BaseModel):
    id: int
    mission_id: str
    sequence: int
    lat: float
    lon: float
    altitude_m: float
    speed_mps: float
    action: WaypointAction
    loiter_seconds: int | None = None
    notes: str | None = None

    model_config = ConfigDict(from_attributes=True)


class MissionRouteSummary(BaseModel):
    waypoint_count: int = 0
    estimated_distance_m: float = 0.0
    max_altitude_m: float = 0.0
    min_altitude_m: float = 0.0


class MissionValidationRead(BaseModel):
    mission_id: str
    status: MissionDraftStatus
    valid: bool
    warnings: list[str]
    errors: list[str]
    summary: MissionRouteSummary


class GeofenceDraftCreate(BaseModel):
    geofence_id: str | None = None
    name: str
    drone_id: str
    enabled: bool = True
    polygon_json: str = "[]"
    max_altitude_m: float = 120.0
    min_altitude_m: float = 0.0


class GeofenceDraftRead(BaseModel):
    id: int
    geofence_id: str
    name: str
    drone_id: str
    enabled: bool
    polygon_json: str
    max_altitude_m: float
    min_altitude_m: float
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class GeofenceValidationRead(BaseModel):
    geofence_id: str
    valid: bool
    errors: list[str]
    warnings: list[str]


class MissionEventRead(BaseModel):
    id: int
    mission_id: str
    drone_id: str
    event_type: str
    severity: str
    message: str
    timestamp: datetime
    details: str | None = None

    model_config = ConfigDict(from_attributes=True)


class MissionSimulationStatusRead(BaseModel):
    mission_id: str
    state: str
    active_waypoint_index: int = 0
    waypoint_count: int = 0
    message: str = ""

class MissionExportRead(BaseModel):
    format: str
    mission: MissionDraftRead
    waypoints: list[MapWaypointRead]
    validation: MissionValidationRead
    exported_at: datetime
    hardware_upload_enabled: bool = False


class MissionImportPayload(BaseModel):
    format: str
    mission: dict
    waypoints: list[dict] = []


class MissionReportRead(BaseModel):
    mission_id: str
    name: str
    drone_id: str
    vehicle_type: str
    status: str
    waypoint_count: int
    estimated_distance_m: float
    estimated_duration_s: float
    max_altitude_m: float
    min_altitude_m: float
    lost_link_action: str
    validation_errors: list[str]
    validation_warnings: list[str]
    simulation_only: bool = True
    hardware_upload_enabled: bool = False
