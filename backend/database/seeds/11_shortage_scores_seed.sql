-- =====================================================
-- AEGISFLOW
-- SHORTAGE SCORES
-- =====================================================

INSERT INTO shortage_scores (
    facility_id,
    medicine_id,
    current_stock,
    daily_consumption_rate,
    lead_time_days,
    safety_stock,
    calculated_score,
    severity
)

SELECT
    facility_id,
    medicine_id,
    available_stock,
    daily_consumption_rate,
    lead_time_days,
    reorder_threshold,
    shortage_score,
    severity
FROM inventory_current;