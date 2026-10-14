WITH ranked AS (

SELECT

    ec.emergency_case_id,

    ic.facility_id,

    ec.medicine_id,

    ic.available_stock,

    GREATEST(
        ic.available_stock - ic.minimum_threshold,
        0
    ) AS transferable_quantity,

    ROUND(
        (
            RANDOM()*20+5
        )::numeric,
        2
    ) AS distance_km,

    ic.shortage_score,

    ROUND(
        (
            (
                GREATEST(
                    ic.available_stock-ic.minimum_threshold,
                    0
                )*0.55
            )
            +
            (
                (100-ic.shortage_score)*0.25
            )
            +
            (
                (100-(RANDOM()*20))*0.20
            )
        )::numeric,
        2
    ) AS ranking_score,

    ROW_NUMBER() OVER(

        PARTITION BY
            ec.emergency_case_id

        ORDER BY

            (
                (
                    GREATEST(
                        ic.available_stock-ic.minimum_threshold,
                        0
                    )*0.55
                )
                +
                (
                    (100-ic.shortage_score)*0.25
                )
            )

            DESC

    ) AS rn

FROM emergency_cases ec

JOIN inventory_current ic

ON
    ic.medicine_id=ec.medicine_id

WHERE

    ic.facility_id<>ec.facility_id

AND

    ic.available_stock>ic.minimum_threshold

)

INSERT INTO emergency_source_matches
(
    emergency_case_id,
    source_facility_id,
    medicine_id,
    available_quantity,
    transferable_quantity,
    distance_km,
    donor_shortage_score,
    ranking_score,
    is_selected,
    matched_at
)

SELECT

    emergency_case_id,

    facility_id,

    medicine_id,

    available_stock,

    transferable_quantity,

    distance_km,

    shortage_score,

    ranking_score,

    rn=1,

    NOW()

FROM ranked

WHERE rn<=5;