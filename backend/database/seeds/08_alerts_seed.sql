-- =====================================================
-- AEGISFLOW
-- ALERT EVENTS
-- =====================================================

INSERT INTO alert_events (
    facility_id,
    medicine_id,
    alert_type,
    severity,
    alert_message,
    alert_status,
    triggered_at
)

SELECT
    f.facility_id,
    m.medicine_id,
    'LOW_STOCK',
    'WARNING'::severity_enum,
    'ORS stock approaching threshold',
    'ACTIVE'::alert_status_enum,
    NOW() - INTERVAL '2 days'
FROM facilities f
JOIN medicine_master m
ON m.medicine_code = 'ORS001'
WHERE f.facility_name = 'MedPlus Pharmacy'

UNION ALL

SELECT
    f.facility_id,
    m.medicine_id,
    'CRITICAL_SHORTAGE',
    'CRITICAL'::severity_enum,
    'Insulin shortage detected',
    'ACTIVE'::alert_status_enum,
    NOW() - INTERVAL '1 day'
FROM facilities f
JOIN medicine_master m
ON m.medicine_code = 'INS100'
WHERE f.facility_name = 'Government General Hospital'

UNION ALL

SELECT
    f.facility_id,
    m.medicine_id,
    'EMERGENCY_SHORTAGE',
    'EMERGENCY'::severity_enum,
    'Salbutamol stock critically exhausted',
    'ACTIVE'::alert_status_enum,
    NOW() - INTERVAL '6 hours'
FROM facilities f
JOIN medicine_master m
ON m.medicine_code = 'SAL100'
WHERE f.facility_name = 'Apollo Pharmacy'

UNION ALL

SELECT
    f.facility_id,
    m.medicine_id,
    'HIGH_CONSUMPTION',
    'WARNING'::severity_enum,
    'Unexpected ORS demand spike',
    'ACTIVE'::alert_status_enum,
    NOW() - INTERVAL '12 hours'
FROM facilities f
JOIN medicine_master m
ON m.medicine_code = 'ORS001'
WHERE f.facility_name = 'Apollo Pharmacy'

UNION ALL

SELECT
    f.facility_id,
    m.medicine_id,
    'RESTOCK_REQUIRED',
    'WARNING'::severity_enum,
    'Metformin reorder recommended',
    'ACTIVE'::alert_status_enum,
    NOW() - INTERVAL '3 hours'
FROM facilities f
JOIN medicine_master m
ON m.medicine_code = 'MET500'
WHERE f.facility_name = 'SIMS Hospital';