from pydantic import BaseModel, ConfigDict
from app.core.enums import VehicleType


class VehicleProfileBase(BaseModel):
    profile_id: str
    name: str
    vehicle_type: VehicleType
    capabilities: dict
    safety_limits: dict = {}


class VehicleProfileCreate(VehicleProfileBase):
    pass


class VehicleProfileRead(VehicleProfileBase):
    model_config = ConfigDict(from_attributes=True)
