export type C2ConnectionMode = 'SETUP_MODE' | 'OPS_MONITOR_MODE' | 'PRAMAAN_CONTROL_MODE' | 'FUTURE_SECURE_CONTROL_MODE';
export type MAVLinkBridgeStatus = 'NOT_CONFIGURED' | 'SIMULATION_ONLY' | 'READ_ONLY_READY' | 'CONNECTED_READ_ONLY' | 'ERROR';
export type MissionDraftStatus = 'DRAFT' | 'VALIDATED' | 'INVALID' | 'LOCKED';
export type WaypointAction = 'NAVIGATE' | 'LOITER' | 'CAPTURE_IMAGE' | 'START_RECORDING' | 'STOP_RECORDING' | 'RETURN_POINT';

export interface BridgeStatus { status: MAVLinkBridgeStatus; read_only: boolean; endpoint_count: number; message: string; hardware_commands_enabled: boolean; }
export interface MAVLinkEndpoint { id: number; endpoint_id: string; name: string; host: string; port: number; protocol: string; status: MAVLinkBridgeStatus; read_only: boolean; created_at: string; updated_at: string; }
export interface C2ConnectionConfig { id?: number; mode: C2ConnectionMode; description: string; mission_planner_allowed: boolean; pramaan_commands_allowed: boolean; hardware_commands_enabled: boolean; puf_required: boolean; created_at?: string; updated_at?: string; }

export interface MissionDraft { id: number; mission_id: string; name: string; drone_id: string; vehicle_type: 'QUADCOPTER' | 'FIXED_WING'; status: MissionDraftStatus; default_altitude_m: number; default_speed_mps: number; lost_link_action: string; created_at: string; updated_at: string; }
export interface MissionDraftCreate { name: string; drone_id: string; vehicle_type: 'QUADCOPTER' | 'FIXED_WING'; default_altitude_m: number; default_speed_mps: number; lost_link_action: string; }
export interface MapWaypoint { id: number; mission_id: string; sequence: number; lat: number; lon: number; altitude_m: number; speed_mps: number; action: WaypointAction; loiter_seconds?: number | null; notes?: string | null; }
export interface MapWaypointCreate { lat: number; lon: number; altitude_m?: number; speed_mps?: number; action: WaypointAction; loiter_seconds?: number | null; notes?: string | null; }
export interface MissionRouteSummary { waypoint_count: number; estimated_distance_m: number; max_altitude_m: number; min_altitude_m: number; }
export interface MissionValidation { mission_id: string; status: MissionDraftStatus; valid: boolean; warnings: string[]; errors: string[]; summary: MissionRouteSummary; }
export interface GeofenceDraft { id: number; geofence_id: string; name: string; drone_id: string; enabled: boolean; polygon_json: string; max_altitude_m: number; min_altitude_m: number; created_at: string; updated_at: string; }
export type TelemetrySource = 'MOCK' | 'MAVLINK_READ_ONLY' | 'PLAYBACK';
export type TelemetrySourceStatus = 'ACTIVE' | 'INACTIVE' | 'CONNECTING' | 'ERROR';
export interface TelemetrySourceConfig { id: number; source_type: TelemetrySource; status: TelemetrySourceStatus; name: string; host?: string | null; port?: number | null; protocol: string; read_only: boolean; last_error?: string | null; created_at: string; updated_at: string; }
export interface MissionEvent { id: number; mission_id: string; drone_id: string; event_type: string; severity: string; message: string; timestamp: string; details?: string | null; }
export interface MissionSimulationStatus { mission_id: string; state: 'IDLE' | 'RUNNING' | 'PAUSED' | 'COMPLETED' | 'ERROR'; active_waypoint_index: number; waypoint_count: number; message: string; }
