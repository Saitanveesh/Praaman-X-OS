import { useEffect, useState } from 'react';
import { api } from '../api/client';
import TelemetrySourcePanel from '../components/TelemetrySourcePanel';
import type { BridgeStatus, C2ConnectionConfig, C2ConnectionMode, MAVLinkEndpoint } from '../types/mission';

const modes: C2ConnectionMode[] = ['SETUP_MODE', 'OPS_MONITOR_MODE', 'PRAMAAN_CONTROL_MODE', 'FUTURE_SECURE_CONTROL_MODE'];

export default function Bridge() {
  const [status, setStatus] = useState<BridgeStatus>();
  const [mode, setMode] = useState<C2ConnectionConfig>();
  const [endpoints, setEndpoints] = useState<MAVLinkEndpoint[]>([]);

  async function refresh() {
    const [bridgeStatus, connectionMode, bridgeEndpoints] = await Promise.all([api.bridgeStatus(), api.connectionMode(), api.bridgeEndpoints()]);
    setStatus(bridgeStatus);
    setMode(connectionMode);
    setEndpoints(bridgeEndpoints);
  }

  useEffect(() => { refresh(); }, []);

  async function selectMode(nextMode: C2ConnectionMode) {
    setMode(await api.setConnectionMode(nextMode));
    setStatus(await api.bridgeStatus());
  }

  return <div className="space-y-4 text-zinc-200">
    <section className="rounded border border-amber-700/60 bg-amber-950/20 p-4 text-sm text-amber-100">
      Stage 1.3 is read-only and simulation-only. No real flight-controller commands are sent. Mission drafts and simulations do not upload to hardware.
    </section>
    <TelemetrySourcePanel />
    <section className="rounded border border-zinc-800 bg-zinc-950 p-4">
      <p className="text-xs uppercase tracking-[0.25em] text-zinc-500">Mission Planner Bridge</p>
      <h2 className="mt-2 text-xl font-semibold text-white">Compatibility and authority separation</h2>
      <p className="mt-3 max-w-3xl text-sm text-zinc-400">Mission Planner handles calibration/setup. Pramaan-X OS handles intelligent supervision, governance, audit logs, and future secure control.</p>
    </section>
    <div className="grid gap-4 lg:grid-cols-3">
      <Status label="Current C2 connection mode" value={mode?.mode ?? 'LOADING'} />
      <Status label="MAVLink bridge status" value={status?.status ?? 'LOADING'} />
      <Status label="Read-only mode" value={status?.read_only ? 'ENABLED' : 'ENFORCED'} />
      <Status label="Mission Planner compatibility" value={mode?.mission_planner_allowed ? 'ALLOWED' : 'LIMITED'} />
      <Status label="Hardware commands enabled" value={mode?.hardware_commands_enabled ? 'TRUE' : 'FALSE'} />
      <Status label="PUF required" value={mode?.puf_required ? 'TRUE' : 'FALSE'} />
    </div>
    <section className="grid gap-4 lg:grid-cols-4">
      {modes.map((item) => <button key={item} onClick={() => selectMode(item)} className={`rounded border p-4 text-left ${mode?.mode === item ? 'border-blue-400 bg-blue-950/20' : 'border-zinc-800 bg-zinc-950 hover:border-zinc-600'}`}>
        <div className="text-sm font-semibold text-white">{item}</div>
        <div className="mt-2 text-xs leading-5 text-zinc-400">{descriptionFor(item)}</div>
      </button>)}
    </section>
    <section className="rounded border border-zinc-800 bg-zinc-950 p-4">
      <p className="text-xs uppercase tracking-[0.25em] text-zinc-500">SITL / MAVProxy Read-Only Plan</p>
      <h3 className="mt-2 text-lg font-semibold text-white">Future telemetry sharing workflow</h3>
      <div className="mt-3 space-y-2 text-sm text-zinc-400">
        <p>Mission Planner remains the calibration/setup tool.</p>
        <p>Pramaan-X OS can later read the same MAVLink stream through MAVProxy or MAVLink Router.</p>
        <p>Stage 1.3 only prepares read-only telemetry support. No MAVLink command sending is enabled.</p>
        <pre className="overflow-auto rounded border border-zinc-800 bg-black p-3 text-xs text-zinc-300">mavproxy --master=COMx --out=127.0.0.1:14550

mavproxy.py --out=127.0.0.1:14550</pre>
        <p className="text-xs text-zinc-500">Examples are documentation/helper text only, not executable controls.</p>
      </div>
    </section>
    <section className="rounded border border-zinc-800 bg-zinc-950 p-4">
      <h3 className="text-sm font-semibold uppercase tracking-widest text-zinc-300">MAVLink Bridge endpoints</h3>
      <div className="mt-3 overflow-x-auto">
        <table className="w-full text-left text-sm"><thead className="text-xs uppercase text-zinc-500"><tr><th className="py-2">Endpoint</th><th>Name</th><th>Host</th><th>Status</th><th>Read-only</th></tr></thead><tbody>{endpoints.map((endpoint) => <tr key={endpoint.endpoint_id} className="border-t border-zinc-800"><td className="py-2 text-zinc-300">{endpoint.endpoint_id}</td><td>{endpoint.name}</td><td>{endpoint.protocol} {endpoint.host}:{endpoint.port}</td><td>{endpoint.status}</td><td>{endpoint.read_only ? 'true' : 'false'}</td></tr>)}</tbody></table>
      </div>
      <p className="mt-3 text-xs text-zinc-500">Future secure mode is a placeholder for later PUFShield integration and is not active in Stage 1.3.</p>
    </section>
  </div>;
}

function Status({ label, value }: { label: string; value: string }) {
  return <div className="rounded border border-zinc-800 bg-zinc-950 p-4"><div className="text-xs uppercase tracking-widest text-zinc-500">{label}</div><div className="mt-2 text-lg font-semibold text-white">{value}</div></div>;
}

function descriptionFor(mode: C2ConnectionMode) {
  if (mode === 'SETUP_MODE') return 'Mission Planner has setup authority; Pramaan-X is read-only.';
  if (mode === 'OPS_MONITOR_MODE') return 'Pramaan-X monitors telemetry; high-risk commands remain disabled.';
  if (mode === 'PRAMAAN_CONTROL_MODE') return 'Future operational authority mode; still simulation-only now.';
  return 'Future PUFShield-secure control placeholder; not active in Stage 1.3.';
}
