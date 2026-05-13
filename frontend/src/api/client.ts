import type { AuditLog } from '../types/audit';
import type { Command, CommandType } from '../types/command';
import type { Drone } from '../types/drone';
import type { Telemetry } from '../types/telemetry';
import type { VehicleProfile } from '../types/profile';

const API_BASE = import.meta.env.VITE_API_BASE ?? 'http://localhost:8000';

async function getJson<T>(path: string): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`);
  if (!response.ok) throw new Error(`GET ${path} failed`);
  return response.json();
}

export const api = {
  drones: () => getJson<Drone[]>('/api/drones'),
  profiles: () => getJson<VehicleProfile[]>('/api/profiles'),
  latestTelemetry: (droneId: string) => getJson<Telemetry>(`/api/telemetry/latest/${droneId}`),
  audit: () => getJson<AuditLog[]>('/api/audit'),
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
