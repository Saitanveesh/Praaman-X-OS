import { useEffect, useState } from 'react';
import { api } from '../api/client';
import type { SITLReadiness as SITLReadinessType } from '../types/mission';

export default function SITLReadiness() {
  const [readiness, setReadiness] = useState<SITLReadinessType>();

  useEffect(() => { api.sitlReadiness().then(setReadiness).catch(() => undefined); }, []);

  return <div className="space-y-4 text-zinc-200">
    <section className="rounded border border-amber-700/60 bg-amber-950/20 p-4 text-sm text-amber-100">
      Documentation only. Pramaan-X OS does not launch SITL in Stage 1.4. MAVLink command sending and mission upload remain disabled.
    </section>

    <section className="grid gap-4 lg:grid-cols-2">
      <div className="rounded border border-zinc-800 bg-zinc-950 p-4">
        <p className="text-xs uppercase tracking-[0.25em] text-zinc-500">SITL Readiness</p>
        <h2 className="mt-2 text-xl font-semibold text-white">Future read-only telemetry checklist</h2>
        <div className="mt-4 grid gap-2 text-sm">
          <Status label="Readiness status" value={readiness?.status ?? 'LOADING'} />
          <Status label="Expected UDP host" value={readiness?.expected_host ?? '127.0.0.1'} />
          <Status label="Expected UDP port" value={String(readiness?.expected_port ?? 14550)} />
          <Status label="Current telemetry source" value={readiness?.telemetry_source ?? 'MOCK'} />
          <Status label="MAVLink read-only status" value={readiness?.mavlink_provider_status ?? 'INACTIVE'} />
          <Status label="Command sending enabled" value={String(readiness?.command_sending_enabled ?? false)} />
          <Status label="Read-only mode" value={String(readiness?.read_only ?? true)} />
        </div>
        <ol className="mt-4 list-decimal space-y-2 pl-5 text-sm text-zinc-400">
          {readiness?.checklist.map((item) => <li key={item}>{item}</li>)}
        </ol>
      </div>

      <div className="rounded border border-zinc-800 bg-zinc-950 p-4">
        <p className="text-xs uppercase tracking-[0.25em] text-zinc-500">Mission Planner Coexistence</p>
        <h2 className="mt-2 text-xl font-semibold text-white">Authority separation model</h2>
        <p className="mt-3 text-sm text-zinc-300">Mission Planner = calibration/setup/parameter tool</p>
        <p className="text-sm text-zinc-300">Pramaan-X OS = operational intelligence and supervision layer</p>
        <div className="mt-4 space-y-3 text-sm text-zinc-400">
          <Mode name="SETUP_MODE" text="Mission Planner has setup authority. Pramaan-X OS is read-only." />
          <Mode name="OPS_MONITOR_MODE" text="Pramaan-X OS monitors telemetry and logs. No high-risk commands enabled." />
          <Mode name="PRAMAAN_SIM_CONTROL_MODE" text="Pramaan-X OS can run simulation-only mission controls. No hardware commands." />
          <Mode name="FUTURE_SECURE_CONTROL_MODE" text="Reserved for future PUFShield integration. Unavailable in Stage 1." />
        </div>
      </div>
    </section>

    <section className="rounded border border-zinc-800 bg-zinc-950 p-4">
      <p className="text-xs uppercase tracking-[0.25em] text-zinc-500">Future SITL Flow</p>
      <pre className="mt-3 overflow-auto rounded border border-zinc-800 bg-black p-4 text-sm leading-7 text-zinc-300">{`ArduPilot SITL / Pixhawk
        ↓ MAVLink
MAVProxy / MAVLink Router
        ↓
Mission Planner + Pramaan-X OS`}</pre>
      <p className="mt-4 text-sm text-zinc-400">Example future commands are text only and are not executable controls:</p>
      <pre className="mt-2 overflow-auto rounded border border-zinc-800 bg-black p-3 text-xs text-zinc-300">mavproxy.py --out=127.0.0.1:14550</pre>
      <pre className="mt-2 overflow-auto rounded border border-zinc-800 bg-black p-3 text-xs text-zinc-300">sim_vehicle.py -v ArduCopter --console --map</pre>
      <p className="mt-3 text-xs uppercase tracking-widest text-amber-200">Documentation only. Pramaan-X OS does not launch SITL in Stage 1.4.</p>
      <p className="mt-2 text-sm text-zinc-500">{readiness?.recommended_next_step}</p>
    </section>
  </div>;
}

function Status({ label, value }: { label: string; value: string }) {
  return <p className="flex justify-between gap-3 rounded border border-zinc-800 bg-black p-2 text-zinc-500"><span>{label}</span><span className="font-mono text-zinc-100">{value}</span></p>;
}

function Mode({ name, text }: { name: string; text: string }) {
  return <div className="rounded border border-zinc-800 bg-black p-3"><div className="font-mono text-xs text-white">{name}</div><div className="mt-1 text-zinc-400">{text}</div></div>;
}
