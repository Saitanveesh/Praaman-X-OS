import type { AuditLog } from '../types/audit';

export default function AuditTable({ logs }: { logs: AuditLog[] }) {
  return <div className="panel overflow-hidden"><table className="w-full text-left text-sm"><thead className="bg-zinc-900 text-xs uppercase tracking-wide text-zinc-400"><tr><th className="p-3">Timestamp</th><th>Operator</th><th>Drone</th><th>Event</th><th>Command</th><th>Decision</th><th>Reason</th></tr></thead><tbody>{logs.map((log) => <tr className="border-t border-zinc-800" key={log.id}><td className="p-3">{new Date(log.timestamp).toLocaleString()}</td><td>{log.operator_id}</td><td>{log.drone_id}</td><td>{log.event_type}</td><td>{log.command_id ?? '—'}</td><td>{log.decision}</td><td className="pr-3 text-zinc-400">{log.reason}</td></tr>)}</tbody></table></div>;
}
