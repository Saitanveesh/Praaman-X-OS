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

## Stage 1.4–1.6: SITL Readiness, Mission Planner Coexistence, Telemetry Intelligence, Mission Replay, and Demo Hardening

Stage 1.4–1.6 turns the working Stage 1 prototype into a stronger demo build while preserving the core safety boundary: Pramaan-X Intelligent C2 OS remains simulation-only, read-only for MAVLink preparation, and disconnected from real drone command execution.

Mission Planner remains the setup/calibration tool for firmware flashing, frame setup, accelerometer calibration, compass calibration, radio calibration, ESC/motor testing, parameter tuning, and initial failsafe setup.

Pramaan-X OS remains the intelligent operational C2 and supervision layer for telemetry intelligence, mission supervision, command governance, audit logging, vehicle profile management, mission draft planning, simulation replay, and future secure C2 integration.

Safety notes for this stage:

- Stage 1 remains simulation-only.
- No real MAVLink command sending exists.
- No real mission upload exists.
- No real `ARM`, `TAKEOFF`, `DISARM`, payload, or hardware command execution exists.
- SITL readiness is documentation/checklist only and never launches SITL.
- Telemetry intelligence provides operator-level warnings and recommended actions only; it never triggers commands.
- Mission replay is mock/simulation-only.
- Mission import/export is draft-only using `PRAMAAN_X_MISSION_DRAFT_V1` JSON.
- Mission reports explicitly return `simulation_only: true` and `hardware_upload_enabled: false`.

Stage 1.4–1.6 adds:

- `SITL READINESS` frontend page with readiness status, expected UDP endpoint, Mission Planner coexistence model, and future SITL flow documentation.
- System Status API and dashboard panel showing Stage 1 simulation status, disabled hardware commands, disabled MAVLink command sending, inactive PUFShield integration, active telemetry source, and backend health.
- Telemetry Intelligence API and dashboard panel for battery risk, telemetry freshness, warnings, summaries, and operator recommendations.
- Link Intelligence API and dashboard panel for link state, link risk, operator message, and recommended action.
- PUF Status dashboard panel that clearly marks PUFShield as not integrated and secure command mode as disabled in Stage 1.
- Mission replay controls: start, pause, resume, stop, reset, current mission, latest event, and simulation-only warning.
- Mission event timeline filtering by event type, severity, or message text.
- Mission draft JSON export/import and mission report generation.
- Improved route summary with waypoint count, estimated distance, estimated duration, min/max altitude, lost-link action, and validation status.

New Stage 1.4–1.6 backend endpoints:

- `GET /api/sitl/readiness`
- `GET /api/system/status`
- `GET /api/intelligence/telemetry/{drone_id}`
- `GET /api/intelligence/link/{drone_id}`
- `GET /api/intelligence/summary/{drone_id}`
- `POST /api/missions/{mission_id}/simulate/pause`
- `POST /api/missions/{mission_id}/simulate/resume`
- `POST /api/missions/{mission_id}/simulate/reset`
- `GET /api/missions/{mission_id}/export`
- `POST /api/missions/import`
- `GET /api/missions/{mission_id}/report`

### Demo Guide

1. Run backend.
2. Run frontend.
3. Open Dashboard.
4. Check Telemetry Intelligence.
5. Open Mission Planner Bridge.
6. Open SITL Readiness.
7. Open Map / Mission.
8. Create mission draft.
9. Add waypoints.
10. Validate mission.
11. Start simulation.
12. View event timeline.
13. Export mission/report.

### Stage 1.4–1.6 verification commands

```bash
cd backend
python -m py_compile $(find app tests -name '*.py')
pytest
```

```bash
cd frontend
npm run build
```
