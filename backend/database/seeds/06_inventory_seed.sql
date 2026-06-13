-- =====================================================
-- AEGISFLOW
-- INVENTORY CURRENT SEED
-- =====================================================

INSERT INTO inventory_current (
    facility_id,
    medicine_id,
    total_stock,
    available_stock,
    reserved_stock,
    minimum_threshold,
    reorder_threshold,
    daily_consumption_rate,
    lead_time_days,
    shortage_score,
    severity,
    last_restocked_at
)

SELECT

    f.facility_id,

    m.medicine_id,

    CASE
        WHEN m.medicine_code = 'INS100' THEN 80
        WHEN m.medicine_code = 'SAL100' THEN 60
        ELSE 500
    END AS total_stock,

    CASE
        WHEN f.facility_name = 'Government General Hospital'
             AND m.medicine_code = 'INS100'
             THEN 8

        WHEN f.facility_name = 'Apollo Pharmacy'
             AND m.medicine_code = 'SAL100'
             THEN 4

        WHEN f.facility_name = 'MedPlus Pharmacy'
             AND m.medicine_code = 'ORS001'
             THEN 25

        ELSE
             FLOOR(
                 RANDOM() * 300 + 150
             )::INTEGER
    END AS available_stock,

    FLOOR(
        RANDOM() * 30
    )::INTEGER AS reserved_stock,

    50 AS minimum_threshold,

    100 AS reorder_threshold,

    ROUND(
        (RANDOM() * 20 + 5)::NUMERIC,
        2
    ) AS daily_consumption_rate,

    FLOOR(
        RANDOM() * 10 + 3
    )::INTEGER AS lead_time_days,

    CASE

        WHEN f.facility_name = 'Government General Hospital'
             AND m.medicine_code = 'INS100'
             THEN 92

        WHEN f.facility_name = 'Apollo Pharmacy'
             AND m.medicine_code = 'SAL100'
             THEN 96

        WHEN f.facility_name = 'MedPlus Pharmacy'
             AND m.medicine_code = 'ORS001'
             THEN 78

        ELSE
             ROUND(
                 (RANDOM() * 50)::NUMERIC,
                 2
             )
    END AS shortage_score,

    CASE

        WHEN f.facility_name = 'Apollo Pharmacy'
             AND m.medicine_code = 'SAL100'
             THEN 'EMERGENCY'

        WHEN f.facility_name = 'Government General Hospital'
             AND m.medicine_code = 'INS100'
             THEN 'CRITICAL'

        WHEN f.facility_name = 'MedPlus Pharmacy'
             AND m.medicine_code = 'ORS001'
             THEN 'WARNING'

        ELSE 'SAFE'
    END::severity_enum,

    NOW() - INTERVAL '5 days'

FROM facilities f
CROSS JOIN medicine_master m;