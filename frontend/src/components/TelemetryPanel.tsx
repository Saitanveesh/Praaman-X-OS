import type { Drone } from '../types/drone';
import type { Telemetry } from '../types/telemetry';
import StatusCard from './StatusCard';

export default function TelemetryPanel({ drone, telemetry }: { drone?: Drone; telemetry?: Telemetry }) {
  return <div className="grid gap-3 md:grid-cols-3 xl:grid-cols-4">
    <StatusCard label="Drone ID" value={drone?.drone_id ?? telemetry?.drone_id} />
    <StatusCard label="Vehicle Type" value={drone?.vehicle_type} />
    <StatusCard label="Armed State" value={telemetry?.armed ? 'ARMED' : 'DISARMED'} />
    <StatusCard label="Flight Mode" value={telemetry?.mode} />
    <StatusCard label="GPS Position" value={telemetry ? `${telemetry.lat.toFixed(5)}, ${telemetry.lon.toFixed(5)}` : '—'} />
    <StatusCard label="Altitude" value={telemetry ? `${telemetry.altitude_m} m` : '—'} />
    <StatusCard label="Speed" value={telemetry ? `${telemetry.speed_mps} m/s` : '—'} />
    <StatusCard label="Battery" value={telemetry ? (telemetry.battery_percent == null ? 'UNKNOWN' : `${telemetry.battery_percent}%`) : '—'} />
    <StatusCard label="Link State" value={telemetry?.link_state} />
    <StatusCard label="Mission State" value={telemetry?.mission_state} />
    <StatusCard label="GPS Status" value={telemetry?.gps_status} />
    <StatusCard label="Last Update" value={telemetry ? new Date(telemetry.timestamp).toLocaleTimeString() : '—'} />
  </div>;
}
