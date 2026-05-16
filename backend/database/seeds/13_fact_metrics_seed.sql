INSERT INTO dim_date (
    date_id,
    day,
    month,
    quarter,
    year,
    weekday,
    is_weekend,
    season
)
VALUES
(
    CURRENT_DATE,
    EXTRACT(DAY FROM CURRENT_DATE),
    EXTRACT(MONTH FROM CURRENT_DATE),
    EXTRACT(QUARTER FROM CURRENT_DATE),
    EXTRACT(YEAR FROM CURRENT_DATE),
    TO_CHAR(CURRENT_DATE, 'Day'),
    FALSE,
    'Summer'
)
ON CONFLICT DO NOTHING;

INSERT INTO fact_inventory_metrics (
    date_id,
    facility_id,
    medicine_id,
    shortage_score,
    available_stock,
    transfer_requests_count,
    emergency_count
)
SELECT
    CURRENT_DATE,
    f.facility_id,
    m.medicine_id,
    112,
    15,
    2,
    1
FROM facilities f
CROSS JOIN medicine_master m
WHERE f.facility_name = 'Apollo Hospital Chennai'
AND m.medicine_name = 'Insulin Injection'
ON CONFLICT DO NOTHING;

INSERT INTO fact_inventory_metrics (
    date_id,
    facility_id,
    medicine_id,
    shortage_score,
    available_stock,
    transfer_requests_count,
    emergency_count
)
SELECT
    CURRENT_DATE,
    f.facility_id,
    m.medicine_id,
    86,
    40,
    1,
    0
FROM facilities f
CROSS JOIN medicine_master m
WHERE f.facility_name = 'WellCare Pharmacy'
AND m.medicine_name = 'Paracetamol 500mg'
ON CONFLICT DO NOTHING;

INSERT INTO fact_inventory_metrics (
    date_id,
    facility_id,
    medicine_id,
    shortage_score,
    available_stock,
    transfer_requests_count,
    emergency_count
)
SELECT
    CURRENT_DATE,
    f.facility_id,
    m.medicine_id,
    52,
    75,
    0,
    0
FROM facilities f
CROSS JOIN medicine_master m
WHERE f.facility_name = 'MedPlus Pharmacy Chennai'
AND m.medicine_name = 'Salbutamol Inhaler'
ON CONFLICT DO NOTHING;