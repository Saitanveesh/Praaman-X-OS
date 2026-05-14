import type { AuditLog } from '../types/audit';
import type { Command, CommandType } from '../types/command';
import type { Drone } from '../types/drone';
import type { Telemetry } from '../types/telemetry';
import type { VehicleProfile } from '../types/profile';
import type { BridgeStatus, C2ConnectionConfig, GeofenceDraft, IntelligenceSummary, MapWaypoint, MapWaypointCreate, MAVLinkEndpoint, MissionDraft, MissionDraftCreate, MissionEvent, MissionExport, MissionImportPayload, MissionReport, MissionRouteSummary, MissionSimulationStatus, MissionValidation, SITLReadiness, SystemStatus, TelemetrySource, TelemetrySourceConfig } from '../types/mission';

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
  telemetryHistory: (droneId: string, limit = 200) => getJson<Telemetry[]>(`/api/telemetry/history/${droneId}?limit=${limit}`),
  audit: () => getJson<AuditLog[]>('/api/audit'),
  bridgeStatus: () => getJson<BridgeStatus>('/api/bridge/status'),
  telemetrySources: () => getJson<TelemetrySourceConfig[]>('/api/telemetry-sources'),
  activeTelemetrySource: () => getJson<TelemetrySourceConfig>('/api/telemetry-sources/active'),
  setTelemetrySource: (source_type: TelemetrySource) => postJson<TelemetrySourceConfig>('/api/telemetry-sources/active', { source_type }),
  mavlinkReadonlyStatus: () => getJson<Record<string, unknown>>('/api/mavlink-readonly/status'),
  mavlinkReadonlyConnect: () => postJson<Record<string, unknown>>('/api/mavlink-readonly/connect', {}),
  mavlinkReadonlyDisconnect: () => postJson<Record<string, unknown>>('/api/mavlink-readonly/disconnect', {}),
  sitlReadiness: () => getJson<SITLReadiness>('/api/sitl/readiness'),
  systemStatus: () => getJson<SystemStatus>('/api/system/status'),
  telemetryIntelligence: (droneId: string) => getJson<IntelligenceSummary>(`/api/intelligence/summary/${droneId}`),
  bridgeEndpoints: () => getJson<MAVLinkEndpoint[]>('/api/bridge/endpoints'),
  connectionMode: () => getJson<C2ConnectionConfig>('/api/connection-mode'),
  setConnectionMode: (mode: C2ConnectionConfig['mode']) => postJson<C2ConnectionConfig>('/api/connection-mode', { mode }),
  missions: () => getJson<MissionDraft[]>('/api/missions'),
  createMission: (mission: MissionDraftCreate) => postJson<MissionDraft>('/api/missions', mission),
  waypoints: (missionId: string) => getJson<MapWaypoint[]>(`/api/missions/${missionId}/waypoints`),
  addWaypoint: (missionId: string, waypoint: MapWaypointCreate) => postJson<MapWaypoint>(`/api/missions/${missionId}/waypoints`, waypoint),
  validateMission: (missionId: string) => postJson<MissionValidation>(`/api/missions/${missionId}/validate`, {}),
  missionSummary: (missionId: string) => getJson<MissionRouteSummary>(`/api/missions/${missionId}/summary`),
  missionEvents: (missionId: string) => getJson<MissionEvent[]>(`/api/missions/${missionId}/events`),
  startMissionSimulation: (missionId: string) => postJson<MissionSimulationStatus>(`/api/missions/${missionId}/simulate/start`, {}),
  stopMissionSimulation: (missionId: string) => postJson<MissionSimulationStatus>(`/api/missions/${missionId}/simulate/stop`, {}),
  pauseMissionSimulation: (missionId: string) => postJson<MissionSimulationStatus>(`/api/missions/${missionId}/simulate/pause`, {}),
  resumeMissionSimulation: (missionId: string) => postJson<MissionSimulationStatus>(`/api/missions/${missionId}/simulate/resume`, {}),
  resetMissionSimulation: (missionId: string) => postJson<MissionSimulationStatus>(`/api/missions/${missionId}/simulate/reset`, {}),
  exportMission: (missionId: string) => getJson<MissionExport>(`/api/missions/${missionId}/export`),
  importMission: (payload: MissionImportPayload) => postJson<MissionDraft>('/api/missions/import', payload),
  missionReport: (missionId: string) => getJson<MissionReport>(`/api/missions/${missionId}/report`),
  missionSimulationStatus: (missionId: string) => getJson<MissionSimulationStatus>(`/api/missions/${missionId}/simulate/status`),
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
