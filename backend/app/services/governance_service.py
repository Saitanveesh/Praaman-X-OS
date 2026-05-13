from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.enums import CommandType, GovernanceDecision, LinkState
from app.models.drone import Drone
from app.models.vehicle_profile import VehicleProfile
from app.plugins.security_provider import SoftwareSecurityProvider
from app.plugins.vehicle_adapter import ProfileVehicleAdapter
from app.services.drone_state_machine import DroneStateMachine
from app.services.telemetry_service import TelemetryService


class GovernanceService:
    allowed_stage1 = {item.value for item in CommandType}
    allowed_operators = {"operator-demo", "system"}
    lost_link_recovery_simulations = {CommandType.SIMULATE_RTL.value, CommandType.READ_STATUS.value}

    def __init__(self):
        self.telemetry_service = TelemetryService()
        self.security_provider = SoftwareSecurityProvider()
        self.drone_state_machine = DroneStateMachine()

    def evaluate(self, db: Session, command) -> tuple[GovernanceDecision, str]:
        drone = db.get(Drone, command.drone_id)
        if not drone:
            return GovernanceDecision.REJECT, "Drone is not registered."
        if command.operator_id not in self.allowed_operators:
            return GovernanceDecision.REJECT, "Operator is not authorized for Stage 1 prototype."
        if command.command_type not in self.allowed_stage1:
            return GovernanceDecision.REJECT, "Command type is not allowed in Stage 1."

        telemetry = self.telemetry_service.latest(db, command.drone_id)
        if not telemetry:
            return GovernanceDecision.REJECT, "No telemetry available for command governance."
        now = datetime.now(timezone.utc)
        age = (now - telemetry.timestamp.replace(tzinfo=timezone.utc)).total_seconds()
        if age > settings.telemetry_fresh_seconds:
            return GovernanceDecision.REJECT, "Telemetry is stale."
        if telemetry.link_state == LinkState.LOST_LINK and command.command_type not in self.lost_link_recovery_simulations:
            return GovernanceDecision.REJECT, "Link is lost; only safe recovery simulations are accepted."

        profile = db.get(VehicleProfile, drone.profile_id) if drone.profile_id else None
        if not profile:
            return GovernanceDecision.REJECT, "Drone has no vehicle profile assigned."
        profile_allowed, profile_reason = ProfileVehicleAdapter(profile).validate_command(command, telemetry)
        if not profile_allowed:
            return GovernanceDecision.REJECT, profile_reason

        drone_state = self.drone_state_machine.from_telemetry(telemetry)
        if not self.security_provider.authorize_command(command, drone_state.value):
            return GovernanceDecision.REJECT, "Software security provider rejected command."
        return GovernanceDecision.ALLOW, "Command accepted by Stage 1 command governance."
