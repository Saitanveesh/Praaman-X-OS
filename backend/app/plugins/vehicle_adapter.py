from abc import ABC, abstractmethod


class VehicleAdapter(ABC):
    @abstractmethod
    def validate_command(self, command, telemetry) -> tuple[bool, str]: ...

    @abstractmethod
    def validate_mission(self, mission) -> tuple[bool, str]: ...

    @abstractmethod
    def get_lost_link_action(self, link_state: str, telemetry) -> str: ...

    @abstractmethod
    def get_safety_limits(self) -> dict: ...


class ProfileVehicleAdapter(VehicleAdapter):
    def __init__(self, profile):
        self.profile = profile

    def validate_command(self, command, telemetry) -> tuple[bool, str]:
        if command.command_type == "SIMULATE_LAND" and self.profile.vehicle_type == "FIXED_WING":
            return False, "Fixed-wing profile requires predefined landing corridor; direct simulated land is not allowed."
        return True, "Vehicle profile accepts command."

    def validate_mission(self, mission) -> tuple[bool, str]:
        return True, "Mission validation placeholder accepted."

    def get_lost_link_action(self, link_state: str, telemetry) -> str:
        return self.profile.capabilities.get("default_lost_link_action", "HOLD_THEN_RTL")

    def get_safety_limits(self) -> dict:
        return self.profile.safety_limits or {}
