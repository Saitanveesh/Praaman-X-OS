import { useState } from 'react';
import { api } from '../api/client';
import type { Command, CommandType } from '../types/command';

const commands: CommandType[] = ['READ_STATUS', 'START_LOGGING', 'STOP_LOGGING', 'SIMULATE_RTL', 'SIMULATE_LAND'];

export default function CommandPanel({ droneId, onCommand }: { droneId: string; onCommand: (command: Command) => void }) {
  const [busy, setBusy] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  async function submit(commandType: CommandType) {
    setBusy(commandType); setError(null);
    try { onCommand(await api.sendCommand(droneId, commandType)); }
    catch (err) { setError(err instanceof Error ? err.message : 'Command failed'); }
    finally { setBusy(null); }
  }
  return <div className="panel p-4">
    <div className="panel-title">Safe Command Panel</div>
    <p className="mt-2 text-sm text-zinc-400">Stage 1 routes only safe simulated commands through governance and mock transport.</p>
    <div className="mt-4 flex flex-wrap gap-2">{commands.map((command) => <button className="btn" disabled={!!busy} key={command} onClick={() => submit(command)}>{busy === command ? 'SENDING' : command}</button>)}</div>
    {error && <p className="mt-3 text-sm text-red-300">{error}</p>}
  </div>;
}
