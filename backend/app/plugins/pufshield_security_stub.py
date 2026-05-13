from app.plugins.security_provider import SoftwareSecurityProvider


class PUFShieldSecurityStub(SoftwareSecurityProvider):
    def verify_drone_identity(self, drone_id: str) -> dict:
        status = super().verify_drone_identity(drone_id)
        status.update({"pufshield_connected": False, "stage": "placeholder_for_stage_2"})
        return status
