from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.core.enums import C2ConnectionMode
from app.models.bridge import C2ConnectionConfig


MODE_POLICIES = {
    C2ConnectionMode.SETUP_MODE: {
        "description": "Mission Planner has setup authority; Pramaan-X remains read-only for telemetry supervision.",
        "mission_planner_allowed": True,
        "pramaan_commands_allowed": False,
        "hardware_commands_enabled": False,
        "puf_required": False,
    },
    C2ConnectionMode.OPS_MONITOR_MODE: {
        "description": "Pramaan-X monitors telemetry and governance context while Mission Planner remains available.",
        "mission_planner_allowed": True,
        "pramaan_commands_allowed": False,
        "hardware_commands_enabled": False,
        "puf_required": False,
    },
    C2ConnectionMode.PRAMAAN_CONTROL_MODE: {
        "description": "Future operational Pramaan-X authority mode; Stage 1.1 remains simulation-only.",
        "mission_planner_allowed": False,
        "pramaan_commands_allowed": True,
        "hardware_commands_enabled": False,
        "puf_required": False,
    },
    C2ConnectionMode.FUTURE_SECURE_CONTROL_MODE: {
        "description": "Placeholder for later PUFShield integration; not active in Stage 1.1.",
        "mission_planner_allowed": False,
        "pramaan_commands_allowed": False,
        "hardware_commands_enabled": False,
        "puf_required": True,
    },
}


class ConnectionModeService:
    def get_mode_policy(self, mode: C2ConnectionMode) -> dict:
        return MODE_POLICIES[mode]

    def get_current_mode(self, db: Session) -> C2ConnectionConfig:
        config = db.query(C2ConnectionConfig).order_by(C2ConnectionConfig.id).first()
        if config:
            return config
        return self.set_mode(db, C2ConnectionMode.SETUP_MODE)

    def set_mode(self, db: Session, mode: C2ConnectionMode) -> C2ConnectionConfig:
        policy = self.get_mode_policy(mode)
        config = db.query(C2ConnectionConfig).order_by(C2ConnectionConfig.id).first()
        if not config:
            config = C2ConnectionConfig(mode=mode.value, **policy)
            db.add(config)
        else:
            config.mode = mode.value
            for key, value in policy.items():
                setattr(config, key, value)
            config.updated_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(config)
        return config
