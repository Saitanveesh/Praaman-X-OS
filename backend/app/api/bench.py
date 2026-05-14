from fastapi import APIRouter

from app.schemas.bench import BenchReadiness
from app.services.pixhawk_bench_readiness_service import PixhawkBenchReadinessService

router = APIRouter(prefix="/api/bench", tags=["bench"])
service = PixhawkBenchReadinessService()


@router.get("/readiness", response_model=BenchReadiness)
def bench_readiness():
    return service.readiness()
