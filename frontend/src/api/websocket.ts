import type { Telemetry } from '../types/telemetry';

const WS_BASE = import.meta.env.VITE_WS_BASE ?? 'ws://localhost:8000';

export function connectTelemetry(onMessage: (telemetry: Telemetry) => void): WebSocket {
  const ws = new WebSocket(`${WS_BASE}/ws/telemetry`);
  ws.onmessage = (event) => onMessage(JSON.parse(event.data));
  return ws;
}
