import type { AuditLog } from '../types/audit';
import type { Command, CommandType } from '../types/command';
import type { Drone } from '../types/drone';
import type { Telemetry } from '../types/telemetry';
import type { VehicleProfile } from '../types/profile';
import type { BridgeStatus, C2ConnectionConfig, GeofenceDraft, MapWaypoint, MapWaypointCreate, MAVLinkEndpoint, MissionDraft, MissionDraftCreate, MissionRouteSummary, MissionValidation } from '../types/mission';

const API_BASE = import.meta.env.VITE_API_BASE ?? 'http://localhost:8000';

async function getJson<T>(path: string): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`);
  if (!response.ok) throw new Error(`GET ${path} failed`);
  return response.json();
}

async function postJson<T>(path: string, body: unknown): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  if (!response.ok) throw new Error(`POST ${path} failed`);
  return response.json();
}

export const api = {
  drones: () => getJson<Drone[]>('/api/drones'),
  profiles: () => getJson<VehicleProfile[]>('/api/profiles'),
  latestTelemetry: (droneId: string) => getJson<Telemetry>(`/api/telemetry/latest/${droneId}`),
  audit: () => getJson<AuditLog[]>('/api/audit'),
  bridgeStatus: () => getJson<BridgeStatus>('/api/bridge/status'),
  bridgeEndpoints: () => getJson<MAVLinkEndpoint[]>('/api/bridge/endpoints'),
  connectionMode: () => getJson<C2ConnectionConfig>('/api/connection-mode'),
  setConnectionMode: (mode: C2ConnectionConfig['mode']) => postJson<C2ConnectionConfig>('/api/connection-mode', { mode }),
  missions: () => getJson<MissionDraft[]>('/api/missions'),
  createMission: (mission: MissionDraftCreate) => postJson<MissionDraft>('/api/missions', mission),
  waypoints: (missionId: string) => getJson<MapWaypoint[]>(`/api/missions/${missionId}/waypoints`),
  addWaypoint: (missionId: string, waypoint: MapWaypointCreate) => postJson<MapWaypoint>(`/api/missions/${missionId}/waypoints`, waypoint),
  validateMission: (missionId: string) => postJson<MissionValidation>(`/api/missions/${missionId}/validate`, {}),
  missionSummary: (missionId: string) => getJson<MissionRouteSummary>(`/api/missions/${missionId}/summary`),
  createGeofence: (geofence: Omit<GeofenceDraft, 'id' | 'geofence_id' | 'created_at' | 'updated_at'> & { geofence_id?: string }) => postJson<GeofenceDraft>('/api/geofences', geofence),
  geofences: () => getJson<GeofenceDraft[]>('/api/geofences'),
  sendCommand: async (drone_id: string, command_type: CommandType, operator_id = 'operator-demo') => {
    const response = await fetch(`${API_BASE}/api/commands`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ drone_id, command_type, operator_id }),
    });
    if (!response.ok) throw new Error('Command submission failed');
    return response.json() as Promise<Command>;
  },
};
