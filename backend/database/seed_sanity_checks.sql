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

    '17fe8ebc-b47e-4cec-921b-37f96627d89d',

    m.medicine_id,

    CASE
        WHEN m.medicine_code='INS100' THEN 80
        WHEN m.medicine_code='SAL100' THEN 60
        ELSE 500
    END,

    FLOOR(RANDOM()*300+150)::INTEGER,

    FLOOR(RANDOM()*30)::INTEGER,

    50,

    100,

    ROUND((RANDOM()*20+5)::NUMERIC,2),

    FLOOR(RANDOM()*10+3)::INTEGER,

    ROUND((RANDOM()*50)::NUMERIC,2),

    'SAFE'::severity_enum,

    NOW()-INTERVAL '5 days'

FROM medicine_master m;