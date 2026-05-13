import type { VehicleProfile } from '../types/profile';

export default function VehicleProfilePanel({ profiles }: { profiles: VehicleProfile[] }) {
  return <div className="grid gap-4 md:grid-cols-2">{profiles.map((profile) => <div className="panel p-4" key={profile.profile_id}><div className="panel-title">{profile.profile_id}</div><h3 className="mt-2 text-xl font-semibold text-zinc-100">{profile.name}</h3><p className="mt-1 text-sm text-zinc-400">{profile.vehicle_type}</p><div className="mt-4 grid gap-3 md:grid-cols-2"><pre className="overflow-auto bg-black/40 p-3 text-xs text-zinc-300">{JSON.stringify(profile.capabilities, null, 2)}</pre><pre className="overflow-auto bg-black/40 p-3 text-xs text-zinc-300">{JSON.stringify(profile.safety_limits, null, 2)}</pre></div></div>)}</div>;
}
