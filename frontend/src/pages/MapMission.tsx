import { FormEvent, useEffect, useMemo, useState } from 'react';
import { api } from '../api/client';
import type { Drone } from '../types/drone';
import type { MapWaypoint, MissionDraft, MissionValidation, WaypointAction } from '../types/mission';
import type { VehicleProfile } from '../types/profile';
import type { Telemetry } from '../types/telemetry';

const actions: WaypointAction[] = ['NAVIGATE', 'LOITER', 'CAPTURE_IMAGE', 'START_RECORDING', 'STOP_RECORDING', 'RETURN_POINT'];

export default function MapMission({ drone, telemetry, profiles }: { drone?: Drone; telemetry?: Telemetry; profiles: VehicleProfile[] }) {
  const [missions, setMissions] = useState<MissionDraft[]>([]);
  const [selectedMissionId, setSelectedMissionId] = useState('');
  const [waypoints, setWaypoints] = useState<MapWaypoint[]>([]);
  const [validation, setValidation] = useState<MissionValidation>();
  const [missionName, setMissionName] = useState('Stage 1.1 Mission Draft');
  const [action, setAction] = useState<WaypointAction>('NAVIGATE');
  const selectedMission = missions.find((mission) => mission.mission_id === selectedMissionId);
  const profile = useMemo(() => profiles.find((item) => item.profile_id === drone?.profile_id), [profiles, drone?.profile_id]);

  async function refreshMissions() {
    const missionRows = await api.missions();
    setMissions(missionRows);
    if (!selectedMissionId && missionRows[0]) setSelectedMissionId(missionRows[0].mission_id);
  }

  useEffect(() => { refreshMissions(); }, []);
  useEffect(() => { if (selectedMissionId) api.waypoints(selectedMissionId).then(setWaypoints); }, [selectedMissionId]);

  async function createMission(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!drone) return;
    const created = await api.createMission({ name: missionName, drone_id: drone.drone_id, vehicle_type: drone.vehicle_type === 'FIXED_WING' ? 'FIXED_WING' : 'QUADCOPTER', default_altitude_m: 50, default_speed_mps: 8, lost_link_action: 'HOLD_THEN_RTL' });
    await refreshMissions();
    setSelectedMissionId(created.mission_id);
  }

  async function addWaypoint(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!selectedMissionId) return;
    const form = new FormData(event.currentTarget);
    await api.addWaypoint(selectedMissionId, { lat: Number(form.get('lat')), lon: Number(form.get('lon')), altitude_m: Number(form.get('altitude_m')), speed_mps: Number(form.get('speed_mps')), action, loiter_seconds: Number(form.get('loiter_seconds')) || null, notes: String(form.get('notes') ?? '') });
    setWaypoints(await api.waypoints(selectedMissionId));
    event.currentTarget.reset();
  }

  async function validateMission() {
    if (!selectedMissionId) return;
    setValidation(await api.validateMission(selectedMissionId));
    await refreshMissions();
  }

  const lat = telemetry?.lat ?? 0;
  const lon = telemetry?.lon ?? 0;

  return <div className="space-y-4 text-zinc-200">
    <section className="grid gap-4 lg:grid-cols-[2fr_1fr]">
      <div className="rounded border border-zinc-800 bg-zinc-950 p-4">
        <div className="flex items-center justify-between"><h2 className="text-lg font-semibold text-white">Map foundation</h2><span className="text-xs uppercase tracking-widest text-zinc-500">placeholder</span></div>
        <div className="relative mt-4 h-72 overflow-hidden rounded border border-zinc-800 bg-[#07090c]">
          <div className="absolute inset-0 opacity-30" style={{ backgroundImage: 'linear-gradient(#27272a 1px, transparent 1px), linear-gradient(90deg, #27272a 1px, transparent 1px)', backgroundSize: '32px 32px' }} />
          <div className="absolute left-1/2 top-1/2 h-3 w-3 -translate-x-1/2 -translate-y-1/2 rounded-full border border-blue-300 bg-blue-500" title="Drone marker placeholder" />
          <div className="absolute bottom-3 left-3 rounded border border-zinc-700 bg-black/70 px-3 py-2 text-xs text-zinc-300">Drone marker placeholder: {lat.toFixed(5)}, {lon.toFixed(5)}</div>
        </div>
        <p className="mt-3 text-sm text-zinc-400">Current drone position: latitude {lat.toFixed(6)}, longitude {lon.toFixed(6)}. Map/Mission features are mission draft and simulation-only.</p>
      </div>
      <div className="rounded border border-zinc-800 bg-zinc-950 p-4">
        <h3 className="text-sm font-semibold uppercase tracking-widest text-zinc-300">Vehicle profile validation</h3>
        <div className="mt-3 space-y-2 text-sm text-zinc-400"><p>Drone: <span className="text-zinc-100">{drone?.drone_id ?? 'None'}</span></p><p>Vehicle type: <span className="text-zinc-100">{drone?.vehicle_type ?? 'Unknown'}</span></p><p>Profile: <span className="text-zinc-100">{profile?.name ?? 'Not assigned'}</span></p><p>Command governance remains active; no mission upload to hardware is available.</p></div>
      </div>
    </section>

    <section className="grid gap-4 lg:grid-cols-2">
      <div className="rounded border border-zinc-800 bg-zinc-950 p-4">
        <h3 className="text-sm font-semibold uppercase tracking-widest text-zinc-300">Create mission draft</h3>
        <form onSubmit={createMission} className="mt-3 flex gap-2"><input value={missionName} onChange={(event) => setMissionName(event.target.value)} className="flex-1 rounded border border-zinc-700 bg-black px-3 py-2 text-sm text-white" /><button className="rounded border border-zinc-600 px-3 py-2 text-sm uppercase text-white">Create</button></form>
        <div className="mt-4 space-y-2">{missions.map((mission) => <button key={mission.mission_id} onClick={() => setSelectedMissionId(mission.mission_id)} className={`block w-full rounded border p-3 text-left text-sm ${selectedMissionId === mission.mission_id ? 'border-blue-400 bg-blue-950/20' : 'border-zinc-800 bg-black'}`}><div className="font-semibold text-white">{mission.name}</div><div className="text-xs text-zinc-500">{mission.mission_id} / {mission.status} / {mission.vehicle_type}</div></button>)}</div>
      </div>
      <div className="rounded border border-zinc-800 bg-zinc-950 p-4">
        <h3 className="text-sm font-semibold uppercase tracking-widest text-zinc-300">Add waypoint draft</h3>
        <form onSubmit={addWaypoint} className="mt-3 grid gap-2 md:grid-cols-2"><input name="lat" required defaultValue={lat.toFixed(6)} className="rounded border border-zinc-700 bg-black px-3 py-2 text-sm" /><input name="lon" required defaultValue={lon.toFixed(6)} className="rounded border border-zinc-700 bg-black px-3 py-2 text-sm" /><input name="altitude_m" type="number" defaultValue="50" className="rounded border border-zinc-700 bg-black px-3 py-2 text-sm" /><input name="speed_mps" type="number" defaultValue="8" className="rounded border border-zinc-700 bg-black px-3 py-2 text-sm" /><select value={action} onChange={(event) => setAction(event.target.value as WaypointAction)} className="rounded border border-zinc-700 bg-black px-3 py-2 text-sm">{actions.map((item) => <option key={item}>{item}</option>)}</select><input name="loiter_seconds" type="number" placeholder="Loiter seconds" className="rounded border border-zinc-700 bg-black px-3 py-2 text-sm" /><input name="notes" placeholder="Notes" className="rounded border border-zinc-700 bg-black px-3 py-2 text-sm md:col-span-2" /><button disabled={!selectedMissionId} className="rounded border border-zinc-600 px-3 py-2 text-sm uppercase text-white md:col-span-2">Add waypoint</button></form>
      </div>
    </section>

    <section className="grid gap-4 lg:grid-cols-2">
      <div className="rounded border border-zinc-800 bg-zinc-950 p-4"><div className="flex items-center justify-between"><h3 className="text-sm font-semibold uppercase tracking-widest text-zinc-300">Waypoint list</h3><button onClick={validateMission} disabled={!selectedMissionId} className="rounded border border-zinc-600 px-3 py-2 text-xs uppercase text-white">Validate mission</button></div><div className="mt-3 space-y-2">{waypoints.map((waypoint) => <div key={waypoint.id} className="rounded border border-zinc-800 bg-black p-3 text-sm"><span className="text-white">#{waypoint.sequence}</span> {waypoint.action} / {waypoint.lat.toFixed(5)}, {waypoint.lon.toFixed(5)} / {waypoint.altitude_m}m</div>)}</div>{validation && <div className="mt-3 rounded border border-zinc-800 bg-black p-3 text-sm"><p className={validation.valid ? 'text-emerald-300' : 'text-red-300'}>{validation.status}: {validation.valid ? 'valid draft' : 'invalid draft'}</p>{validation.errors.map((item) => <p key={item} className="text-red-300">Error: {item}</p>)}{validation.warnings.map((item) => <p key={item} className="text-amber-200">Warning: {item}</p>)}</div>}</div>
      <div className="rounded border border-zinc-800 bg-zinc-950 p-4"><h3 className="text-sm font-semibold uppercase tracking-widest text-zinc-300">Geofence placeholder panel</h3><p className="mt-3 text-sm text-zinc-400">Geofence drafts support polygon JSON and altitude bounds through backend APIs. No enforcement or hardware upload is enabled in Stage 1.1.</p><p className="mt-3 text-xs text-zinc-500">Selected mission: {selectedMission?.mission_id ?? 'none'}</p></div>
    </section>
  </div>;
}
