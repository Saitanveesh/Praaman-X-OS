from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.core.enums import TelemetrySource, TelemetrySourceStatus


class TelemetrySourceConfigRead(BaseModel):
    id: int
    source_type: TelemetrySource
    status: TelemetrySourceStatus
    name: str
    host: str | None = None
    port: int | None = None
    protocol: str
    read_only: bool
    last_error: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TelemetrySourceSetActive(BaseModel):
    source_type: TelemetrySource
