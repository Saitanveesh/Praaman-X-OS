import 'leaflet/dist/leaflet.css';
import { DivIcon, LatLngExpression } from 'leaflet';
import { FormEvent, useEffect, useMemo, useState } from 'react';
import { MapContainer, Marker, Polygon, Polyline, Popup, TileLayer, useMap } from 'react-leaflet';
import { api } from '../api/client';
import type { Drone } from '../types/drone';
import type { GeofenceDraft, MapWaypoint, MissionDraft, MissionEvent, MissionReport, MissionRouteSummary, MissionSimulationStatus, MissionValidation, TelemetrySourceConfig, WaypointAction } from '../types/mission';
import type { VehicleProfile } from '../types/profile';
import type { Telemetry } from '../types/telemetry';
import TelemetrySourcePanel from '../components/TelemetrySourcePanel';

const DEFAULT_CENTER = { lat: 12.9716, lon: 77.5946 };
const actions: WaypointAction[] = ['NAVIGATE', 'LOITER', 'CAPTURE_IMAGE', 'START_RECORDING', 'STOP_RECORDING', 'RETURN_POINT'];

const droneIcon = new DivIcon({ className: 'px-map-marker px-map-marker-drone', html: '<span>▲</span>', iconSize: [28, 28], iconAnchor: [14, 14] });
const homeIcon = new DivIcon({ className: 'px-map-marker px-map-marker-home', html: '<span>H</span>', iconSize: [24, 24], iconAnchor: [12, 12] });
const waypointIcon = (sequence: number) => new DivIcon({ className: 'px-map-marker px-map-marker-waypoint', html: `<span>${sequence}</span>`, iconSize: [24, 24], iconAnchor: [12, 12] });

function RecenterMap({ center }: { center: LatLngExpression }) {
  const map = useMap();
  useEffect(() => { map.setView(center, map.getZoom(), { animate: false }); }, [center, map]);
  return null;
}

function parseGeofencePolygon(geofence?: GeofenceDraft): LatLngExpression[] {
  if (!geofence) return [];
  try {
    const parsed = JSON.parse(geofence.polygon_json) as Array<{ lat?: number; lon?: number; lng?: number } | [number, number]>;
    return parsed
      .map((point) => Array.isArray(point) ? point : [point.lat, point.lon ?? point.lng])
      .filter((point): point is [number, number] => typeof point[0] === 'number' && typeof point[1] === 'number');
  } catch {
    return [];
  }
}

function haversineDistanceM(points: LatLngExpression[]): number {
  const toTuple = (point: LatLngExpression): [number, number] => Array.isArray(point) ? [Number(point[0]), Number(point[1])] : [point.lat, point.lng];
  const earthRadiusM = 6371000;
  let distance = 0;
  for (let i = 1; i < points.length; i += 1) {
    const [lat1, lon1] = toTuple(points[i - 1]);
    const [lat2, lon2] = toTuple(points[i]);
    const phi1 = lat1 * Math.PI / 180;
    const phi2 = lat2 * Math.PI / 180;
    const deltaPhi = (lat2 - lat1) * Math.PI / 180;
    const deltaLambda = (lon2 - lon1) * Math.PI / 180;
    const a = Math.sin(deltaPhi / 2) ** 2 + Math.cos(phi1) * Math.cos(phi2) * Math.sin(deltaLambda / 2) ** 2;
    distance += earthRadiusM * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  }
  return distance;
}

export default function MapMission({ drone, telemetry, profiles }: { drone?: Drone; telemetry?: Telemetry; profiles: VehicleProfile[] }) {
  const [missions, setMissions] = useState<MissionDraft[]>([]);
  const [selectedMissionId, setSelectedMissionId] = useState('');
  const [waypoints, setWaypoints] = useState<MapWaypoint[]>([]);
  const [geofences, setGeofences] = useState<GeofenceDraft[]>([]);
  const [validation, setValidation] = useState<MissionValidation>();
  const [summary, setSummary] = useState<MissionRouteSummary>({ waypoint_count: 0, estimated_distance_m: 0, max_altitude_m: 0, min_altitude_m: 0 });
  const [missionName, setMissionName] = useState('Stage 1.6 Mission Draft');
  const [missionDroneId, setMissionDroneId] = useState('PX-QD-001');
  const [vehicleType, setVehicleType] = useState<'QUADCOPTER' | 'FIXED_WING'>('QUADCOPTER');
  const [defaultAltitude, setDefaultAltitude] = useState(40);
  const [defaultSpeed, setDefaultSpeed] = useState(6);
  const [lostLinkAction, setLostLinkAction] = useState('HOLD_THEN_RTL');
  const [action, setAction] = useState<WaypointAction>('NAVIGATE');
  const [mapError, setMapError] = useState<string>();
  const [history, setHistory] = useState<Telemetry[]>([]);
  const [events, setEvents] = useState<MissionEvent[]>([]);
  const [simulation, setSimulation] = useState<MissionSimulationStatus>();
  const [activeSource, setActiveSource] = useState<TelemetrySourceConfig>();
  const [eventFilter, setEventFilter] = useState('');
  const [missionJson, setMissionJson] = useState('');
  const [report, setReport] = useState<MissionReport>();
  const [importJson, setImportJson] = useState('');
  const [importMessage, setImportMessage] = useState('');

  const selectedMission = missions.find((mission) => mission.mission_id === selectedMissionId);
  const profile = useMemo(() => profiles.find((item) => item.profile_id === drone?.profile_id), [profiles, drone?.profile_id]);
  const lat = telemetry?.lat ?? DEFAULT_CENTER.lat;
  const lon = telemetry?.lon ?? DEFAULT_CENTER.lon;
  const center: LatLngExpression = [lat, lon];
  const homePoint: LatLngExpression = [DEFAULT_CENTER.lat, DEFAULT_CENTER.lon];
  const routePoints: LatLngExpression[] = waypoints.map((waypoint) => [waypoint.lat, waypoint.lon]);
  const trackPoints: LatLngExpression[] = history.map((point) => [point.lat, point.lon]);
  const activeGeofence = geofences.find((geofence) => geofence.drone_id === (selectedMission?.drone_id ?? missionDroneId)) ?? geofences[0];
  const geofencePolygon = parseGeofencePolygon(activeGeofence);
  const frontendSummary = useMemo(() => {
    const altitudes = waypoints.map((waypoint) => waypoint.altitude_m);
    const estimatedDistance = summary.estimated_distance_m || haversineDistanceM(routePoints);
    const speed = selectedMission?.default_speed_mps ?? defaultSpeed;
    return {
      waypoint_count: waypoints.length,
      estimated_distance_m: estimatedDistance,
      estimated_duration_s: speed > 0 ? estimatedDistance / speed : 0,
      max_altitude_m: altitudes.length ? Math.max(...altitudes) : 0,
      min_altitude_m: altitudes.length ? Math.min(...altitudes) : 0,
    };
  }, [defaultSpeed, routePoints, selectedMission?.default_speed_mps, summary.estimated_distance_m, waypoints]);

  const filteredEvents = useMemo(() => {
    const needle = eventFilter.trim().toLowerCase();
    if (!needle) return events;
    return events.filter((event) => `${event.event_type} ${event.severity} ${event.message}`.toLowerCase().includes(needle));
  }, [eventFilter, events]);

  const latestMissionEvent = events[events.length - 1];
  const isMavlinkSource = activeSource?.source_type === 'MAVLINK_READ_ONLY';

  const localWarnings = useMemo(() => {
    const warnings: string[] = [];
    if (!selectedMission) warnings.push('No mission selected. Create or select a draft before planning.');
    if (selectedMission && waypoints.length === 0) warnings.push('No waypoints added. Route preview is empty.');
    waypoints.forEach((waypoint) => {
      if (waypoint.lat < -90 || waypoint.lat > 90 || waypoint.lon < -180 || waypoint.lon > 180) warnings.push(`Waypoint ${waypoint.sequence} has invalid latitude/longitude.`);
      if (waypoint.altitude_m <= 0) warnings.push(`Waypoint ${waypoint.sequence} altitude is below or equal to zero.`);
    });
    if (selectedMission?.vehicle_type === 'FIXED_WING' && !waypoints.some((waypoint) => waypoint.action === 'LOITER' || waypoint.action === 'RETURN_POINT')) warnings.push('Fixed-wing draft has no LOITER or RETURN_POINT behavior.');
    if (!activeGeofence) warnings.push('Geofence missing. This is informational in Stage 1.6.');
    warnings.push('Mission is draft/simulation-only. No mission upload to drone hardware is available.');
    return warnings;
  }, [activeGeofence, selectedMission, waypoints]);

  async function refreshMissions(nextSelectedId = selectedMissionId) {
    const missionRows = await api.missions();
    setMissions(missionRows);
    if (nextSelectedId) setSelectedMissionId(nextSelectedId);
    else if (missionRows[0]) setSelectedMissionId(missionRows[0].mission_id);
  }

  async function refreshGeofences() { setGeofences(await api.geofences()); }

  useEffect(() => {
    refreshMissions();
    refreshGeofences();
  }, []);

  useEffect(() => {
    if (!drone) return;
    setMissionDroneId(drone.drone_id);
    setVehicleType(drone.vehicle_type === 'FIXED_WING' ? 'FIXED_WING' : 'QUADCOPTER');
  }, [drone]);

  useEffect(() => {
    if (!selectedMissionId) {
      setWaypoints([]);
      setSummary({ waypoint_count: 0, estimated_distance_m: 0, max_altitude_m: 0, min_altitude_m: 0 });
      return;
    }
    api.waypoints(selectedMissionId).then(setWaypoints);
    api.missionSummary(selectedMissionId).then(setSummary).catch(() => undefined);
    api.missionEvents(selectedMissionId).then(setEvents).catch(() => undefined);
    api.missionSimulationStatus(selectedMissionId).then(setSimulation).catch(() => undefined);
    setValidation(undefined);
  }, [selectedMissionId]);

  useEffect(() => {
    if (!drone?.drone_id) return;
    api.telemetryHistory(drone.drone_id, 200).then(setHistory).catch(() => undefined);
    api.activeTelemetrySource().then(setActiveSource).catch(() => undefined);
    const timer = window.setInterval(() => {
      api.telemetryHistory(drone.drone_id, 200).then(setHistory).catch(() => undefined);
      api.activeTelemetrySource().then(setActiveSource).catch(() => undefined);
      if (selectedMissionId) {
        api.missionEvents(selectedMissionId).then(setEvents).catch(() => undefined);
        api.missionSimulationStatus(selectedMissionId).then(setSimulation).catch(() => undefined);
      }
    }, 3000);
    return () => window.clearInterval(timer);
  }, [drone?.drone_id, selectedMissionId]);

  async function createMission(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const created = await api.createMission({ name: missionName, drone_id: missionDroneId, vehicle_type: vehicleType, default_altitude_m: defaultAltitude, default_speed_mps: defaultSpeed, lost_link_action: lostLinkAction });
    await refreshMissions(created.mission_id);
    setSelectedMissionId(created.mission_id);
  }

  async function addWaypoint(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!selectedMissionId) return;
    const form = new FormData(event.currentTarget);
    await api.addWaypoint(selectedMissionId, { lat: Number(form.get('lat')), lon: Number(form.get('lon')), altitude_m: Number(form.get('altitude_m')), speed_mps: Number(form.get('speed_mps')), action, loiter_seconds: Number(form.get('loiter_seconds')) || null, notes: String(form.get('notes') ?? '') });
    setWaypoints(await api.waypoints(selectedMissionId));
    setSummary(await api.missionSummary(selectedMissionId));
    event.currentTarget.reset();
  }

  async function validateMission() {
    if (!selectedMissionId) return;
    const result = await api.validateMission(selectedMissionId);
    setValidation(result);
    setSummary(result.summary);
    setEvents(await api.missionEvents(selectedMissionId));
    await refreshMissions(selectedMissionId);
  }

  async function startSimulation() {
    if (!selectedMissionId || isMavlinkSource) return;
    setSimulation(await api.startMissionSimulation(selectedMissionId));
    setEvents(await api.missionEvents(selectedMissionId));
  }

  async function stopSimulation() {
    if (!selectedMissionId || isMavlinkSource) return;
    setSimulation(await api.stopMissionSimulation(selectedMissionId));
    setEvents(await api.missionEvents(selectedMissionId));
  }

  async function pauseSimulation() {
    if (!selectedMissionId || isMavlinkSource) return;
    setSimulation(await api.pauseMissionSimulation(selectedMissionId));
    setEvents(await api.missionEvents(selectedMissionId));
  }

  async function resumeSimulation() {
    if (!selectedMissionId || isMavlinkSource) return;
    setSimulation(await api.resumeMissionSimulation(selectedMissionId));
    setEvents(await api.missionEvents(selectedMissionId));
  }

  async function resetSimulation() {
    if (!selectedMissionId || isMavlinkSource) return;
    setSimulation(await api.resetMissionSimulation(selectedMissionId));
    setEvents(await api.missionEvents(selectedMissionId));
  }

  async function exportMissionJson() {
    if (!selectedMissionId) return;
    setMissionJson(JSON.stringify(await api.exportMission(selectedMissionId), null, 2));
  }

  async function generateMissionReport() {
    if (!selectedMissionId) return;
    const nextReport = await api.missionReport(selectedMissionId);
    setReport(nextReport);
    setMissionJson(JSON.stringify(nextReport, null, 2));
  }

  async function importMissionDraft() {
    try {
      const created = await api.importMission(JSON.parse(importJson));
      setImportMessage(`Imported draft ${created.mission_id}. Draft-only; no hardware upload.`);
      await refreshMissions(created.mission_id);
      setSelectedMissionId(created.mission_id);
    } catch (error) {
      setImportMessage(error instanceof Error ? error.message : 'Import failed.');
    }
  }

  async function createDraftGeofence() {
    const delta = 0.003;
    const polygon = [
      { lat: lat - delta, lon: lon - delta },
      { lat: lat - delta, lon: lon + delta },
      { lat: lat + delta, lon: lon + delta },
      { lat: lat + delta, lon: lon - delta },
    ];
    await api.createGeofence({ name: 'Stage 1.6 Draft Geofence', drone_id: selectedMission?.drone_id ?? missionDroneId, enabled: true, polygon_json: JSON.stringify(polygon), max_altitude_m: 120, min_altitude_m: 0 });
    await refreshGeofences();
  }

  return <div className="space-y-4 text-zinc-200">
    <section className="grid gap-4 xl:grid-cols-[2fr_1fr]">
      <div className="rounded border border-zinc-800 bg-zinc-950 p-4">
        <div className="flex items-center justify-between"><h2 className="text-lg font-semibold text-white">Real map / mission preview</h2><span className="text-xs uppercase tracking-widest text-zinc-500">simulation-only</span></div>
        <div className="mt-4 h-[28rem] overflow-hidden rounded border border-zinc-800 bg-[#07090c]">
          {!mapError ? <MapContainer center={center} zoom={16} className="h-full w-full" whenReady={() => setMapError(undefined)}>
            <RecenterMap center={center} />
            <TileLayer eventHandlers={{ tileerror: () => setMapError('Map tiles are unavailable; using coordinate fallback text.') }} attribution="&copy; OpenStreetMap contributors" url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
            <Marker position={homePoint} icon={homeIcon}><Popup>Home point / simulation origin<br />{DEFAULT_CENTER.lat.toFixed(6)}, {DEFAULT_CENTER.lon.toFixed(6)}</Popup></Marker>
            <Marker position={center} icon={droneIcon}><Popup>Live telemetry marker: {telemetry?.drone_id ?? 'PX-QD-001'}<br />{lat.toFixed(6)}, {lon.toFixed(6)}</Popup></Marker>
            {routePoints.length > 1 && <Polyline positions={routePoints} pathOptions={{ color: '#d4d4d8', weight: 2 }} />}
            {trackPoints.length > 1 && <Polyline positions={trackPoints} pathOptions={{ color: '#60a5fa', weight: 2, dashArray: '4 4' }} />}
            {waypoints.map((waypoint) => <Marker key={waypoint.id} position={[waypoint.lat, waypoint.lon]} icon={waypointIcon(waypoint.sequence)}><Popup>WP {waypoint.sequence}: {waypoint.action}<br />{waypoint.altitude_m}m / {waypoint.speed_mps}mps</Popup></Marker>)}
            {geofencePolygon.length >= 3 && <Polygon positions={geofencePolygon} pathOptions={{ color: '#94a3b8', fillColor: '#64748b', fillOpacity: 0.12, weight: 1 }} />}
          </MapContainer> : <div className="flex h-full items-center justify-center p-6 text-center text-sm text-zinc-400">{mapError}<br />Drone marker fallback: {lat.toFixed(6)}, {lon.toFixed(6)}</div>}
        </div>
        <p className="mt-3 text-sm text-zinc-400">Drone marker uses latest telemetry for PX-QD-001 when available, including MAVLink-derived telemetry when MAVLINK_READ_ONLY is active. Home defaults to Bengaluru coordinates. Mission routes are silver previews; live telemetry history tracks are dashed blue read-only paths.</p>
      </div>
      <div className="rounded border border-zinc-800 bg-zinc-950 p-4">
        <h3 className="text-sm font-semibold uppercase tracking-widest text-zinc-300">Vehicle / safety context</h3>
        <div className="mt-3 space-y-2 text-sm text-zinc-400"><p>Drone: <span className="text-zinc-100">{drone?.drone_id ?? 'PX-QD-001 fallback'}</span></p><p>Vehicle type: <span className="text-zinc-100">{drone?.vehicle_type ?? 'QUADCOPTER fallback'}</span></p><p>Profile: <span className="text-zinc-100">{profile?.name ?? 'Not assigned'}</span></p><p>Telemetry: <span className="text-zinc-100">{telemetry ? 'live/mock stream active' : 'fallback coordinate active'}</span></p><p>Source: <span className="text-zinc-100">{activeSource?.source_type ?? 'UNKNOWN'}</span></p><p>No ARM, TAKEOFF, DISARM, mission upload, payload, or MAVLink hardware execution is available.</p></div>
      </div>
    </section>

    <section className="rounded border border-amber-700/60 bg-amber-950/20 p-4 text-sm text-amber-100">
      Stage 2.0 read-only safety remains enforced. No real flight-controller commands are sent. Mission drafts do not upload to hardware.
      {isMavlinkSource && <p className="mt-2">Mission simulation is available only with MOCK telemetry source.</p>}
    </section>
    <TelemetrySourcePanel compact />

    <section className="grid gap-4 xl:grid-cols-[1fr_1fr]">
      <div className="rounded border border-zinc-800 bg-zinc-950 p-4">
        <h3 className="text-sm font-semibold uppercase tracking-widest text-zinc-300">Mission draft panel</h3>
        <form onSubmit={createMission} className="mt-3 grid gap-2 md:grid-cols-2"><input aria-label="Mission name" value={missionName} onChange={(event) => setMissionName(event.target.value)} className="rounded border border-zinc-700 bg-black px-3 py-2 text-sm text-white md:col-span-2" /><input aria-label="Drone ID" value={missionDroneId} onChange={(event) => setMissionDroneId(event.target.value)} className="rounded border border-zinc-700 bg-black px-3 py-2 text-sm" /><select aria-label="Vehicle type" value={vehicleType} onChange={(event) => setVehicleType(event.target.value as 'QUADCOPTER' | 'FIXED_WING')} className="rounded border border-zinc-700 bg-black px-3 py-2 text-sm"><option>QUADCOPTER</option><option>FIXED_WING</option></select><input aria-label="Default altitude" type="number" value={defaultAltitude} onChange={(event) => setDefaultAltitude(Number(event.target.value))} className="rounded border border-zinc-700 bg-black px-3 py-2 text-sm" /><input aria-label="Default speed" type="number" value={defaultSpeed} onChange={(event) => setDefaultSpeed(Number(event.target.value))} className="rounded border border-zinc-700 bg-black px-3 py-2 text-sm" /><input aria-label="Lost link action" value={lostLinkAction} onChange={(event) => setLostLinkAction(event.target.value)} className="rounded border border-zinc-700 bg-black px-3 py-2 text-sm md:col-span-2" /><button className="rounded border border-zinc-600 px-3 py-2 text-sm uppercase text-white md:col-span-2">Create draft</button></form>
        {selectedMission && <div className="mt-4 rounded border border-zinc-800 bg-black p-3 text-sm text-zinc-400"><p className="text-white">{selectedMission.name}</p><p>{selectedMission.mission_id} / {selectedMission.status}</p><p>{selectedMission.drone_id} / {selectedMission.vehicle_type}</p><p>Default: {selectedMission.default_altitude_m}m, {selectedMission.default_speed_mps}mps / {selectedMission.lost_link_action}</p><p>Validation: {validation?.status ?? 'not run this session'}</p></div>}
        <div className="mt-4 max-h-64 space-y-2 overflow-auto">{missions.map((mission) => <button key={mission.mission_id} onClick={() => setSelectedMissionId(mission.mission_id)} className={`block w-full rounded border p-3 text-left text-sm ${selectedMissionId === mission.mission_id ? 'border-sky-300 bg-sky-950/20' : 'border-zinc-800 bg-black'}`}><div className="font-semibold text-white">{mission.name}</div><div className="text-xs text-zinc-500">{mission.mission_id} / {mission.status} / {mission.vehicle_type}</div></button>)}</div>
      </div>
      <div className="rounded border border-zinc-800 bg-zinc-950 p-4">
        <h3 className="text-sm font-semibold uppercase tracking-widest text-zinc-300">Waypoint panel</h3>
        <form onSubmit={addWaypoint} className="mt-3 grid gap-2 md:grid-cols-2"><input name="lat" required defaultValue={lat.toFixed(6)} className="rounded border border-zinc-700 bg-black px-3 py-2 text-sm" /><input name="lon" required defaultValue={lon.toFixed(6)} className="rounded border border-zinc-700 bg-black px-3 py-2 text-sm" /><input name="altitude_m" type="number" defaultValue={selectedMission?.default_altitude_m ?? 40} className="rounded border border-zinc-700 bg-black px-3 py-2 text-sm" /><input name="speed_mps" type="number" defaultValue={selectedMission?.default_speed_mps ?? 6} className="rounded border border-zinc-700 bg-black px-3 py-2 text-sm" /><select value={action} onChange={(event) => setAction(event.target.value as WaypointAction)} className="rounded border border-zinc-700 bg-black px-3 py-2 text-sm">{actions.map((item) => <option key={item}>{item}</option>)}</select><input name="loiter_seconds" type="number" placeholder="Loiter seconds" className="rounded border border-zinc-700 bg-black px-3 py-2 text-sm" /><input name="notes" placeholder="Notes" className="rounded border border-zinc-700 bg-black px-3 py-2 text-sm md:col-span-2" /><button disabled={!selectedMissionId} className="rounded border border-zinc-600 px-3 py-2 text-sm uppercase text-white md:col-span-2">Add waypoint draft</button></form>
      </div>
    </section>

    <section className="grid gap-4 xl:grid-cols-[1.2fr_0.8fr]">
      <div className="rounded border border-zinc-800 bg-zinc-950 p-4"><div className="flex items-center justify-between"><h3 className="text-sm font-semibold uppercase tracking-widest text-zinc-300">Waypoint table</h3><button onClick={validateMission} disabled={!selectedMissionId} className="rounded border border-zinc-600 px-3 py-2 text-xs uppercase text-white">Validate mission</button></div><div className="mt-3 overflow-auto"><table className="w-full text-left text-xs"><thead className="text-zinc-500"><tr><th className="p-2">Seq</th><th className="p-2">Lat</th><th className="p-2">Lon</th><th className="p-2">Alt</th><th className="p-2">Speed</th><th className="p-2">Action</th><th className="p-2">Notes</th></tr></thead><tbody>{waypoints.map((waypoint) => <tr key={waypoint.id} className="border-t border-zinc-800"><td className="p-2 text-white">{waypoint.sequence}</td><td className="p-2">{waypoint.lat.toFixed(6)}</td><td className="p-2">{waypoint.lon.toFixed(6)}</td><td className="p-2">{waypoint.altitude_m}m</td><td className="p-2">{waypoint.speed_mps}mps</td><td className="p-2">{waypoint.action}</td><td className="p-2">{waypoint.notes}</td></tr>)}</tbody></table>{waypoints.length === 0 && <p className="p-3 text-sm text-zinc-500">No waypoint drafts added.</p>}</div></div>
      <div className="rounded border border-zinc-800 bg-zinc-950 p-4"><h3 className="text-sm font-semibold uppercase tracking-widest text-zinc-300">Route summary</h3><div className="mt-3 grid grid-cols-2 gap-2 text-sm"><p className="rounded border border-zinc-800 bg-black p-2">Waypoints<br /><span className="text-lg text-white">{frontendSummary.waypoint_count}</span></p><p className="rounded border border-zinc-800 bg-black p-2">Distance<br /><span className="text-lg text-white">{frontendSummary.estimated_distance_m.toFixed(1)} m</span></p><p className="rounded border border-zinc-800 bg-black p-2">Duration<br /><span className="text-lg text-white">{frontendSummary.estimated_duration_s.toFixed(1)} s</span></p><p className="rounded border border-zinc-800 bg-black p-2">Highest altitude<br /><span className="text-lg text-white">{frontendSummary.max_altitude_m} m</span></p><p className="rounded border border-zinc-800 bg-black p-2">Lowest altitude<br /><span className="text-lg text-white">{frontendSummary.min_altitude_m} m</span></p><p className="rounded border border-zinc-800 bg-black p-2">Vehicle<br /><span className="text-white">{selectedMission?.vehicle_type ?? vehicleType}</span></p><p className="rounded border border-zinc-800 bg-black p-2">Lost link<br /><span className="text-white">{selectedMission?.lost_link_action ?? lostLinkAction}</span></p></div><p className={`mt-3 text-sm ${validation?.valid ? 'text-emerald-300' : validation ? 'text-red-300' : 'text-zinc-400'}`}>Validation result: {validation ? `${validation.status} (${validation.valid ? 'valid' : 'invalid'})` : 'not run'}</p></div>
    </section>

    <section className="grid gap-4 xl:grid-cols-2">
      <div className="rounded border border-zinc-800 bg-zinc-950 p-4">
        <div className="flex items-center justify-between gap-3">
          <h3 className="text-sm font-semibold uppercase tracking-widest text-zinc-300">Mission simulation controls</h3>
          <span className="rounded border border-zinc-700 px-2 py-1 text-xs text-zinc-300">{simulation?.state ?? 'IDLE'}</span>
        </div>
        <p className="mt-2 text-sm text-zinc-400">Simulation moves mock telemetry along draft waypoints only. It does not upload missions or send MAVLink commands.</p>
        <div className="mt-3 flex flex-wrap gap-2">
          <button onClick={startSimulation} disabled={!selectedMissionId || isMavlinkSource} className="rounded border border-zinc-600 px-3 py-2 text-xs uppercase text-white disabled:opacity-40">Start Simulation</button>
          <button onClick={pauseSimulation} disabled={!selectedMissionId || isMavlinkSource} className="rounded border border-zinc-600 px-3 py-2 text-xs uppercase text-white disabled:opacity-40">Pause</button>
          <button onClick={resumeSimulation} disabled={!selectedMissionId || isMavlinkSource} className="rounded border border-zinc-600 px-3 py-2 text-xs uppercase text-white disabled:opacity-40">Resume</button>
          <button onClick={stopSimulation} disabled={!selectedMissionId || isMavlinkSource} className="rounded border border-zinc-600 px-3 py-2 text-xs uppercase text-white disabled:opacity-40">Stop</button>
          <button onClick={resetSimulation} disabled={!selectedMissionId || isMavlinkSource} className="rounded border border-zinc-600 px-3 py-2 text-xs uppercase text-white disabled:opacity-40">Reset</button>
        </div>
        {isMavlinkSource && <p className="mt-2 rounded border border-amber-900/70 bg-amber-950/20 p-2 text-xs text-amber-100">Mission simulation is available only with MOCK telemetry source.</p>}
        <p className="mt-2 text-xs text-zinc-500">Current mission: {selectedMission?.name ?? 'none'}</p>
        <p className="mt-2 text-xs text-zinc-500">{simulation?.message ?? 'Select a mission to view simulation status.'} Waypoint {simulation ? simulation.active_waypoint_index + 1 : 0} / {simulation?.waypoint_count ?? waypoints.length}</p>
        <p className="mt-2 text-xs text-zinc-500">Latest event: {latestMissionEvent ? `${latestMissionEvent.event_type} / ${latestMissionEvent.message}` : 'none'}</p>
        <p className="mt-2 text-xs text-zinc-500">Flight track points loaded: {trackPoints.length}</p>
      </div>
      <div className="rounded border border-zinc-800 bg-zinc-950 p-4">
        <div className="flex items-center justify-between gap-3"><h3 className="text-sm font-semibold uppercase tracking-widest text-zinc-300">Mission event timeline</h3><input value={eventFilter} onChange={(event) => setEventFilter(event.target.value)} placeholder="Filter event/severity" className="rounded border border-zinc-700 bg-black px-2 py-1 text-xs text-zinc-200" /></div>
        <div className="mt-3 max-h-56 overflow-auto">
          <table className="w-full text-left text-xs">
            <thead className="text-zinc-500"><tr><th className="p-2">Time</th><th className="p-2">Event</th><th className="p-2">Severity</th><th className="p-2">Message</th></tr></thead>
            <tbody>{filteredEvents.map((event) => <tr key={event.id} className="border-t border-zinc-800"><td className="p-2">{new Date(event.timestamp).toLocaleTimeString()}</td><td className="p-2 text-white">{event.event_type}</td><td className="p-2">{event.severity}</td><td className="p-2 text-zinc-300">{event.message}</td></tr>)}</tbody>
          </table>
          {filteredEvents.length === 0 && <p className="p-3 text-sm text-zinc-500">No matching mission events recorded.</p>}
        </div>
      </div>
    </section>



    <section className="grid gap-4 xl:grid-cols-2">
      <div className="rounded border border-zinc-800 bg-zinc-950 p-4">
        <h3 className="text-sm font-semibold uppercase tracking-widest text-zinc-300">Mission export / report</h3>
        <div className="mt-3 flex flex-wrap gap-2"><button onClick={exportMissionJson} disabled={!selectedMissionId} className="rounded border border-zinc-600 px-3 py-2 text-xs uppercase text-white">Export Mission JSON</button><button onClick={generateMissionReport} disabled={!selectedMissionId} className="rounded border border-zinc-600 px-3 py-2 text-xs uppercase text-white">Generate Mission Report</button></div>
        <textarea value={missionJson} onChange={(event) => setMissionJson(event.target.value)} className="mt-3 h-56 w-full rounded border border-zinc-800 bg-black p-3 font-mono text-xs text-zinc-200" placeholder="Export or report JSON appears here." />
        <p className="mt-2 text-xs text-zinc-500">Report status: {report ? `${report.status} / ${report.waypoint_count} waypoints / hardware_upload_enabled=${report.hardware_upload_enabled}` : 'not generated'}</p>
      </div>
      <div className="rounded border border-zinc-800 bg-zinc-950 p-4">
        <h3 className="text-sm font-semibold uppercase tracking-widest text-zinc-300">Mission import panel</h3>
        <p className="mt-2 text-sm text-zinc-400">Import accepts PRAMAAN_X_MISSION_DRAFT_V1 JSON only. Imported missions remain draft-only and are validated after import.</p>
        <textarea value={importJson} onChange={(event) => setImportJson(event.target.value)} className="mt-3 h-56 w-full rounded border border-zinc-800 bg-black p-3 font-mono text-xs text-zinc-200" placeholder="Paste exported mission JSON here." />
        <button onClick={importMissionDraft} className="mt-3 rounded border border-zinc-600 px-3 py-2 text-xs uppercase text-white">Import Draft Mission</button>
        {importMessage && <p className="mt-2 text-xs text-zinc-400">{importMessage}</p>}
      </div>
    </section>

    <section className="grid gap-4 xl:grid-cols-2">
      <div className="rounded border border-zinc-800 bg-zinc-950 p-4"><h3 className="text-sm font-semibold uppercase tracking-widest text-zinc-300">Validation warnings</h3><div className="mt-3 space-y-2 text-sm">{validation?.errors.map((item) => <p key={item} className="rounded border border-red-900/70 bg-red-950/20 p-2 text-red-200">Error: {item}</p>)}{[...localWarnings, ...(validation?.warnings ?? [])].map((item) => <p key={item} className="rounded border border-amber-900/70 bg-amber-950/20 p-2 text-amber-100">Warning: {item}</p>)}</div></div>
      <div className="rounded border border-zinc-800 bg-zinc-950 p-4"><div className="flex items-center justify-between"><h3 className="text-sm font-semibold uppercase tracking-widest text-zinc-300">Geofence panel</h3><button onClick={createDraftGeofence} className="rounded border border-zinc-600 px-3 py-2 text-xs uppercase text-white">Create draft polygon</button></div><div className="mt-3 space-y-2 text-sm text-zinc-400"><p>Status: <span className="text-zinc-100">{activeGeofence ? `${activeGeofence.name} / ${activeGeofence.enabled ? 'enabled draft' : 'disabled draft'}` : 'No draft geofence available'}</span></p><p>Polygon preview points: <span className="text-zinc-100">{geofencePolygon.length}</span></p><p>Geofence is draft-only in Stage 1.6. No hardware enforcement.</p><p className="text-xs text-zinc-500">Selected mission: {selectedMission?.mission_id ?? 'none'}</p></div></div>
    </section>
  </div>;
}
