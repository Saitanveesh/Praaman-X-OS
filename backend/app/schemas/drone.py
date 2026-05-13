from pydantic import BaseModel, ConfigDict
from app.core.enums import VehicleType


class DroneBase(BaseModel):
    drone_id: str
    name: str
    vehicle_type: VehicleType
    flight_stack: str = "ARDUPILOT"
    firmware_version: str = "SIM-0.1"
    status: str = "CONNECTED"
    profile_id: str | None = None
    future_puf_status: str = "NOT_INTEGRATED"


class DroneCreate(DroneBase):
    pass


class DroneRead(DroneBase):
    model_config = ConfigDict(from_attributes=True)
