export type CommandType = 'READ_STATUS' | 'START_LOGGING' | 'STOP_LOGGING' | 'SIMULATE_RTL' | 'SIMULATE_LAND';
export interface Command { command_id: string; drone_id: string; operator_id: string; command_type: CommandType; status: string; decision: string; reason: string; ack_message?: string; created_at: string; acknowledged_at?: string; }
