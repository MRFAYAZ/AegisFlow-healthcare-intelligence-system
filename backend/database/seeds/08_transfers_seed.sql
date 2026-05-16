INSERT INTO transfer_requests (
    from_facility_id,
    to_facility_id,
    medicine_id,
    requested_quantity,
    approved_quantity,
    transfer_status,
    cascade_safe,
    match_score,
    transfer_distance_km,
    requested_at
)
SELECT
    donor.facility_id,
    receiver.facility_id,
    m.medicine_id,
    80,
    75,
    'APPROVED',
    TRUE,
    94,
    7.5,
    CURRENT_TIMESTAMP
FROM facilities donor
CROSS JOIN facilities receiver
CROSS JOIN medicine_master m
WHERE donor.facility_name = 'Fortis Medical Center'
AND receiver.facility_name = 'Apollo Hospital Chennai'
AND m.medicine_name = 'Insulin Injection'
ON CONFLICT DO NOTHING;