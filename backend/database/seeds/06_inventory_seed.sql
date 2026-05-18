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
    severity,
    last_restocked_at
)
SELECT
    f.facility_id,
    m.medicine_id,
    500,
    480,
    20,
    100,
    150,
    25,
    5,
    15,
    'SAFE',
    CURRENT_TIMESTAMP
FROM facilities f
CROSS JOIN medicine_master m
WHERE f.facility_type = 'HOSPITAL'
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
    severity,
    last_restocked_at
)
SELECT
    f.facility_id,
    m.medicine_id,
    40,
    35,
    5,
    50,
    80,
    18,
    6,
    85,
    'EMERGENCY',
    CURRENT_TIMESTAMP
FROM facilities f
CROSS JOIN medicine_master m
WHERE f.facility_name = 'Apollo Hospital Chennai'
AND m.medicine_name = 'Insulin Injection'
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
    severity,
    last_restocked_at
)
SELECT
    f.facility_id,
    m.medicine_id,
    300,
    250,
    50,
    100,
    150,
    20,
    5,
    20,
    'SAFE',
    CURRENT_TIMESTAMP
FROM facilities f
CROSS JOIN medicine_master m
WHERE f.facility_name = 'Fortis Medical Center'
AND m.medicine_name = 'Insulin Injection'
ON CONFLICT DO NOTHING;