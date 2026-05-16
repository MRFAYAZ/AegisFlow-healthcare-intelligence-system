INSERT INTO redistribution_recommendations (
    shortage_facility_id,
    donor_facility_id,
    medicine_id,
    recommended_quantity,
    donor_surplus,
    transfer_distance_km,
    redistribution_score,
    recommendation_reason
)
SELECT
    f1.facility_id,
    f2.facility_id,
    m.medicine_id,
    80,
    200,
    7.5,
    91,
    'Nearby surplus inventory available for emergency redistribution'
FROM facilities f1
CROSS JOIN facilities f2
CROSS JOIN medicine_master m
WHERE f1.facility_name = 'Apollo Hospital Chennai'
AND f2.facility_name = 'Fortis Medical Center'
AND m.medicine_name = 'Insulin Injection'
ON CONFLICT DO NOTHING;