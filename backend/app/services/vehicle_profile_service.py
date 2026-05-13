from sqlalchemy.orm import Session
from app.models.vehicle_profile import VehicleProfile
from app.schemas.vehicle_profile import VehicleProfileCreate


class VehicleProfileService:
    def list_profiles(self, db: Session) -> list[VehicleProfile]:
        return db.query(VehicleProfile).order_by(VehicleProfile.profile_id).all()

    def create_profile(self, db: Session, profile: VehicleProfileCreate) -> VehicleProfile:
        obj = VehicleProfile(**profile.model_dump(mode="json"))
        db.merge(obj)
        db.commit()
        return db.get(VehicleProfile, profile.profile_id)
