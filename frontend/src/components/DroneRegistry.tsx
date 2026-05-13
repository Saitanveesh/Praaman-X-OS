import type { Drone } from '../types/drone';

export default function DroneRegistry({ drones }: { drones: Drone[] }) {
  return <div className="panel overflow-hidden"><table className="w-full text-left text-sm"><thead className="bg-zinc-900 text-xs uppercase tracking-wide text-zinc-400"><tr><th className="p-3">Drone ID</th><th>Name</th><th>Type</th><th>Firmware</th><th>Status</th><th>Profile</th><th>Future PUF Status</th></tr></thead><tbody>{drones.map((drone) => <tr className="border-t border-zinc-800" key={drone.drone_id}><td className="p-3 font-medium text-zinc-100">{drone.drone_id}</td><td>{drone.name}</td><td>{drone.vehicle_type}</td><td>{drone.firmware_version}</td><td>{drone.status}</td><td>{drone.profile_id ?? '—'}</td><td>{drone.future_puf_status}</td></tr>)}</tbody></table></div>;
}
