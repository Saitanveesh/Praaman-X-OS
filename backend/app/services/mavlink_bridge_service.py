from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.core.enums import MAVLinkBridgeStatus
from app.models.bridge import MAVLinkEndpoint
from app.schemas.bridge import BridgeStatusRead, MAVLinkEndpointCreate


class MAVLinkBridgeService:
    """Simulation-only MAVLink Bridge placeholder.

    This service intentionally does not open sockets or send MAVLink commands.
    Stage 1.1 exposes read-only compatibility state for Mission Planner workflows.
    """

    def get_bridge_status(self, db: Session) -> BridgeStatusRead:
        endpoints = self.get_endpoints(db)
        read_only = all(endpoint.read_only for endpoint in endpoints) if endpoints else True
        status = endpoints[0].status if endpoints else MAVLinkBridgeStatus.NOT_CONFIGURED.value
        return BridgeStatusRead(
            status=status,
            read_only=read_only,
            endpoint_count=len(endpoints),
            message="Simulation-only MAVLink Bridge stub. No real hardware command execution is enabled.",
            hardware_commands_enabled=False,
        )

    def get_endpoints(self, db: Session) -> list[MAVLinkEndpoint]:
        return db.query(MAVLinkEndpoint).order_by(MAVLinkEndpoint.endpoint_id).all()

    def create_endpoint(self, db: Session, payload: MAVLinkEndpointCreate) -> MAVLinkEndpoint:
        endpoint = MAVLinkEndpoint(**payload.model_dump(mode="json"))
        endpoint.read_only = True
        if endpoint.status not in {MAVLinkBridgeStatus.SIMULATION_ONLY.value, MAVLinkBridgeStatus.READ_ONLY_READY.value, MAVLinkBridgeStatus.CONNECTED_READ_ONLY.value}:
            endpoint.status = MAVLinkBridgeStatus.SIMULATION_ONLY.value
        db.add(endpoint)
        db.commit()
        db.refresh(endpoint)
        return endpoint

    def set_read_only_mode(self, db: Session, endpoint_id: str, read_only: bool = True) -> MAVLinkEndpoint | None:
        endpoint = db.query(MAVLinkEndpoint).filter(MAVLinkEndpoint.endpoint_id == endpoint_id).first()
        if not endpoint:
            return None
        endpoint.read_only = True if not read_only else read_only
        endpoint.updated_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(endpoint)
        return endpoint
