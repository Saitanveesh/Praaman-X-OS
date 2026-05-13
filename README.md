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

## Stage 1.2: Real Map + Mission Draft Improvement

Stage 1.2 improves the `MAP / MISSION` page into a usable simulation mission planning screen while preserving the Stage 1 safety boundary.

This stage remains simulation-only:

- The map is an operational planning preview only and uses mock/latest telemetry for the live `PX-QD-001` marker.
- Mission drafts are planning records and are not uploaded to drone hardware.
- Waypoints are planning objects only; route lines and waypoint markers do not command a flight controller.
- Geofences are draft visualizations only. Stage 1.2 performs no hardware geofence enforcement.
- Mission Planner remains the calibration/setup tool for firmware, frame setup, sensors, radio, ESC/motor testing, parameters, and tuning.
- Future stages will connect SITL MAVLink read-only telemetry while preserving command governance and no-hardware-command defaults.

Stage 1.2 adds:

- Leaflet/react-leaflet map preview with live drone marker, home marker, waypoint markers, route polyline, and geofence polygon preview.
- Expanded mission draft creation fields for drone ID, vehicle type, default altitude, default speed, and lost-link action.
- Expanded waypoint drafts with altitude, speed, action, loiter seconds, notes, and a compact waypoint table.
- Structured mission validation with warnings, errors, and route summary data.
- Approximate route distance calculation with the Haversine formula.
- Route summary and validation warning panels in the frontend.

Stage 1.2 backend mission validation returns:

```json
{
  "mission_id": "string",
  "status": "VALIDATED or INVALID",
  "warnings": [],
  "errors": [],
  "summary": {
    "waypoint_count": 0,
    "estimated_distance_m": 0,
    "max_altitude_m": 0,
    "min_altitude_m": 0
  }
}
```

Additional Stage 1.2 endpoint:

- `GET /api/missions/{mission_id}/summary`

## Stage 1.3: SITL-Ready Read-Only MAVLink + Telemetry Source Manager + Mission Simulation

Stage 1.3 prepares Pramaan-X Intelligent C2 OS for future ArduPilot SITL/MAVLink telemetry ingestion while keeping the default app safe, read-only, and simulation-only.

Safety boundary remains unchanged:

- Default telemetry source is `MOCK` and remains active on startup.
- The MAVLink provider is read-only and intended for future SITL/ArduPilot telemetry reading only.
- No MAVLink command sending is enabled.
- No `ARM`, `TAKEOFF`, `DISARM`, payload, mission upload, or real flight-controller command execution exists in Stage 1.3.
- Mission drafts and mission simulations do not upload anything to hardware.
- Mission simulation only moves mock telemetry for `PX-QD-001` along draft waypoints.

Stage 1.3 adds:

- Telemetry Source Manager with `MOCK`, `MAVLINK_READ_ONLY`, and `PLAYBACK` source records.
- Seeded SITL placeholder: `ArduPilot SITL UDP Read-Only` at `127.0.0.1:14550` using `UDP` and `read_only: true`.
- Graceful read-only MAVLink provider stub that reports missing `pymavlink` or connection failures without crashing the backend.
- Recent telemetry history endpoint for map flight-track visualization.
- Map/Mission flight track polyline from telemetry history.
- Simulation-only mission runner for draft waypoints.
- Mission event timeline for validation, source switching, MAVLink read-only errors, and simulation events.
- Dashboard and Mission Planner Bridge telemetry source panels.

New Stage 1.3 backend endpoints:

- `GET /api/telemetry-sources`
- `GET /api/telemetry-sources/active`
- `POST /api/telemetry-sources/active`
- `GET /api/telemetry/history/{drone_id}?limit=200`
- `GET /api/mavlink-readonly/status`
- `POST /api/mavlink-readonly/connect`
- `POST /api/mavlink-readonly/disconnect`
- `GET /api/missions/{mission_id}/events`
- `POST /api/missions/{mission_id}/simulate/start`
- `POST /api/missions/{mission_id}/simulate/stop`
- `GET /api/missions/{mission_id}/simulate/status`

### Future SITL / Mission Planner telemetry-sharing plan

Mission Planner remains the calibration/setup tool. Pramaan-X OS remains the operational intelligence/C2 layer for supervision, governance, audit logs, mission simulation, and future secure integrations.

A later SITL workflow can forward one telemetry stream to multiple consumers using MAVProxy or MAVLink Router so Mission Planner and Pramaan-X OS can observe the same vehicle state. Stage 1.3 only prepares the Pramaan-X read-only listener path.

Documentation-only command examples for future operator setup:

```bash
mavproxy --master=COMx --out=127.0.0.1:14550
```

```bash
mavproxy.py --out=127.0.0.1:14550
```

These examples are helper text only. They are not executed by Pramaan-X OS, and they do not enable command authority in this application.
