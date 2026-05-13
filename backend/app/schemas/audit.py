from datetime import datetime
from pydantic import BaseModel, ConfigDict
from app.core.enums import GovernanceDecision


class AuditRead(BaseModel):
    id: int
    timestamp: datetime
    operator_id: str
    drone_id: str
    event_type: str
    command_id: str | None = None
    decision: GovernanceDecision
    reason: str

    model_config = ConfigDict(from_attributes=True)
