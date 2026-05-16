INSERT INTO inventory_current (
    facility_id,
    medicine_id,
    total_stock,
    available_stock,
    reserved_stock,
    minimum_threshold,
    reorder_threshold,
    daily_consumption_rate,
    lead_time_days,
    shortage_score,
    severity
)
SELECT
    f.facility_id,
    m.medicine_id,
    500,
    450,
    20,
    100,
    150,
    25,
    5,
    30,
    'SAFE'
FROM facilities f
CROSS JOIN medicine_master m
WHERE f.facility_type = 'HOSPITAL'
LIMIT 10
ON CONFLICT DO NOTHING;

INSERT INTO inventory_current (
    facility_id,
    medicine_id,
    total_stock,
    available_stock,
    reserved_stock,
    minimum_threshold,
    reorder_threshold,
    daily_consumption_rate,
    lead_time_days,
    shortage_score,
    severity
)
SELECT
    f.facility_id,
    m.medicine_id,
    40,
    15,
    5,
    50,
    80,
    18,
    6,
    92,
    'CRITICAL'
FROM facilities f
CROSS JOIN medicine_master m
WHERE f.facility_name = 'Apollo Hospital Chennai'
AND m.medicine_name = 'Insulin Injection'
ON CONFLICT DO NOTHING;