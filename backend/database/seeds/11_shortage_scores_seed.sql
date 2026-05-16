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
    f.facility_id,
    m.medicine_id,
    15,
    18,
    7,
    30,
    112,
    'EMERGENCY'
FROM facilities f
CROSS JOIN medicine_master m
WHERE f.facility_name = 'Apollo Hospital Chennai'
AND m.medicine_name = 'Insulin Injection'
ON CONFLICT DO NOTHING;

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
    f.facility_id,
    m.medicine_id,
    40,
    20,
    5,
    35,
    86,
    'CRITICAL'
FROM facilities f
CROSS JOIN medicine_master m
WHERE f.facility_name = 'WellCare Pharmacy'
AND m.medicine_name = 'Paracetamol 500mg'
ON CONFLICT DO NOTHING;

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
    f.facility_id,
    m.medicine_id,
    75,
    14,
    4,
    40,
    52,
    'WARNING'
FROM facilities f
CROSS JOIN medicine_master m
WHERE f.facility_name = 'MedPlus Pharmacy Chennai'
AND m.medicine_name = 'Salbutamol Inhaler'
ON CONFLICT DO NOTHING;