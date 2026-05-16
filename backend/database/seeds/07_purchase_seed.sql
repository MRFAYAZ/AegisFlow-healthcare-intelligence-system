INSERT INTO purchase_transactions (
    facility_id,
    medicine_id,
    customer_name,
    customer_phone,
    quantity,
    unit_price,
    total_amount,
    purchase_status,
    stock_reduced
)
SELECT
    f.facility_id,
    m.medicine_id,
    'Rahul Verma',
    '9123456780',
    5,
    450.00,
    2250.00,
    'COMPLETED',
    TRUE
FROM facilities f
CROSS JOIN medicine_master m
WHERE f.facility_name = 'MedPlus Pharmacy Chennai'
AND m.medicine_name = 'Insulin Injection'
ON CONFLICT DO NOTHING;

INSERT INTO purchase_transactions (
    facility_id,
    medicine_id,
    customer_name,
    customer_phone,
    quantity,
    unit_price,
    total_amount,
    purchase_status,
    stock_reduced
)
SELECT
    f.facility_id,
    m.medicine_id,
    'Sneha Iyer',
    '9234567890',
    10,
    3.50,
    35.00,
    'COMPLETED',
    TRUE
FROM facilities f
CROSS JOIN medicine_master m
WHERE f.facility_name = 'WellCare Pharmacy'
AND m.medicine_name = 'Dolo 650'
ON CONFLICT DO NOTHING;