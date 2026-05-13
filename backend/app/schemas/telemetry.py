from datetime import datetime
from pydantic import BaseModel, ConfigDict
from app.core.enums import LinkState, MissionState


class TelemetryRead(BaseModel):
    drone_id: str
    lat: float
    lon: float
    altitude_m: float
    speed_mps: float
    heading_deg: float
    battery_percent: int
    mode: str
    armed: bool
    gps_status: str
    link_state: LinkState
    mission_state: MissionState
    warnings: list[str] = []
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)
