import { useEffect, useState } from 'react';
import { api } from '../api/client';
import TelemetrySourcePanel from '../components/TelemetrySourcePanel';
import type { BridgeStatus, C2ConnectionConfig, C2ConnectionMode, ConnectionProfile, MAVLinkEndpoint, MAVLinkReadonlyStatus } from '../types/mission';

const modes: C2ConnectionMode[] = ['SETUP_MODE', 'OPS_MONITOR_MODE', 'PRAMAAN_CONTROL_MODE', 'FUTURE_SECURE_CONTROL_MODE'];

export default function Bridge() {
  const [status, setStatus] = useState<BridgeStatus>();
  const [mode, setMode] = useState<C2ConnectionConfig>();
  const [endpoints, setEndpoints] = useState<MAVLinkEndpoint[]>([]);
  const [profiles, setProfiles] = useState<ConnectionProfile[]>([]);
  const [activeSource, setActiveSource] = useState<string>('MOCK');
  const [mavlinkStatus, setMavlinkStatus] = useState<MAVLinkReadonlyStatus>();
  const [host, setHost] = useState('127.0.0.1');
  const [port, setPort] = useState(14550);
  const [protocol, setProtocol] = useState('UDP');
  const [mavlinkMessage, setMavlinkMessage] = useState('');

  async function refresh() {
    const [bridgeStatus, connectionMode, bridgeEndpoints, readonlyStatus, connectionProfiles, activeTelemetrySource] = await Promise.all([api.bridgeStatus(), api.connectionMode(), api.bridgeEndpoints(), api.mavlinkReadonlyDiagnostics(), api.connectionProfiles(), api.activeTelemetrySource()]);
    setStatus(bridgeStatus);
    setMode(connectionMode);
    setEndpoints(bridgeEndpoints);
    setMavlinkStatus(readonlyStatus);
    setProfiles(connectionProfiles);
    setActiveSource(activeTelemetrySource.active_source ?? activeTelemetrySource.source_type);
    setHost(readonlyStatus.host ?? '127.0.0.1');
    setPort(readonlyStatus.port ?? 14550);
    setProtocol(readonlyStatus.protocol ?? 'UDP');
  }

  useEffect(() => { refresh(); }, []);

  async function selectMode(nextMode: C2ConnectionMode) {
    setMode(await api.setConnectionMode(nextMode));
    setStatus(await api.bridgeStatus());
  }

  async function connectMavlinkReadonly() {
    setMavlinkMessage('');
    const result = await api.mavlinkReadonlyConnect({ host, port, protocol });
    setMavlinkStatus(result);
    if (result.ok === false || result.last_error) setMavlinkMessage(result.last_error ?? 'MAVLink read-only listener did not connect.');
  }

  async function disconnectMavlinkReadonly() {
    setMavlinkStatus(await api.mavlinkReadonlyDisconnect());
  }

  async function useSource(source: 'MOCK' | 'MAVLINK_READ_ONLY') {
    const result = await api.setTelemetrySource(source);
    setMavlinkMessage(result.message ?? 'Telemetry source updated.');
    await refresh();
  }

  function applyProfile(profileId: string) {
    const profile = profiles.find((item) => item.profile_id === profileId);
    if (!profile) return;
    setHost(profile.host ?? '127.0.0.1');
    setPort(profile.port ?? 14550);
    setProtocol(profile.protocol);
  }

  return <div className="space-y-4 text-zinc-200">
    <section className="rounded border border-amber-700/60 bg-amber-950/20 p-4 text-sm text-amber-100">
      Read-only mode. Pramaan-X OS does not send MAVLink commands in Stage 2.
    </section>
    <TelemetrySourcePanel />

    <section className="rounded border border-zinc-800 bg-zinc-950 p-4">
      <div className="rounded border border-amber-700/60 bg-amber-950/20 p-3 text-sm text-amber-100">Read-only mode. Pramaan-X OS does not send MAVLink commands in Stage 2.0.</div>
      <div className="mt-4 flex items-center justify-between gap-3">
        <div><p className="text-xs uppercase tracking-[0.25em] text-zinc-500">MAVLink Read-Only Connection</p><h3 className="mt-1 text-lg font-semibold text-white">SITL / MAVProxy UDP listener</h3></div>
        <span className="rounded border border-zinc-700 px-2 py-1 text-xs uppercase text-zinc-300">{mavlinkStatus?.connected ? 'CONNECTED' : 'DISCONNECTED'}</span>
      </div>
      <div className="mt-4 grid gap-3 md:grid-cols-4">
        <label className="text-xs uppercase tracking-widest text-zinc-500">Profile<select onChange={(event) => applyProfile(event.target.value)} defaultValue="" className="mt-1 w-full rounded border border-zinc-700 bg-black px-3 py-2 text-sm text-white"><option value="" disabled>Select profile</option>{profiles.map((profile) => <option key={profile.profile_id} value={profile.profile_id}>{profile.name}</option>)}</select></label>
        <label className="text-xs uppercase tracking-widest text-zinc-500">Host<input value={host} onChange={(event) => setHost(event.target.value)} className="mt-1 w-full rounded border border-zinc-700 bg-black px-3 py-2 text-sm text-white" /></label>
        <label className="text-xs uppercase tracking-widest text-zinc-500">Port<input type="number" value={port} onChange={(event) => setPort(Number(event.target.value))} className="mt-1 w-full rounded border border-zinc-700 bg-black px-3 py-2 text-sm text-white" /></label>
        <label className="text-xs uppercase tracking-widest text-zinc-500">Protocol<select value={protocol} onChange={(event) => setProtocol(event.target.value)} className="mt-1 w-full rounded border border-zinc-700 bg-black px-3 py-2 text-sm text-white"><option value="UDP">UDP - Supported for Stage 2</option><option value="TCP" disabled>TCP - Disabled / Placeholder</option><option value="SERIAL" disabled>SERIAL - Stage 3 Bench Placeholder</option></select></label>
      </div>
      <div className="mt-4 flex flex-wrap gap-2">
        <button onClick={connectMavlinkReadonly} className="rounded border border-zinc-600 px-3 py-2 text-xs uppercase text-white">Connect MAVLink Read-Only</button>
        <button onClick={disconnectMavlinkReadonly} className="rounded border border-zinc-600 px-3 py-2 text-xs uppercase text-white">Disconnect</button>
        <button onClick={() => useSource('MAVLINK_READ_ONLY')} className="rounded border border-zinc-600 px-3 py-2 text-xs uppercase text-white">Use MAVLink Read-Only Source</button>
        <button onClick={() => useSource('MOCK')} className="rounded border border-zinc-600 px-3 py-2 text-xs uppercase text-white">Use Mock Source</button>
        <button onClick={refresh} className="rounded border border-zinc-600 px-3 py-2 text-xs uppercase text-white">Refresh Diagnostics</button>
      </div>
      <div className="mt-4 grid gap-2 text-xs text-zinc-400 md:grid-cols-2">
        <p>Active telemetry source: <span className="text-zinc-100">{activeSource}</span></p>
        <p>Read-only enforced: <span className="text-zinc-100">{mavlinkStatus?.read_only ? 'true' : 'true'}</span></p>
        <p>Command sending enabled: <span className="text-zinc-100">false</span></p>
        <p>Mission upload enabled: <span className="text-zinc-100">false</span></p>
        <p>Endpoint: <span className="text-zinc-100">{mavlinkStatus?.endpoint ?? 'udpin:127.0.0.1:14550'}</span></p>
        <p>Last MAVLink message: <span className="text-zinc-100">{mavlinkStatus?.last_message_time ?? 'none'}</span></p>
        <p className="md:col-span-2">Parsed message counts: <span className="text-zinc-100">{mavlinkStatus ? Object.entries(mavlinkStatus.message_counts).map(([key, value]) => `${key}:${value}`).join(' / ') : 'none'}</span></p>
        {(mavlinkMessage || mavlinkStatus?.last_error) && <p className="rounded border border-amber-900/70 bg-amber-950/20 p-2 text-amber-100 md:col-span-2">Last error: {mavlinkMessage || mavlinkStatus?.last_error}</p>}
      </div>
    </section>
    <section className="rounded border border-zinc-800 bg-zinc-950 p-4">
      <p className="text-xs uppercase tracking-[0.25em] text-zinc-500">Mission Planner Bridge</p>
      <h2 className="mt-2 text-xl font-semibold text-white">Compatibility and authority separation</h2>
      <p className="mt-3 max-w-3xl text-sm text-zinc-400">Mission Planner = setup, calibration, parameter tuning. Pramaan-X OS = telemetry intelligence, mission supervision, audit, future secure C2. Only one system should hold command authority at a time. In Stage 2, Pramaan-X OS has no hardware command authority.</p>
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
        <p>Stage 2 supports UDP read-only telemetry, mission supervision, and intelligence panels. TCP remains disabled/placeholder; serial is reserved for Stage 3 bench readiness. No MAVLink command sending is enabled.</p>
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
      <p className="mt-3 text-xs text-zinc-500">Future secure mode is a placeholder for later PUFShield integration and is not active in Stage 1.</p>
    </section>
  </div>;
}

function Status({ label, value }: { label: string; value: string }) {
  return <div className="rounded border border-zinc-800 bg-zinc-950 p-4"><div className="text-xs uppercase tracking-widest text-zinc-500">{label}</div><div className="mt-2 text-lg font-semibold text-white">{value}</div></div>;
}

function descriptionFor(mode: C2ConnectionMode) {
  if (mode === 'SETUP_MODE') return 'Mission Planner has setup authority; Pramaan-X is read-only.';
  if (mode === 'OPS_MONITOR_MODE') return 'Pramaan-X monitors telemetry; high-risk commands remain disabled.';
  if (mode === 'PRAMAAN_CONTROL_MODE') return 'Pramaan-X can run simulation-only mission controls. No hardware commands.';
  return 'Future PUFShield-secure control placeholder; unavailable in Stage 1.';
}
