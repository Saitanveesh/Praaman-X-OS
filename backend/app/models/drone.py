from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class Drone(Base):
    __tablename__ = "drones"

    drone_id: Mapped[str] = mapped_column(String(64), primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(128))
    vehicle_type: Mapped[str] = mapped_column(String(32))
    flight_stack: Mapped[str] = mapped_column(String(64), default="ARDUPILOT")
    firmware_version: Mapped[str] = mapped_column(String(64), default="SIM-0.1")
    status: Mapped[str] = mapped_column(String(32), default="CONNECTED")
    profile_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    future_puf_status: Mapped[str] = mapped_column(String(64), default="NOT_INTEGRATED")
