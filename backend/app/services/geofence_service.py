import json
from uuid import uuid4

from sqlalchemy.orm import Session

from app.models.mission import GeofenceDraft
from app.schemas.mission import GeofenceDraftCreate, GeofenceValidationRead


class GeofenceService:
    def list_geofences(self, db: Session) -> list[GeofenceDraft]:
        return db.query(GeofenceDraft).order_by(GeofenceDraft.created_at.desc()).all()

    def create_geofence(self, db: Session, payload: GeofenceDraftCreate) -> GeofenceDraft:
        geofence = GeofenceDraft(
            geofence_id=payload.geofence_id or f"geofence-{uuid4().hex[:10]}",
            name=payload.name,
            drone_id=payload.drone_id,
            enabled=payload.enabled,
            polygon_json=payload.polygon_json,
            max_altitude_m=payload.max_altitude_m,
            min_altitude_m=payload.min_altitude_m,
        )
        db.add(geofence)
        db.commit()
        db.refresh(geofence)
        return geofence

    def validate_geofence(self, geofence: GeofenceDraft) -> GeofenceValidationRead:
        errors: list[str] = []
        warnings: list[str] = []
        try:
            polygon = json.loads(geofence.polygon_json)
        except json.JSONDecodeError:
            polygon = None
            errors.append("Geofence polygon_json must be valid JSON.")
        if isinstance(polygon, list) and polygon and len(polygon) < 3:
            errors.append("Enabled geofence polygons should have at least three points.")
        if geofence.max_altitude_m <= geofence.min_altitude_m:
            errors.append("Geofence max_altitude_m must be greater than min_altitude_m.")
        if not geofence.enabled:
            warnings.append("Geofence draft is disabled and will only be displayed as a placeholder.")
        return GeofenceValidationRead(geofence_id=geofence.geofence_id, valid=not errors, errors=errors, warnings=warnings)
