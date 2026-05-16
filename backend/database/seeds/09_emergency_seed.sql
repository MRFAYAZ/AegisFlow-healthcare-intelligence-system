INSERT INTO emergency_cases (
    facility_id,
    medicine_id,
    shortage_score,
    severity,
    emergency_radius_km,
    required_quantity,
    available_quantity,
    emergency_status
)
SELECT
    f.facility_id,
    m.medicine_id,
    115,
    'EMERGENCY',
    10,
    120,
    15,
    'ACTIVE'
FROM facilities f
CROSS JOIN medicine_master m
WHERE f.facility_name = 'Apollo Hospital Chennai'
AND m.medicine_name = 'Insulin Injection'
ON CONFLICT DO NOTHING;