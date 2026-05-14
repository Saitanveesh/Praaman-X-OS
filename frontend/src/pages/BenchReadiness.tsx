import { useEffect, useState } from 'react';
import { api } from '../api/client';
import type { BenchReadiness as BenchReadinessType } from '../types/mission';

export default function BenchReadiness() {
  const [readiness, setReadiness] = useState<BenchReadinessType>();

  useEffect(() => { api.benchReadiness().then(setReadiness).catch(() => undefined); }, []);

  return <div className="space-y-4 text-zinc-200">
    <section className="rounded border border-red-800/70 bg-red-950/20 p-4 text-sm text-red-100">
      Bench mode is read-only. Remove propellers before any future hardware test. Pramaan-X OS does not send hardware commands in this stage.
    </section>
    <section className="grid gap-4 lg:grid-cols-4">
      <Status label="Stage" value={readiness?.stage ?? 'LOADING'} />
      <Status label="Propellers removed required" value={readiness?.propellers_required_removed ? 'TRUE' : 'TRUE'} />
      <Status label="Read-only mode" value={readiness?.read_only ? 'ENFORCED' : 'ENFORCED'} />
      <Status label="Hardware commands enabled" value={readiness?.hardware_commands_enabled ? 'TRUE' : 'FALSE'} />
    </section>
    <section className="grid gap-4 lg:grid-cols-2">
      <div className="rounded border border-zinc-800 bg-zinc-950 p-4">
        <p className="text-xs uppercase tracking-[0.25em] text-zinc-500">Pixhawk Bench Readiness</p>
        <h2 className="mt-2 text-xl font-semibold text-white">Stage 3 read-only path placeholder</h2>
        <div className="mt-3 space-y-2 text-sm text-zinc-400">
          <p>Serial support: <span className="text-zinc-100">{readiness?.serial_supported ?? 'placeholder'}</span></p>
          <p>Recommended connection: <span className="text-zinc-100">{readiness?.recommended_connection ?? 'USB/Serial MAVLink read-only in future Stage 3.x'}</span></p>
          <p>Mission Planner role: calibration, setup, safety checks, and parameter review.</p>
          <p>Pramaan-X role: read-only telemetry dashboard, telemetry intelligence, audit, and mission supervision.</p>
        </div>
      </div>
      <div className="rounded border border-amber-800/70 bg-amber-950/20 p-4">
        <h3 className="text-sm font-semibold uppercase tracking-widest text-amber-100">Warning panel</h3>
        <div className="mt-3 space-y-2 text-sm text-amber-100">
          {(readiness?.warnings ?? []).map((warning) => <p key={warning} className="rounded border border-amber-900/70 bg-black/20 p-2">{warning}</p>)}
        </div>
      </div>
    </section>
    <section className="rounded border border-zinc-800 bg-zinc-950 p-4">
      <h3 className="text-sm font-semibold uppercase tracking-widest text-zinc-300">Bench checklist</h3>
      <ol className="mt-3 list-decimal space-y-2 pl-5 text-sm text-zinc-400">
        {(readiness?.checklist ?? []).map((item) => <li key={item}>{item}</li>)}
      </ol>
    </section>
  </div>;
}

function Status({ label, value }: { label: string; value: string }) {
  return <div className="rounded border border-zinc-800 bg-zinc-950 p-4"><div className="text-xs uppercase tracking-widest text-zinc-500">{label}</div><div className="mt-2 text-lg font-semibold text-white">{value}</div></div>;
}
