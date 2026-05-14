from datetime import datetime
from sqlalchemy import Boolean, DateTime, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class Telemetry(Base):
    __tablename__ = "telemetry"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    drone_id: Mapped[str] = mapped_column(String(64), index=True)
    lat: Mapped[float] = mapped_column(Float)
    lon: Mapped[float] = mapped_column(Float)
    altitude_m: Mapped[float] = mapped_column(Float)
    speed_mps: Mapped[float] = mapped_column(Float)
    heading_deg: Mapped[float] = mapped_column(Float)
    battery_percent: Mapped[int | None] = mapped_column(Integer, nullable=True)
    mode: Mapped[str] = mapped_column(String(32))
    armed: Mapped[bool] = mapped_column(Boolean, default=False)
    gps_status: Mapped[str] = mapped_column(String(32))
    link_state: Mapped[str] = mapped_column(String(32))
    mission_state: Mapped[str] = mapped_column(String(32))
    warnings: Mapped[str] = mapped_column(String(512), default="")
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
