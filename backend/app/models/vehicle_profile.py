from sqlalchemy import JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class VehicleProfile(Base):
    __tablename__ = "vehicle_profiles"

    profile_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(128))
    vehicle_type: Mapped[str] = mapped_column(String(32))
    capabilities: Mapped[dict] = mapped_column(JSON, default=dict)
    safety_limits: Mapped[dict] = mapped_column(JSON, default=dict)
