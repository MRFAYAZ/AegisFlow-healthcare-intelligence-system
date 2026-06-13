-- =====================================================
-- AEGISFLOW
-- PURCHASE TRANSACTIONS
-- =====================================================

INSERT INTO purchase_transactions (
    facility_id,
    medicine_id,
    customer_name,
    customer_phone,
    quantity,
    unit_price,
    total_amount,
    purchase_status,
    stock_reduced,
    purchased_at
)

SELECT
    f.facility_id,
    m.medicine_id,
    'Rahul Sharma',
    '9876543210',
    5,
    m.unit_price,
    5 * m.unit_price,
    'COMPLETED'::purchase_status_enum,
    TRUE,
    NOW() - INTERVAL '15 days'
FROM facilities f
JOIN medicine_master m
ON m.medicine_code = 'PCM500'
WHERE f.facility_name = 'Apollo Pharmacy'

UNION ALL

SELECT
    f.facility_id,
    m.medicine_id,
    'Priya Menon',
    '9876543211',
    3,
    m.unit_price,
    3 * m.unit_price,
    'COMPLETED'::purchase_status_enum,
    TRUE,
    NOW() - INTERVAL '14 days'
FROM facilities f
JOIN medicine_master m
ON m.medicine_code = 'DOLO650'
WHERE f.facility_name = 'Apollo Pharmacy'

UNION ALL

SELECT
    f.facility_id,
    m.medicine_id,
    'Arun Kumar',
    '9876543212',
    2,
    m.unit_price,
    2 * m.unit_price,
    'COMPLETED'::purchase_status_enum,
    TRUE,
    NOW() - INTERVAL '13 days'
FROM facilities f
JOIN medicine_master m
ON m.medicine_code = 'AMX500'
WHERE f.facility_name = 'MedPlus Pharmacy'

UNION ALL

SELECT
    f.facility_id,
    m.medicine_id,
    'Sneha Reddy',
    '9876543213',
    4,
    m.unit_price,
    4 * m.unit_price,
    'COMPLETED'::purchase_status_enum,
    TRUE,
    NOW() - INTERVAL '12 days'
FROM facilities f
JOIN medicine_master m
ON m.medicine_code = 'AZI250'
WHERE f.facility_name = 'MedPlus Pharmacy'

UNION ALL

SELECT
    f.facility_id,
    m.medicine_id,
    'Ramesh Kumar',
    '9876543214',
    2,
    m.unit_price,
    2 * m.unit_price,
    'COMPLETED'::purchase_status_enum,
    TRUE,
    NOW() - INTERVAL '11 days'
FROM facilities f
JOIN medicine_master m
ON m.medicine_code = 'MET500'
WHERE f.facility_name = 'Apollo Pharmacy'

UNION ALL

SELECT
    f.facility_id,
    m.medicine_id,
    'Lakshmi Devi',
    '9876543215',
    1,
    m.unit_price,
    1 * m.unit_price,
    'COMPLETED'::purchase_status_enum,
    TRUE,
    NOW() - INTERVAL '10 days'
FROM facilities f
JOIN medicine_master m
ON m.medicine_code = 'INS100'
WHERE f.facility_name = 'Government General Hospital'

UNION ALL

SELECT
    f.facility_id,
    m.medicine_id,
    'Vikram Rao',
    '9876543216',
    8,
    m.unit_price,
    8 * m.unit_price,
    'COMPLETED'::purchase_status_enum,
    TRUE,
    NOW() - INTERVAL '9 days'
FROM facilities f
JOIN medicine_master m
ON m.medicine_code = 'ORS001'
WHERE f.facility_name = 'MedPlus Pharmacy'

UNION ALL

SELECT
    f.facility_id,
    m.medicine_id,
    'Anjali Nair',
    '9876543217',
    2,
    m.unit_price,
    2 * m.unit_price,
    'COMPLETED'::purchase_status_enum,
    TRUE,
    NOW() - INTERVAL '8 days'
FROM facilities f
JOIN medicine_master m
ON m.medicine_code = 'SAL100'
WHERE f.facility_name = 'Apollo Pharmacy'

UNION ALL

SELECT
    f.facility_id,
    m.medicine_id,
    'Kiran Patel',
    '9876543218',
    5,
    m.unit_price,
    5 * m.unit_price,
    'COMPLETED'::purchase_status_enum,
    TRUE,
    NOW() - INTERVAL '7 days'
FROM facilities f
JOIN medicine_master m
ON m.medicine_code = 'ATOR10'
WHERE f.facility_name = 'Apollo Pharmacy'

UNION ALL

SELECT
    f.facility_id,
    m.medicine_id,
    'Deepak Verma',
    '9876543219',
    3,
    m.unit_price,
    3 * m.unit_price,
    'COMPLETED'::purchase_status_enum ,
    TRUE,
    NOW() - INTERVAL '6 days'
FROM facilities f
JOIN medicine_master m
ON m.medicine_code = 'CEF200'
WHERE f.facility_name = 'MedPlus Pharmacy';