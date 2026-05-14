from pydantic import BaseModel


class BenchReadiness(BaseModel):
    stage: str
    bench_mode: bool
    propellers_required_removed: bool
    read_only: bool
    hardware_commands_enabled: bool
    serial_supported: str
    recommended_connection: str
    checklist: list[str]
    warnings: list[str]
