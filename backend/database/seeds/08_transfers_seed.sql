-- =====================================================
-- AEGISFLOW
-- TRANSFER REQUESTS
-- =====================================================

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
    requested_by,
    approved_by,
    requested_at,
    approved_at,
    completed_at
)

-- =====================================================
-- INSULIN TRANSFER
-- =====================================================

SELECT
    donor.facility_id,
    receiver.facility_id,
    med.medicine_id,

    100,
    75,

    'APPROVED'::transfer_status_enum,

    TRUE,

    94.50,

    12.40,

    requester.user_id,

    approver.user_id,

    NOW() - INTERVAL '2 days',

    NOW() - INTERVAL '1 day',

    NULL::TIMESTAMP

FROM facilities donor
JOIN facilities receiver
    ON donor.facility_id <> receiver.facility_id

JOIN medicine_master med
    ON med.medicine_code = 'INS100'

JOIN users requester
    ON requester.role = 'EMERGENCY_OPERATOR'

JOIN users approver
    ON approver.role = 'SYSTEM_ADMIN'

WHERE donor.facility_name = 'SIMS Hospital'
AND receiver.facility_name = 'Government General Hospital'

UNION ALL

-- =====================================================
-- SALBUTAMOL TRANSFER
-- =====================================================

SELECT
    donor.facility_id,
    receiver.facility_id,
    med.medicine_id,

    150,
    120,

    'IN_TRANSIT'::transfer_status_enum,

    TRUE,

    96.20,

    8.50,

    requester.user_id,

    approver.user_id,

    NOW() - INTERVAL '12 hours',

    NOW() - INTERVAL '8 hours',

    NULL::TIMESTAMP

FROM facilities donor
JOIN facilities receiver
    ON donor.facility_id <> receiver.facility_id

JOIN medicine_master med
    ON med.medicine_code = 'SAL100'

JOIN users requester
    ON requester.role = 'EMERGENCY_OPERATOR'

JOIN users approver
    ON approver.role = 'SYSTEM_ADMIN'

WHERE donor.facility_name = 'Apollo Hospital Chennai'
AND receiver.facility_name = 'Apollo Pharmacy'

UNION ALL

-- =====================================================
-- ORS TRANSFER
-- =====================================================

SELECT
    donor.facility_id,
    receiver.facility_id,
    med.medicine_id,

    80,
    80,

    'COMPLETED'::transfer_status_enum,

    TRUE,

    88.00,

    5.20,

    requester.user_id,

    approver.user_id,

    NOW() - INTERVAL '5 days',

    NOW() - INTERVAL '4 days',

    NOW() - INTERVAL '3 days'

FROM facilities donor
JOIN facilities receiver
    ON donor.facility_id <> receiver.facility_id

JOIN medicine_master med
    ON med.medicine_code = 'ORS001'

JOIN users requester
    ON requester.role = 'EMERGENCY_OPERATOR'

JOIN users approver
    ON approver.role = 'SYSTEM_ADMIN'

WHERE donor.facility_name = 'Apollo Hospital Chennai'
AND receiver.facility_name = 'MedPlus Pharmacy'

UNION ALL

-- =====================================================
-- PARACETAMOL TRANSFER
-- =====================================================

SELECT
    donor.facility_id,
    receiver.facility_id,
    med.medicine_id,

    200,
    NULL::INTEGER,

    'PENDING'::transfer_status_enum,

    TRUE,

    82.00,

    10.00,

    requester.user_id,

    approver.user_id,

    NOW() - INTERVAL '1 hour',

    NULL::TIMESTAMP,

    NULL::TIMESTAMP

FROM facilities donor
JOIN facilities receiver
    ON donor.facility_id <> receiver.facility_id

JOIN medicine_master med
    ON med.medicine_code = 'PCM500'

JOIN users requester
    ON requester.role = 'EMERGENCY_OPERATOR'

JOIN users approver
    ON approver.role = 'SYSTEM_ADMIN'

WHERE donor.facility_name = 'Aster Medical Supplier'
AND receiver.facility_name = 'Government General Hospital';