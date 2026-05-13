import type { Command } from '../types/command';
import type { Telemetry } from '../types/telemetry';

export default function WarningPanel({ telemetry, lastCommand }: { telemetry?: Telemetry; lastCommand?: Command }) {
  const warnings = telemetry?.warnings?.length ? telemetry.warnings : ['NO_ACTIVE_WARNINGS'];
  return <div className="panel p-4">
    <div className="panel-title">Warnings</div>
    <ul className="mt-3 space-y-1 text-sm text-zinc-300">{warnings.map((warning) => <li key={warning}>{warning}</li>)}</ul>
    <div className="panel-title mt-5">Last Command Status</div>
    <div className="mt-2 text-sm text-zinc-300">{lastCommand ? `${lastCommand.command_type} / ${lastCommand.status} / ${lastCommand.decision}` : 'No command submitted this session.'}</div>
  </div>;
}
