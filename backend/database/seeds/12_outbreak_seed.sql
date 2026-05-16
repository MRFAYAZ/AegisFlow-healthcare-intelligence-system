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
    m.medicine_id,
    120,
    210,
    75,
    4,
    89,
    'CONFIRMED'
FROM medicine_master m
WHERE m.medicine_name = 'Paracetamol 500mg'
ON CONFLICT DO NOTHING;

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
    'Coimbatore',
    m.medicine_id,
    80,
    155,
    93,
    3,
    84,
    'UNDER_REVIEW'
FROM medicine_master m
WHERE m.medicine_name = 'Azithromycin 500mg'
ON CONFLICT DO NOTHING;

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
    'Madurai',
    m.medicine_id,
    60,
    118,
    96,
    2,
    79,
    'DETECTED'
FROM medicine_master m
WHERE m.medicine_name = 'ORS Sachet'
ON CONFLICT DO NOTHING;