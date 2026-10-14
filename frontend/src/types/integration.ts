export interface IntegrationSource {
  source_id: string
  source_name: string
  system_type: string
  facility_id: string
  is_active: boolean
  last_snapshot_at: string | null
}

export interface IntegrationSourceCreated extends IntegrationSource {
  integration_key: string
  credential_note: string
}

export interface IntegrationMedicineMapping {
  mapping_id: string
  source_id: string
  external_medicine_code: string
  medicine_id: string
  is_active: boolean
}

export interface IntegrationFacility {
  facility_id: string
  facility_name: string
  facility_type: string
  city?: string
  state?: string
}

export interface IntegrationMedicine {
  medicine_id: string
  medicine_code: string
  medicine_name: string
  generic_name?: string
}


export interface IntegrationSnapshotEvent {
  integration_event_id: string
  source_id: string
  external_event_id: string
  source_timestamp: string
  status: string
  records_processed: number
  received_at: string
  processed_at: string
}
