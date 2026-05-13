import type { Command } from '../types/command';
import type { Drone } from '../types/drone';
import type { Telemetry } from '../types/telemetry';
import CommandPanel from '../components/CommandPanel';
import TelemetryPanel from '../components/TelemetryPanel';
import WarningPanel from '../components/WarningPanel';

export default function Dashboard({ drone, telemetry, lastCommand, onCommand }: { drone?: Drone; telemetry?: Telemetry; lastCommand?: Command; onCommand: (command: Command) => void }) {
  return <div className="space-y-4"><TelemetryPanel drone={drone} telemetry={telemetry} /><div className="grid gap-4 lg:grid-cols-2"><WarningPanel telemetry={telemetry} lastCommand={lastCommand} />{drone && <CommandPanel droneId={drone.drone_id} onCommand={onCommand} />}</div></div>;
}
