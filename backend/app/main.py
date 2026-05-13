import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import audit, bridge, commands, connection_mode, drones, geofences, mavlink_readonly, missions, profiles, telemetry, telemetry_sources, websocket
from app.core.config import settings
from app.db.init_db import init_db
from app.db.session import SessionLocal
from app.mock.telemetry_generator import MockTelemetryGenerator
from app.services.telemetry_service import TelemetryService, telemetry_to_schema
from app.services.telemetry_source_service import TelemetrySourceService
from app.services.mission_simulation_service import mission_simulation_service
from app.core.enums import TelemetrySource


async def telemetry_loop(app: FastAPI) -> None:
    generator = MockTelemetryGenerator()
    service = TelemetryService()
    while True:
        with SessionLocal() as db:
            active = TelemetrySourceService().get_active_source(db)
            row = mission_simulation_service.step_simulation(db)
            if row is None and (active is None or active.source_type == TelemetrySource.MOCK.value):
                row = service.save(db, generator.next())
            if row is None:
                await asyncio.sleep(1)
                continue
            payload = telemetry_to_schema(row).model_dump(mode="json")
        await websocket.manager.broadcast(payload)
        await asyncio.sleep(1)


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    task = asyncio.create_task(telemetry_loop(app))
    yield
    task.cancel()


app = FastAPI(title=settings.app_name, lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(drones.router)
app.include_router(profiles.router)
app.include_router(telemetry.router)
app.include_router(commands.router)
app.include_router(audit.router)
app.include_router(geofences.router)
app.include_router(missions.router)
app.include_router(connection_mode.router)
app.include_router(bridge.router)
app.include_router(telemetry_sources.router)
app.include_router(mavlink_readonly.router)
app.include_router(websocket.router)


@app.get("/api/health")
def health():
    return {"status": "ok", "app": settings.app_name}
