from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.core.enums import ConnectionProfileType


class ConnectionProfileCreate(BaseModel):
    profile_id: str
    name: str
    profile_type: ConnectionProfileType
    host: str | None = None
    port: int | None = None
    serial_port: str | None = None
    baud_rate: int | None = None
    protocol: str = "UDP"
    read_only: bool = True
    enabled: bool = True
    notes: str | None = None


class ConnectionProfileRead(ConnectionProfileCreate):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
