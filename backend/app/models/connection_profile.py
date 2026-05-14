from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.enums import ConnectionProfileType
from app.db.session import Base


class ConnectionProfile(Base):
    __tablename__ = "connection_profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    profile_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(128))
    profile_type: Mapped[str] = mapped_column(String(64), index=True)
    host: Mapped[str | None] = mapped_column(String(128), nullable=True)
    port: Mapped[int | None] = mapped_column(Integer, nullable=True)
    serial_port: Mapped[str | None] = mapped_column(String(128), nullable=True)
    baud_rate: Mapped[int | None] = mapped_column(Integer, nullable=True)
    protocol: Mapped[str] = mapped_column(String(32), default="UDP")
    read_only: Mapped[bool] = mapped_column(Boolean, default=True)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    notes: Mapped[str | None] = mapped_column(String(512), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    @classmethod
    def seeds(cls) -> list["ConnectionProfile"]:
        return [
            cls(profile_id="sitl-udp-14550", name="SITL UDP 14550", profile_type=ConnectionProfileType.SITL_UDP.value, host="127.0.0.1", port=14550, protocol="UDP", read_only=True, enabled=True, notes="Stage 2 supported ArduPilot SITL UDP read-only telemetry."),
            cls(profile_id="mavproxy-udp-14550", name="MAVProxy UDP 14550", profile_type=ConnectionProfileType.MAVPROXY_UDP.value, host="127.0.0.1", port=14550, protocol="UDP", read_only=True, enabled=True, notes="Use MAVProxy or MAVLink Router output to this local UDP listener."),
            cls(profile_id="pixhawk-serial-placeholder", name="Pixhawk Serial Placeholder", profile_type=ConnectionProfileType.PIXHAWK_SERIAL_PLACEHOLDER.value, host=None, port=None, serial_port="/dev/ttyACM0", baud_rate=115200, protocol="SERIAL", read_only=True, enabled=False, notes="Stage 3 bench read-only placeholder; no hardware commands enabled."),
            cls(profile_id="playback-placeholder", name="Playback Placeholder", profile_type=ConnectionProfileType.PLAYBACK.value, host=None, port=None, protocol="FILE", read_only=True, enabled=False, notes="Future telemetry playback profile placeholder."),
        ]
