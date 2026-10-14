export type EmergencySeverity =
  | "WARNING"
  | "CRITICAL"
  | "EMERGENCY"

export type EmergencyStatus =
  | "ACTIVE"
  | "MATCHING"
  | "RESOLVED"

export interface Emergency {

    emergency_case_id: string

    facility_id: string
    facility_name: string

    facility_latitude?: number

    facility_longitude?: number

    donor_latitude?: number

    donor_longitude?: number
    medicine_id: string
    medicine_name: string

    shortage_score: number

    severity: string

    emergency_radius_km: number

    required_quantity: number

    available_quantity: number

    emergency_status: string

    triggered_at: string

    resolved_at: string | null

    transfer_id: string | null

    donor_facility: string | null

    transfer_status: string | null

    approved_quantity: number | null

    match_score: number | null

    transfer_distance_km: number | null

    cascade_safe: boolean | null

    estimated_eta_minutes: number | null

    ai_reason: string | null

    alternative_donors: number | null

    inventory_score?: number | null
    distance_score?: number | null
    risk_score?: number | null
    hospital_rating?: number | null
    patients_at_risk?: number | null
    delivery_confidence?: number | null
    incident_owner?: string | null
    assigned_dispatcher?: string | null
    incident_age_minutes?: number | null
    sla_remaining_minutes?: number | null

    selected_batch_number?: string | null
    earliest_expiry_date?: string | null
    cold_chain_required?: boolean
    cold_chain_capable?: boolean
    safety_status?: string
    safety_reason?: string | null
    batch_allocations?: Array<{ batch_number: string; quantity: number; expiry_date: string }>
}