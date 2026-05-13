from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.enums import TelemetrySource, TelemetrySourceStatus
from app.db.session import Base


class TelemetrySourceConfig(Base):
    __tablename__ = "telemetry_source_configs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    source_type: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    status: Mapped[str] = mapped_column(String(32), default=TelemetrySourceStatus.INACTIVE.value)
    name: Mapped[str] = mapped_column(String(128))
    host: Mapped[str | None] = mapped_column(String(128), nullable=True)
    port: Mapped[int | None] = mapped_column(Integer, nullable=True)
    protocol: Mapped[str] = mapped_column(String(32), default="INTERNAL")
    read_only: Mapped[bool] = mapped_column(Boolean, default=True)
    last_error: Mapped[str | None] = mapped_column(String(512), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    @classmethod
    def mock_default(cls) -> "TelemetrySourceConfig":
        return cls(
            source_type=TelemetrySource.MOCK.value,
            status=TelemetrySourceStatus.ACTIVE.value,
            name="Mock Telemetry Generator",
            host=None,
            port=None,
            protocol="INTERNAL",
            read_only=True,
        )

    @classmethod
    def sitl_placeholder(cls) -> "TelemetrySourceConfig":
        return cls(
            source_type=TelemetrySource.MAVLINK_READ_ONLY.value,
            status=TelemetrySourceStatus.INACTIVE.value,
            name="ArduPilot SITL UDP Read-Only",
            host="127.0.0.1",
            port=14550,
            protocol="UDP",
            read_only=True,
        )

    @classmethod
    def playback_placeholder(cls) -> "TelemetrySourceConfig":
        return cls(
            source_type=TelemetrySource.PLAYBACK.value,
            status=TelemetrySourceStatus.INACTIVE.value,
            name="Telemetry Playback Placeholder",
            host=None,
            port=None,
            protocol="FILE",
            read_only=True,
        )
