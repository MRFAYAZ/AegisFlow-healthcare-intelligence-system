export interface InventoryRecord {
  inventory_id: string
  facility_name: string
  medicine_name: string
  total_stock: number
  available_stock: number
  reserved_stock: number
  shortage_score: number
  severity: "SAFE" | "WARNING" | "CRITICAL" | "EMERGENCY"
}
