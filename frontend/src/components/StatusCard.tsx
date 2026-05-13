export default function StatusCard({ label, value }: { label: string; value?: string | number | boolean }) {
  return <div className="panel p-4"><div className="panel-title">{label}</div><div className="value mt-2">{String(value ?? '—')}</div></div>;
}
