import CommandPanel from '../components/CommandPanel';
import type { Command } from '../types/command';
export default function Commands({ droneId, lastCommand, onCommand }: { droneId: string; lastCommand?: Command; onCommand: (command: Command) => void }) { return <div className="space-y-4"><CommandPanel droneId={droneId} onCommand={onCommand} />{lastCommand && <pre className="panel p-4 text-sm text-zinc-300">{JSON.stringify(lastCommand, null, 2)}</pre>}</div>; }
