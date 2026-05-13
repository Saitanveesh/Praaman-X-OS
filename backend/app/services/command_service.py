from datetime import datetime, timezone
from uuid import uuid4
from sqlalchemy.orm import Session

from app.core.enums import CommandStatus, GovernanceDecision
from app.models.command import Command
from app.plugins.command_transport import MockCommandTransport
from app.schemas.command import CommandCreate
from app.services.audit_service import AuditService
from app.services.governance_service import GovernanceService


class CommandService:
    def __init__(self):
        self.governance = GovernanceService()
        self.audit = AuditService()
        self.transport = MockCommandTransport()

    async def submit(self, db: Session, request: CommandCreate) -> Command:
        command = Command(
            command_id=f"cmd-{uuid4().hex[:12]}",
            drone_id=request.drone_id,
            operator_id=request.operator_id,
            command_type=request.command_type.value,
            status=CommandStatus.QUEUED.value,
            decision=GovernanceDecision.REJECT.value,
            reason="Pending governance.",
            created_at=datetime.now(timezone.utc),
        )
        decision, reason = self.governance.evaluate(db, command)
        command.decision = decision.value
        command.reason = reason
        if decision == GovernanceDecision.ALLOW:
            await self.transport.send_command(command)
            ack = await self.transport.await_ack(command.command_id)
            command.status = CommandStatus.ACKNOWLEDGED.value
            command.ack_message = ack.get("message", "Command acknowledged by mock transport.")
            command.acknowledged_at = datetime.now(timezone.utc)
        else:
            command.status = CommandStatus.REJECTED.value
        db.add(command)
        db.commit()
        db.refresh(command)
        self.audit.record(
            db,
            operator_id=command.operator_id,
            drone_id=command.drone_id,
            event_type="COMMAND_SUBMITTED",
            command_id=command.command_id,
            decision=command.decision,
            reason=command.reason,
        )
        return command

    def get(self, db: Session, command_id: str) -> Command | None:
        return db.get(Command, command_id)
