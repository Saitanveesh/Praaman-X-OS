# AGENTS.md

## Project Identity

This repository contains **Pramaan-X Intelligent C2 OS** for **Shauryan Aerospace**.

Stage 1 is a simulation-only intelligent command-and-control / ground-control platform for Shauryan Aerospace drone systems.

This repository is not yet the secure PUF-based version.

## Roadmap

### Stage 1: Pramaan-X Intelligent C2 OS

Current stage.

Purpose:
- General C2/GCS platform for Shauryan Aerospace drones
- Simulation-first development
- Mock telemetry
- Safe command governance
- Vehicle profiles
- Audit logging
- Plugin-ready architecture

### Stage 2: Pramaan-X PUFShield Trust Gate

Future parallel hardware security layer.

Purpose:
- Hardware-rooted drone identity
- Command verification
- Anti-replay logic
- Session validation
- Secure command gate between companion computer and flight controller

### Stage 3: Pramaan-X Secure Intelligent C2 OS

Future secure version.

Created by integrating:

Pramaan-X Intelligent C2 OS  
+  
Pramaan-X PUFShield Trust Gate

## Core Rules

1. This project is **Pramaan-X Intelligent C2 OS** for **Shauryan Aerospace**.
2. Stage 1 is **simulation-only**.
3. Do not implement real `ARM`, `TAKEOFF`, `DISARM`, payload, or hardware MAVLink execution unless explicitly requested later.
4. Keep UI minimal, black/silver, and classic aerospace style.
5. Maintain plugin interfaces for:
   - `TelemetryProvider`
   - `CommandTransport`
   - `SecurityProvider`
   - `VehicleAdapter`
   - `AIObservationPlugin`
   - `MapProvider`
6. PUFShield is future integration only. Do not make Stage 1 dependent on PUF hardware.
7. Every command must pass governance before acceptance.
8. Every command decision must be written to audit logs.
9. Prefer small working increments over large rewrites.
10. Flag missing tests, unsafe command behavior, broken imports, and README inaccuracies as high-priority issues.

## Safety Restrictions

Do not add real drone hardware control in Stage 1.

Do not add:
- real ARM execution
- real TAKEOFF execution
- real DISARM execution
- real payload execution
- real MAVLink hardware command execution

Allowed in Stage 1:
- mock telemetry
- simulated commands
- simulated RTL
- simulated LAND
- command governance
- audit logs
- vehicle profile handling
- UI dashboard
- plugin stubs

## UI Direction

The UI must remain simple and serious.

Use:
- black / near-black background
- white, gray, and silver text
- thin borders
- compact panels
- minimal blue accents only when needed
- classic aerospace / defense console feel

Avoid:
- neon cyberpunk UI
- flashy animations
- fake 3D cockpit clutter
- overdesigned sci-fi dashboards
- colorful gradients

## Plugin Policy

Keep the system plugin-ready.

Current plugins are placeholders for future integration:

- MAVLink adapter
- PUFShield security provider
- AI observation module
- Map provider
- Telemetry provider
- Command transport

Do not remove or bypass these interfaces.

## Development Rule

Build in small steps.

Preferred order:
1. Keep backend running.
2. Keep frontend building.
3. Keep mock telemetry working.
4. Keep command governance active.
5. Keep audit logs working.
6. Add real integrations only after simulation is stable.

## Final Warning

This is drone command-and-control software.

Treat unsafe commands, broken governance, and unclear execution paths as serious issues.
