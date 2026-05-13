from app.core.enums import CommandType, GovernanceDecision
from app.db.init_db import init_db
from app.db.session import SessionLocal
from app.mock.telemetry_generator import MockTelemetryGenerator
from app.schemas.command import CommandCreate
from app.services.governance_service import GovernanceService
from app.services.telemetry_service import TelemetryService


def test_governance_allows_safe_stage1_command():
    init_db()
    with SessionLocal() as db:
        TelemetryService().save(db, MockTelemetryGenerator().next())
        command = CommandCreate(drone_id="PX-QD-001", command_type=CommandType.READ_STATUS)
        decision, reason = GovernanceService().evaluate(db, command)
    assert decision == GovernanceDecision.ALLOW
    assert "accepted" in reason
