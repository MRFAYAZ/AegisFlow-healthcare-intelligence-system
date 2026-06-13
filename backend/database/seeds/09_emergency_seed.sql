-- =====================================================
-- AEGISFLOW
-- EMERGENCY CASES
-- =====================================================

INSERT INTO emergency_cases (
    facility_id,
    medicine_id,
    shortage_score,
    severity,
    emergency_radius_km,
    required_quantity,
    available_quantity,
    emergency_status,
    triggered_by,
    triggered_at
)

SELECT
    f.facility_id,
    m.medicine_id,
    96.00,
    'EMERGENCY'::severity_enum,
    25,
    150,
    4,
    'ACTIVE',
    u.user_id,
    NOW() - INTERVAL '6 hours'
FROM facilities f
JOIN medicine_master m
ON m.medicine_code = 'SAL100'
JOIN users u
ON u.role = 'EMERGENCY_OPERATOR'
WHERE f.facility_name = 'Apollo Pharmacy'

UNION ALL

SELECT
    f.facility_id,
    m.medicine_id,
    92.00,
    'CRITICAL'::severity_enum,
    20,
    100,
    8,
    'ACTIVE',
    u.user_id,
    NOW() - INTERVAL '1 day'
FROM facilities f
JOIN medicine_master m
ON m.medicine_code = 'INS100'
JOIN users u
ON u.role = 'EMERGENCY_OPERATOR'
WHERE f.facility_name = 'Government General Hospital'

UNION ALL

SELECT
    f.facility_id,
    m.medicine_id,
    78.00,
    'WARNING'::severity_enum,
    15,
    75,
    25,
    'MATCHING',
    u.user_id,
    NOW() - INTERVAL '12 hours'
FROM facilities f
JOIN medicine_master m
ON m.medicine_code = 'ORS001'
JOIN users u
ON u.role = 'EMERGENCY_OPERATOR'
WHERE f.facility_name = 'MedPlus Pharmacy';