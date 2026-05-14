from app.schemas.bench import BenchReadiness


class PixhawkBenchReadinessService:
    def readiness(self) -> BenchReadiness:
        return BenchReadiness(
            stage="STAGE_3_PIXHAWK_BENCH_READINESS",
            bench_mode=True,
            propellers_required_removed=True,
            read_only=True,
            hardware_commands_enabled=False,
            serial_supported="placeholder",
            recommended_connection="USB/Serial MAVLink read-only in future Stage 3.x",
            checklist=[
                "Remove propellers.",
                "Power Pixhawk safely on bench.",
                "Use Mission Planner for calibration and setup.",
                "Confirm vehicle is disarmed.",
                "Confirm Pramaan-X OS is in read-only mode.",
                "Confirm no hardware command execution is enabled.",
                "Connect telemetry stream only.",
                "Validate telemetry freshness.",
                "Do not test commands in Stage 3 readiness.",
            ],
            warnings=[
                "Bench mode is read-only. Remove propellers before any future hardware test.",
                "Pramaan-X OS does not send hardware commands in this stage.",
                "Stage 3 physical bench validation is manual and not performed automatically by this codebase.",
            ],
        )
