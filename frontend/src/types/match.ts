export interface MatchScoreBreakdown {
  distance_score: number
  inventory_score: number
  donor_health_score: number
  distance_weight: number
  inventory_weight: number
  donor_health_weight: number
}

export interface EmergencyMatch {
  rank: number
  facility_id: string
  facility_name: string
  facility_type: string
  available_quantity: number
  transferable_quantity: number
  suggested_quantity: number
  distance_km: number
  ranking_score: number
  score_breakdown: MatchScoreBreakdown
  batch_traceability: string
  eligible_batch_count: number
  nearest_expiry_date: string
  recommendation_reason: string
}
