import VehicleProfilePanel from '../components/VehicleProfilePanel';
import type { VehicleProfile } from '../types/profile';
export default function Profiles({ profiles }: { profiles: VehicleProfile[] }) { return <VehicleProfilePanel profiles={profiles} />; }
