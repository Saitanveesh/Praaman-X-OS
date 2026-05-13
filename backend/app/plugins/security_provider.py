from abc import ABC, abstractmethod


class SecurityProvider(ABC):
    @abstractmethod
    def verify_drone_identity(self, drone_id: str) -> dict: ...

    @abstractmethod
    def authorize_command(self, command, drone_state: str) -> bool: ...

    @abstractmethod
    def sign_command(self, command) -> str: ...

    @abstractmethod
    def verify_command(self, command) -> bool: ...


class SoftwareSecurityProvider(SecurityProvider):
    def verify_drone_identity(self, drone_id: str) -> dict:
        return {"drone_id": drone_id, "software_verified": True, "hardware_verified": False, "pufshield_connected": False}

    def authorize_command(self, command, drone_state: str) -> bool:
        return drone_state not in {"ERROR", "UNSEEN"}

    def sign_command(self, command) -> str:
        return f"software-signature:{command.command_id}"

    def verify_command(self, command) -> bool:
        return True
