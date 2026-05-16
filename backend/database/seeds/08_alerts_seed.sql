INSERT INTO alert_events (
    facility_id,
    medicine_id,
    alert_type,
    severity,
    alert_message,
    alert_status
)
SELECT
    f.facility_id,
    m.medicine_id,
    'SHORTAGE_ALERT',
    'CRITICAL',
    'Critical insulin shortage detected at Apollo Hospital Chennai',
    'ACTIVE'
FROM facilities f
CROSS JOIN medicine_master m
WHERE f.facility_name = 'Apollo Hospital Chennai'
AND m.medicine_name = 'Insulin Injection'
ON CONFLICT DO NOTHING;