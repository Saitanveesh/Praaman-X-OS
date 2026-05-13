from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.core.enums import C2ConnectionMode, MAVLinkBridgeStatus


class MAVLinkEndpointCreate(BaseModel):
    endpoint_id: str
    name: str
    host: str = "127.0.0.1"
    port: int = 14550
    protocol: str = "UDP"
    status: MAVLinkBridgeStatus = MAVLinkBridgeStatus.SIMULATION_ONLY
    read_only: bool = True


class MAVLinkEndpointRead(MAVLinkEndpointCreate):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class BridgeStatusRead(BaseModel):
    status: MAVLinkBridgeStatus
    read_only: bool
    endpoint_count: int
    message: str
    hardware_commands_enabled: bool = False


class C2ConnectionConfigRead(BaseModel):
    id: int | None = None
    mode: C2ConnectionMode
    description: str
    mission_planner_allowed: bool
    pramaan_commands_allowed: bool
    hardware_commands_enabled: bool
    puf_required: bool
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class C2ConnectionModeUpdate(BaseModel):
    mode: C2ConnectionMode
