export type Role = 'system_admin' | 'hospital_admin' | 'pharmacist' | 'shop_owner' | 'emergency_operator' | 'dispatcher' | 'supplier_manager'

export type { Transfer } from './transfer'

export interface User {
  id: string
  name: string
  email: string
  role: string
  profile?: string
  profile_access?: string[]
  facility?: string
  avatar?: string
}

export interface Medicine {
  id: string
  name: string
  details: string
  category: string
  stock: number
  maxStock: number
  expiry: string
  status: 'adequate' | 'warning' | 'critical' | 'emergency'
  unit: string
}




export interface Shortage {
  id: string
  medicine: string
  facility: string
  severity: 'emergency' | 'critical' | 'warning'
  stock: string
  daysLeft: number
  nearestSource: string
}

export interface ShortageRiskAssessment {
  inventory_id: string
  facility_id: string
  medicine_id: string
  facility_name: string
  medicine_name: string
  current_stock: number
  reserved_stock: number
  usable_stock: number
  daily_consumption: number
  safety_stock_days: number
  safety_stock_units: number
  lead_time_days: number
  projected_stockout_days: number | null
  risk_score: number
  risk_level: 'SAFE' | 'WARNING' | 'HIGH' | 'CRITICAL'
  recommended_action: 'CONTINUE_MONITORING' | 'PREPARE_REPLENISHMENT' | 'INITIATE_PROCUREMENT' | 'SOURCE_NETWORK'
}

export interface ReplenishmentRequirement {
  requirement_id: string | null
  inventory_id: string
  facility_id: string
  medicine_id: string
  facility_name: string
  medicine_name: string
  requested_quantity: number
  priority: string
  projected_stockout_days: number | null
  required_by_days: number | null
  reason: string
  status: string
}

export interface SupplierRecommendation {
  supplier_facility_id: string
  supplier_name: string
  medicine_id: string
  medicine_name: string
  available_quantity: number
  requested_quantity: number
  lead_time_days: number
  distance_km: number | null
  readiness_score: number
  reliability_status: string
  recommendation_reason: string
}

export interface SupplyRequest {
  request_id: string
  requirement_id: string
  supplier_facility_id: string
  supplier_name: string
  target_facility_id: string
  target_facility_name: string
  medicine_id: string
  medicine_name: string
  requested_quantity: number
  accepted_quantity: number
  lead_time_days: number
  recommendation_score: number
  status: string
  created_at: string
}

export interface KPI {
  label: string
  value: string | number
  sub: string
  trend?: 'up' | 'down' | 'neutral'
  color: 'blue' | 'green' | 'red' | 'orange'
}

export interface Alert {
  id: string
  type: 'emergency' | 'critical' | 'warning' | 'resolved'
  message: string
  time: string
}

export interface Facility {
  id: string
  name: string
  type: 'hospital' | 'pharmacy' | 'clinic'
  lat: number
  lng: number
  status: 'stocked' | 'low' | 'critical' | 'emergency'
  address: string
}
