from datetime import datetime

from pydantic import BaseModel


class TelemetryIntelligence(BaseModel):
    drone_id: str
    battery_level: int
    battery_risk: str
    altitude_status: str
    speed_status: str
    gps_status: str
    telemetry_freshness: str
    recommended_action: str
    warnings: list[str]
    summary: str
    timestamp: datetime


class LinkIntelligence(BaseModel):
    drone_id: str
    link_state: str
    link_quality: str
    operator_message: str
    risk_level: str
    recommended_action: str
    timestamp: datetime


class IntelligenceSummary(BaseModel):
    drone_id: str
    telemetry: TelemetryIntelligence
    link: LinkIntelligence
    warnings: list[str]
    simulation_only: bool = True
    hardware_commands_enabled: bool = False
