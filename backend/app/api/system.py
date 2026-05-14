from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.enums import TelemetrySource
from app.db.session import get_db
from app.services.telemetry_source_service import TelemetrySourceService

router = APIRouter(prefix="/api/system", tags=["system"])


class SystemStatus(BaseModel):
    app_name: str
    company: str
    app_stage: str
    simulation_only: bool
    hardware_commands_enabled: bool
    mavlink_command_sending_enabled: bool
    pufshield_integrated: bool
    active_telemetry_source: str
    backend_status: str
    warning_count: int


@router.get("/status", response_model=SystemStatus)
def system_status(db: Session = Depends(get_db)):
    active = TelemetrySourceService().get_active_source(db)
    return SystemStatus(
        app_name="Pramaan-X Intelligent C2 OS",
        company="Shauryan Aerospace",
        app_stage="STAGE_1_SIMULATION",
        simulation_only=True,
        hardware_commands_enabled=False,
        mavlink_command_sending_enabled=False,
        pufshield_integrated=False,
        active_telemetry_source=active.source_type if active else TelemetrySource.MOCK.value,
        backend_status="OK",
        warning_count=0,
    )
