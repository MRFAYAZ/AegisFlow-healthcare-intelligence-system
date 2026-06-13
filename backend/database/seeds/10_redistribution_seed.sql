-- =====================================================
-- AEGISFLOW
-- REDISTRIBUTION RECOMMENDATIONS
-- =====================================================

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
    sf.facility_id,
    df.facility_id,
    m.medicine_id,
    100,
    250,
    8.5,
    95.0,
    'Nearest facility with sufficient Salbutamol inventory'
FROM facilities sf
JOIN facilities df
ON sf.facility_id <> df.facility_id
JOIN medicine_master m
ON m.medicine_code = 'SAL100'
WHERE sf.facility_name = 'Apollo Pharmacy'
AND df.facility_name = 'Apollo Hospital Chennai'

UNION ALL

SELECT
    sf.facility_id,
    df.facility_id,
    m.medicine_id,
    75,
    180,
    12.4,
    91.0,
    'Insulin shortage mitigation recommendation'
FROM facilities sf
JOIN facilities df
ON sf.facility_id <> df.facility_id
JOIN medicine_master m
ON m.medicine_code = 'INS100'
WHERE sf.facility_name = 'Government General Hospital'
AND df.facility_name = 'SIMS Hospital'

UNION ALL

SELECT
    sf.facility_id,
    df.facility_id,
    m.medicine_id,
    50,
    300,
    5.2,
    87.0,
    'ORS redistribution due to local demand spike'
FROM facilities sf
JOIN facilities df
ON sf.facility_id <> df.facility_id
JOIN medicine_master m
ON m.medicine_code = 'ORS001'
WHERE sf.facility_name = 'MedPlus Pharmacy'
AND df.facility_name = 'Apollo Hospital Chennai';