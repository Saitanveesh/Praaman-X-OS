from pydantic import BaseModel


class SITLReadiness(BaseModel):
    status: str
    read_only: bool
    command_sending_enabled: bool
    expected_host: str
    expected_port: int
    telemetry_source: str
    mavlink_provider_status: str
    mission_planner_role: str
    pramaanx_role: str
    checklist: list[str]
    warnings: list[str]
    recommended_next_step: str
