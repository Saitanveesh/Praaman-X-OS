import { useEffect, useState } from 'react';
import { api } from '../api/client';
import type { TelemetrySource, TelemetrySourceConfig } from '../types/mission';

export default function TelemetrySourcePanel({ compact = false }: { compact?: boolean }) {
  const [sources, setSources] = useState<TelemetrySourceConfig[]>([]);
  const [active, setActive] = useState<TelemetrySourceConfig>();
  const [warning, setWarning] = useState('');

  async function refresh() {
    const [items, current] = await Promise.all([api.telemetrySources(), api.activeTelemetrySource()]);
    setSources(items);
    setActive(current);
  }

  useEffect(() => { refresh().catch((error) => setWarning(String(error))); }, []);

  async function choose(source: TelemetrySource) {
    setWarning('');
    try {
      const selected = await api.setTelemetrySource(source);
      setActive(selected);
      setSources(await api.telemetrySources());
      if (source === 'MAVLINK_READ_ONLY') {
        const status = await api.mavlinkReadonlyConnect();
        if (status.ok === false) setWarning(String(status.last_error ?? 'MAVLink read-only provider is not connected.'));
      }
    } catch (error) {
      setWarning(String(error));
    }
  }

  const mavlink = sources.find((item) => item.source_type === 'MAVLINK_READ_ONLY');

  return <section className="rounded border border-zinc-800 bg-zinc-950 p-4 text-sm text-zinc-300">
    <div className="flex flex-wrap items-start justify-between gap-3">
      <div>
        <p className="text-xs uppercase tracking-[0.25em] text-zinc-500">Telemetry Source Manager</p>
        <h3 className="mt-1 text-base font-semibold text-white">Active source: {active?.source_type ?? 'LOADING'}</h3>
        <p className="mt-1 text-zinc-400">Status: <span className="text-zinc-100">{active?.status ?? 'UNKNOWN'}</span> / Read-only: <span className="text-zinc-100">{active?.read_only ? 'ENFORCED' : 'NOT ALLOWED'}</span></p>
        {!compact && <p className="mt-1 text-zinc-500">MAVLink placeholder: {mavlink?.host ?? '127.0.0.1'}:{mavlink?.port ?? 14550} {mavlink?.protocol ?? 'UDP'}</p>}
        {(warning || active?.last_error) && <p className="mt-2 rounded border border-amber-900/70 bg-amber-950/20 p-2 text-amber-100">{warning || active?.last_error}</p>}
      </div>
      <div className="flex flex-wrap gap-2">
        <button onClick={() => choose('MOCK')} className="rounded border border-zinc-600 px-3 py-2 text-xs uppercase text-white">Use Mock Telemetry</button>
        <button onClick={() => choose('MAVLINK_READ_ONLY')} className="rounded border border-zinc-600 px-3 py-2 text-xs uppercase text-white">Use MAVLink Read-Only</button>
        <button onClick={() => choose('PLAYBACK')} className="rounded border border-zinc-600 px-3 py-2 text-xs uppercase text-white">Use Playback</button>
      </div>
    </div>
  </section>;
}
