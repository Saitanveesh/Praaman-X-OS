from datetime import datetime
from pydantic import BaseModel, ConfigDict
from app.core.enums import CommandStatus, CommandType, GovernanceDecision


class CommandCreate(BaseModel):
    drone_id: str
    command_type: CommandType
    operator_id: str = "operator-demo"


class CommandRead(BaseModel):
    command_id: str
    drone_id: str
    operator_id: str
    command_type: CommandType
    status: CommandStatus
    decision: GovernanceDecision
    reason: str
    ack_message: str | None = None
    created_at: datetime
    acknowledged_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)
