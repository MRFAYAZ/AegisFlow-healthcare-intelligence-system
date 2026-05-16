-- =====================================================
-- AegisFlow Indexing Strategy
-- =====================================================

CREATE INDEX idx_users_email
ON users(email);

-- =====================================================

CREATE INDEX idx_facility_type
ON facilities(facility_type);

-- =====================================================

CREATE INDEX idx_inventory_facility_medicine
ON inventory_current(facility_id, medicine_id);

-- =====================================================

CREATE INDEX idx_inventory_batches_expiry
ON inventory_batches(expiry_date);

-- =====================================================

CREATE INDEX idx_shortage_scores
ON shortage_scores(calculated_score);

-- =====================================================

CREATE INDEX idx_alert_severity
ON alert_events(severity);

-- =====================================================

CREATE INDEX idx_transfer_status
ON transfer_requests(transfer_status);

-- =====================================================

CREATE INDEX idx_purchase_timestamp
ON purchase_transactions(purchased_at);

-- =====================================================

CREATE INDEX idx_outbreak_city
ON outbreak_signals(city);

-- =====================================================

CREATE INDEX idx_inventory_snapshot_timestamp
ON inventory_snapshots(snapshot_timestamp);

-- =====================================================
-- GEO INDEX
-- =====================================================

CREATE INDEX idx_geo_location
ON locations
USING GIST(geo_point);

-- =====================================================
-- JSONB EVENT INDEX
-- =====================================================

CREATE INDEX idx_event_payload
ON event_log
USING GIN(event_payload);