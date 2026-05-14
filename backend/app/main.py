import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import audit, bridge, commands, connection_mode, drones, geofences, intelligence, mavlink_readonly, missions, profiles, sitl, system, telemetry, telemetry_sources, websocket
from app.core.config import settings
from app.db.init_db import init_db
from app.db.session import SessionLocal
from app.mock.telemetry_generator import MockTelemetryGenerator
from app.services.telemetry_service import TelemetryService, telemetry_to_schema
from app.services.telemetry_source_service import TelemetrySourceService
from app.services.mission_simulation_service import mission_simulation_service
from app.core.enums import MissionEventType, TelemetrySource
from app.models.mission import MissionEvent
from app.services.mavlink_readonly_runtime import mavlink_readonly_provider


async def telemetry_loop(app: FastAPI) -> None:
    generator = MockTelemetryGenerator()
    service = TelemetryService()
    source_service = TelemetrySourceService()
    mavlink_seen = False
    while True:
        with SessionLocal() as db:
            active = source_service.get_active_source(db)
            active_type = active.source_type if active else TelemetrySource.MOCK.value
            row = None
            if active_type == TelemetrySource.MOCK.value:
                mavlink_seen = False
                row = mission_simulation_service.step_simulation(db)
                if row is None:
                    row = service.save(db, generator.next())
            elif active_type == TelemetrySource.MAVLINK_READ_ONLY.value:
                payload_data = mavlink_readonly_provider.poll_once()
                if payload_data is not None:
                    row = service.save(db, payload_data)
                    if not mavlink_seen:
                        db.add(MissionEvent(
                            mission_id="SYSTEM",
                            drone_id=payload_data["drone_id"],
                            event_type=MissionEventType.MAVLINK_TELEMETRY_RECEIVED.value,
                            severity="INFO",
                            message="First MAVLink read-only telemetry received after source activation.",
                            details=f"endpoint={mavlink_readonly_provider.get_status().get('endpoint')}",
                        ))
                        db.commit()
                        mavlink_seen = True
                elif mavlink_readonly_provider.get_status().get("last_error"):
                    source_service.set_source_error(db, TelemetrySource.MAVLINK_READ_ONLY, str(mavlink_readonly_provider.get_status().get("last_error")))
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
app.include_router(sitl.router)
app.include_router(intelligence.router)
app.include_router(system.router)
app.include_router(websocket.router)


@app.get("/api/health")
def health():
    return {"status": "ok", "app": settings.app_name}
