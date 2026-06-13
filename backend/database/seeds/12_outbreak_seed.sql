-- =====================================================
-- AEGISFLOW
-- OUTBREAK SIGNALS
-- =====================================================

INSERT INTO outbreak_signals (
    city,
    medicine_id,
    baseline_consumption,
    current_consumption,
    spike_percentage,
    affected_facilities,
    confidence_score,
    outbreak_status
)

SELECT
    'Chennai',
    medicine_id,
    150,
    420,
    180.00,
    4,
    92.50,
    'CONFIRMED'
FROM medicine_master
WHERE medicine_code='ORS001'

UNION ALL

SELECT
    'Chennai',
    medicine_id,
    200,
    510,
    155.00,
    3,
    89.00,
    'UNDER_REVIEW'
FROM medicine_master
WHERE medicine_code='PCM500'

UNION ALL

SELECT
    'OMR',
    medicine_id,
    80,
    250,
    212.00,
    2,
    95.00,
    'CONFIRMED'
FROM medicine_master
WHERE medicine_code='SAL100'

UNION ALL

SELECT
    'Tambaram',
    medicine_id,
    70,
    180,
    157.00,
    2,
    85.00,
    'DETECTED'
FROM medicine_master
WHERE medicine_code='AZI250';