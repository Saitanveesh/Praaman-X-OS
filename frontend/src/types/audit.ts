export interface AuditLog { id: number; timestamp: string; operator_id: string; drone_id: string; event_type: string; command_id?: string; decision: string; reason: string; }
