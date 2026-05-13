# Pramaan-X Intelligent C2 OS

Stage 1 prototype for Shauryan Aerospace's Pramaan-X Intelligent C2 OS. This build is a general intelligent command-and-control / ground-control prototype for future drones. It uses mock telemetry and a mock command transport only; it does not send commands to real flight hardware.

## What is included

- FastAPI backend with SQLite development storage and SQLAlchemy models.
- React + TypeScript + Vite frontend with a restrained black/silver aerospace console style.
- Live mock telemetry over WebSocket for `PX-QD-001`.
- Drone registry, vehicle profiles, command panel, command acknowledgements, and audit log.
- Stage 1 command governance for safe simulated commands only.
- Plugin interfaces for telemetry providers, command transports, software/PUFShield security, vehicle adapters, AI observation, maps, and MAVLink integration.

## Safety scope

This prototype intentionally excludes real hardware control. The safe commands are:

- `READ_STATUS`
- `START_LOGGING`
- `STOP_LOGGING`
- `SIMULATE_RTL`
- `SIMULATE_LAND`

## Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Backend API: <http://localhost:8000>

Important endpoints:

- `GET /api/drones`
- `GET /api/drones/{drone_id}`
- `POST /api/drones`
- `GET /api/profiles`
- `POST /api/profiles`
- `GET /api/telemetry/latest/{drone_id}`
- `POST /api/commands`
- `GET /api/commands/{command_id}`
- `GET /api/audit`
- `WS /ws/telemetry`

## Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend: <http://localhost:5173>

Optional environment overrides:

```bash
VITE_API_BASE=http://localhost:8000
VITE_WS_BASE=ws://localhost:8000
```

## Tests

```bash
cd backend
pytest
```

```bash
cd frontend
npm run build
```

## Development notes

- SQLite is the default via `PRAAMANX_DATABASE_URL=sqlite:///./praamanx_dev.db`; use a PostgreSQL SQLAlchemy URL later without changing the service layer.
- `backend/app/plugins/pufshield_security_stub.py` is a Stage 2 placeholder and currently reports `pufshield_connected: false`.
- `backend/app/plugins/mavlink_adapter_stub.py` is a future integration placeholder and is not connected to real vehicles.
- Mock telemetry starts automatically with the FastAPI lifespan and emits one sample every second.

## Stage 1.1: Mission Planner Compatibility + Map/Mission Foundation

Stage 1.1 adds compatibility structure for using Mission Planner as the engineering setup/calibration tool while Pramaan-X Intelligent C2 OS remains the operational C2 and intelligence layer.

Mission Planner remains responsible for firmware flashing, frame setup, accelerometer/compass/radio calibration, ESC and motor testing, parameter setup, and basic tuning. Pramaan-X OS is responsible for mission supervision, telemetry intelligence, vehicle profiles, command governance, audit logging, later cloud/tactical C2, and future PUFShield integration.

This stage is still simulation-only:

- The Mission Planner Bridge and MAVLink Bridge are placeholders for read-only telemetry compatibility.
- No real MAVLink command execution is enabled.
- Hardware command execution remains disabled in every C2 connection mode.
- Mission drafts, waypoint drafts, and geofence drafts are draft/simulation-only records.
- Map/Mission UI is a foundation panel with a drone marker placeholder based on latest telemetry latitude/longitude.
- Future integration can use a MAVLink router or MAVProxy so Mission Planner and Pramaan-X OS can receive the same telemetry stream while command governance and authority separation remain explicit.

New Stage 1.1 backend endpoints:

- `GET /api/bridge/status`
- `GET /api/bridge/endpoints`
- `POST /api/bridge/endpoints`
- `GET /api/connection-mode`
- `POST /api/connection-mode`
- `GET /api/missions`
- `POST /api/missions`
- `GET /api/missions/{mission_id}`
- `POST /api/missions/{mission_id}/waypoints`
- `GET /api/missions/{mission_id}/waypoints`
- `POST /api/missions/{mission_id}/validate`
- `GET /api/geofences`
- `POST /api/geofences`

New Stage 1.1 frontend pages:

- `MISSION PLANNER BRIDGE` for setup/operations authority separation, read-only MAVLink Bridge status, and future secure mode placeholders.
- `MAP / MISSION` for map foundation, current simulated position, mission draft creation, waypoint draft creation, mission validation, and geofence placeholders.
