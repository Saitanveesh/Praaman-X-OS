import { useEffect, useState } from 'react';
import type { Command } from '../types/command';
import type { Drone } from '../types/drone';
import type { IntelligenceSummary, SystemStatus } from '../types/mission';
import type { Telemetry } from '../types/telemetry';
import { api } from '../api/client';
import CommandPanel from '../components/CommandPanel';
import TelemetryPanel from '../components/TelemetryPanel';
import WarningPanel from '../components/WarningPanel';
import TelemetrySourcePanel from '../components/TelemetrySourcePanel';

export default function Dashboard({ drone, telemetry, lastCommand, onCommand }: { drone?: Drone; telemetry?: Telemetry; lastCommand?: Command; onCommand: (command: Command) => void }) {
  const [systemStatus, setSystemStatus] = useState<SystemStatus>();
  const [intelligence, setIntelligence] = useState<IntelligenceSummary>();

  useEffect(() => {
    api.systemStatus().then(setSystemStatus).catch(() => undefined);
  }, []);

  useEffect(() => {
    if (!drone?.drone_id) return;
    api.telemetryIntelligence(drone.drone_id).then(setIntelligence).catch(() => undefined);
    const timer = window.setInterval(() => api.telemetryIntelligence(drone.drone_id).then(setIntelligence).catch(() => undefined), 3000);
    return () => window.clearInterval(timer);
  }, [drone?.drone_id, telemetry?.timestamp]);

  return <div className="space-y-4">
    <section className="grid gap-4 xl:grid-cols-4">
      <Panel title="System Status">
        <StatusRow label="App stage" value={systemStatus?.app_stage ?? 'STAGE_1_SIMULATION'} />
        <StatusRow label="Hardware commands enabled" value={systemStatus?.hardware_commands_enabled ? 'true' : 'false'} />
        <StatusRow label="PUFShield integrated" value={systemStatus?.pufshield_integrated ? 'true' : 'false'} />
        <StatusRow label="Telemetry source" value={systemStatus?.active_telemetry_source ?? 'MOCK'} />
        <StatusRow label="Backend status" value={systemStatus?.backend_status ?? 'CHECKING'} />
        <StatusRow label="Safety mode" value="simulation-only" />
      </Panel>
      <Panel title="Telemetry Intelligence">
        <StatusRow label="Battery risk" value={intelligence?.telemetry.battery_risk ?? 'LOADING'} />
        <StatusRow label="Battery" value={`${intelligence?.telemetry.battery_level ?? telemetry?.battery_percent ?? 0}%`} />
        <StatusRow label="Freshness" value={intelligence?.telemetry.telemetry_freshness ?? 'UNKNOWN'} />
        <p className="mt-2 text-xs text-zinc-400">{intelligence?.telemetry.recommended_action ?? 'Waiting for telemetry intelligence.'}</p>
        {intelligence?.telemetry.warnings.map((warning) => <p key={warning} className="mt-2 rounded border border-amber-900/70 bg-amber-950/20 p-2 text-xs text-amber-100">{warning}</p>)}
      </Panel>
      <Panel title="Link Intelligence">
        <StatusRow label="Link state" value={intelligence?.link.link_state ?? telemetry?.link_state ?? 'UNKNOWN'} />
        <StatusRow label="Link risk" value={intelligence?.link.risk_level ?? 'UNKNOWN'} />
        <StatusRow label="Link quality" value={intelligence?.link.link_quality ?? 'UNKNOWN'} />
        <p className="mt-2 text-xs text-zinc-400">{intelligence?.link.operator_message ?? 'Waiting for link analysis.'}</p>
        <p className="mt-2 text-xs text-zinc-500">{intelligence?.link.recommended_action ?? 'No action.'}</p>
      </Panel>
      <Panel title="PUF Status">
        <StatusRow label="PUFShield" value="NOT INTEGRATED" />
        <StatusRow label="Hardware Verification" value="NOT AVAILABLE IN STAGE 1" />
        <StatusRow label="Secure Command Mode" value="DISABLED" />
        <p className="mt-2 text-xs text-zinc-500">Future PUFShield integration remains unavailable and is not a Stage 1 dependency.</p>
      </Panel>
    </section>
    <TelemetrySourcePanel compact />
    <TelemetryPanel drone={drone} telemetry={telemetry} />
    <div className="grid gap-4 lg:grid-cols-2"><WarningPanel telemetry={telemetry} lastCommand={lastCommand} />{drone && <CommandPanel droneId={drone.drone_id} onCommand={onCommand} />}</div>
  </div>;
}

function Panel({ title, children }: { title: string; children: React.ReactNode }) {
  return <section className="rounded border border-zinc-800 bg-zinc-950 p-4"><h3 className="text-xs font-semibold uppercase tracking-widest text-zinc-300">{title}</h3><div className="mt-3 space-y-1">{children}</div></section>;
}

function StatusRow({ label, value }: { label: string; value: string }) {
  return <p className="flex justify-between gap-3 text-xs text-zinc-500"><span>{label}</span><span className="text-right font-mono text-zinc-100">{value}</span></p>;
}
