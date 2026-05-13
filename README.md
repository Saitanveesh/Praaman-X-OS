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
