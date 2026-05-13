import DroneRegistry from '../components/DroneRegistry';
import type { Drone } from '../types/drone';
export default function Drones({ drones }: { drones: Drone[] }) { return <DroneRegistry drones={drones} />; }
