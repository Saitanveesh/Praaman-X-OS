import AuditTable from '../components/AuditTable';
import type { AuditLog } from '../types/audit';
export default function Audit({ logs }: { logs: AuditLog[] }) { return <AuditTable logs={logs} />; }
