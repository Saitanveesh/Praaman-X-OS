from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.enums import C2ConnectionMode, MAVLinkBridgeStatus
from app.db.session import Base


class MAVLinkEndpoint(Base):
    __tablename__ = "mavlink_endpoints"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    endpoint_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(128))
    host: Mapped[str] = mapped_column(String(128))
    port: Mapped[int] = mapped_column(Integer)
    protocol: Mapped[str] = mapped_column(String(16), default="UDP")
    status: Mapped[str] = mapped_column(String(32), default=MAVLinkBridgeStatus.SIMULATION_ONLY.value)
    read_only: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))


class C2ConnectionConfig(Base):
    __tablename__ = "c2_connection_configs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    mode: Mapped[str] = mapped_column(String(48), unique=True, index=True, default=C2ConnectionMode.SETUP_MODE.value)
    description: Mapped[str] = mapped_column(String(512))
    mission_planner_allowed: Mapped[bool] = mapped_column(Boolean, default=True)
    pramaan_commands_allowed: Mapped[bool] = mapped_column(Boolean, default=False)
    hardware_commands_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    puf_required: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
