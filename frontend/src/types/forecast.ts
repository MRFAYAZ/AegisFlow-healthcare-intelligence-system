export interface StockoutForecast {
  inventory_id: string
  facility_id: string
  facility_name: string
  medicine_id: string
  medicine_name: string
  available_stock: number
  reserved_stock: number
  batch_verified_usable_stock: number
  expired_batch_quantity: number
  batch_traceability: "VERIFIED" | "EXPIRED_ONLY" | "UNVERIFIED"
  eligible_batch_count: number
  usable_stock: number
  daily_consumption_rate: number
  lead_time_days: number
  safety_stock_days: number
  projected_stockout_days: number | null
  risk_score: number | null
  risk_level: "CRITICAL" | "HIGH" | "WARNING" | "SAFE" | "INSUFFICIENT_DATA"
  recommended_action: "SOURCE_NETWORK" | "REPLENISH" | "REVIEW_REPLENISHMENT" | "MONITOR" | "REVIEW_CONSUMPTION"
  explanation: string
}
