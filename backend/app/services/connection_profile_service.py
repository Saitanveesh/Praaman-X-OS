from sqlalchemy.orm import Session

from app.models.connection_profile import ConnectionProfile
from app.schemas.connection_profile import ConnectionProfileCreate


class ConnectionProfileService:
    def ensure_defaults(self, db: Session) -> None:
        for seed in ConnectionProfile.seeds():
            if not db.query(ConnectionProfile).filter(ConnectionProfile.profile_id == seed.profile_id).first():
                db.add(seed)
        db.commit()

    def list_profiles(self, db: Session) -> list[ConnectionProfile]:
        self.ensure_defaults(db)
        return db.query(ConnectionProfile).order_by(ConnectionProfile.id).all()

    def get_profile(self, db: Session, profile_id: str) -> ConnectionProfile | None:
        self.ensure_defaults(db)
        return db.query(ConnectionProfile).filter(ConnectionProfile.profile_id == profile_id).first()

    def create_profile(self, db: Session, payload: ConnectionProfileCreate) -> ConnectionProfile:
        profile = ConnectionProfile(**payload.model_dump())
        db.add(profile)
        db.commit()
        db.refresh(profile)
        return profile
