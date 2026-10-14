export type TransferStatus =
  | "PENDING"
  | "APPROVED"
  | "REJECTED"
  | "IN_TRANSIT"
  | "COMPLETED"
  | "CANCELLED"

export type DispatchStatus =
  | "ASSIGNED"
  | "IN_TRANSIT"
  | "DELIVERED"
  | "FAILED"
  | "CANCELLED"

export interface TransferRecord {
  transfer_id: string
  emergency_case_id: string | null
  from_facility_id: string
  from_facility_name: string
  to_facility_id: string
  to_facility_name: string
  medicine_id: string
  medicine_name: string
  requested_quantity: number
  approved_quantity: number | null
  transfer_status: TransferStatus
  cascade_safe: boolean
  match_score: number | null
  transfer_distance_km: number | null
  recommendation_reason: string | null
  requested_at: string
  approved_at?: string | null
  completed_at: string | null
  rejection_reason?: string | null
  dispatch_id?: string | null
  dispatch_status?: DispatchStatus | null
  transport_type?: string | null
  vehicle_reference?: string | null
  dispatched_at?: string | null
  delivered_at?: string | null
}
