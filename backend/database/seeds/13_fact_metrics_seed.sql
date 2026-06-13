-- =====================================================
-- AEGISFLOW
-- DATE DIMENSION
-- =====================================================

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

SELECT
    d::date,
    EXTRACT(DAY FROM d),
    EXTRACT(MONTH FROM d),
    EXTRACT(QUARTER FROM d),
    EXTRACT(YEAR FROM d),
    TO_CHAR(d,'Day'),
    CASE
        WHEN EXTRACT(ISODOW FROM d) IN (6,7)
        THEN TRUE
        ELSE FALSE
    END,
    'SUMMER'

FROM generate_series(
    CURRENT_DATE - INTERVAL '30 days',
    CURRENT_DATE,
    INTERVAL '1 day'
) d;

-- =====================================================
-- AEGISFLOW
-- FACT INVENTORY METRICS
-- =====================================================

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

    facility_id,

    medicine_id,

    shortage_score,

    available_stock,

    FLOOR(RANDOM() * 5)::INTEGER,

    CASE
        WHEN severity IN ('CRITICAL','EMERGENCY')
        THEN 1
        ELSE 0
    END

FROM inventory_current;