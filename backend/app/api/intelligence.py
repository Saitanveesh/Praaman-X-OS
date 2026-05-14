from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.intelligence import IntelligenceSummary, LinkIntelligence, TelemetryIntelligence
from app.services.link_intelligence_service import LinkIntelligenceService
from app.services.telemetry_intelligence_service import TelemetryIntelligenceService

router = APIRouter(prefix="/api/intelligence", tags=["intelligence"])
telemetry_service = TelemetryIntelligenceService()
link_service = LinkIntelligenceService()


@router.get("/telemetry/{drone_id}", response_model=TelemetryIntelligence)
def telemetry_intelligence(drone_id: str, db: Session = Depends(get_db)):
    return telemetry_service.evaluate(db, drone_id)


@router.get("/link/{drone_id}", response_model=LinkIntelligence)
def link_intelligence(drone_id: str, db: Session = Depends(get_db)):
    return link_service.evaluate(db, drone_id)


@router.get("/summary/{drone_id}", response_model=IntelligenceSummary)
def intelligence_summary(drone_id: str, db: Session = Depends(get_db)):
    telemetry = telemetry_service.evaluate(db, drone_id)
    link = link_service.evaluate(db, drone_id)
    return IntelligenceSummary(
        drone_id=drone_id,
        telemetry=telemetry,
        link=link,
        warnings=[*telemetry.warnings, link.operator_message] if link.risk_level != "LOW" else telemetry.warnings,
    )
