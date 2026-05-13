import { useEffect, useState } from 'react';
import { api } from './api/client';
import { connectTelemetry } from './api/websocket';
import Layout from './components/Layout';
import Audit from './pages/Audit';
import Commands from './pages/Commands';
import Dashboard from './pages/Dashboard';
import Drones from './pages/Drones';
import Profiles from './pages/Profiles';
import type { AuditLog } from './types/audit';
import type { Command } from './types/command';
import type { Drone } from './types/drone';
import type { VehicleProfile } from './types/profile';
import type { Telemetry } from './types/telemetry';

export default function App() {
  const [page, setPage] = useState('dashboard');
  const [drones, setDrones] = useState<Drone[]>([]);
  const [profiles, setProfiles] = useState<VehicleProfile[]>([]);
  const [telemetry, setTelemetry] = useState<Telemetry>();
  const [lastCommand, setLastCommand] = useState<Command>();
  const [audit, setAudit] = useState<AuditLog[]>([]);
  const primaryDrone = drones[0];

  async function refreshAudit() { setAudit(await api.audit()); }
  async function handleCommand(command: Command) { setLastCommand(command); await refreshAudit(); }

  useEffect(() => { api.drones().then(setDrones); api.profiles().then(setProfiles); refreshAudit(); }, []);
  useEffect(() => {
    if (!primaryDrone) return;
    api.latestTelemetry(primaryDrone.drone_id).then(setTelemetry).catch(() => undefined);
    const ws = connectTelemetry((message) => { if (message.drone_id === primaryDrone.drone_id) setTelemetry(message); });
    return () => ws.close();
  }, [primaryDrone?.drone_id]);

  let content = <Dashboard drone={primaryDrone} telemetry={telemetry} lastCommand={lastCommand} onCommand={handleCommand} />;
  if (page === 'drones') content = <Drones drones={drones} />;
  if (page === 'commands') content = primaryDrone ? <Commands droneId={primaryDrone.drone_id} lastCommand={lastCommand} onCommand={handleCommand} /> : <div>No drone registered.</div>;
  if (page === 'audit') content = <Audit logs={audit} />;
  if (page === 'profiles') content = <Profiles profiles={profiles} />;

  return <Layout page={page} setPage={setPage}>{content}</Layout>;
}
