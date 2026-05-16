INSERT INTO locations (
    state,
    district,
    city,
    postal_code,
    address_line,
    latitude,
    longitude,
    geo_point
)
VALUES
(
    'Tamil Nadu',
    'Chennai',
    'Chennai',
    '600095',
    'Ambattur Industrial Estate',
    13.1143,
    80.1548,
    ST_SetSRID(ST_MakePoint(80.1548, 13.1143), 4326)
),
(
    'Tamil Nadu',
    'Coimbatore',
    'Coimbatore',
    '641001',
    'Gandhipuram Main Road',
    11.0168,
    76.9558,
    ST_SetSRID(ST_MakePoint(76.9558, 11.0168), 4326)
),
(
    'Tamil Nadu',
    'Madurai',
    'Madurai',
    '625001',
    'KK Nagar',
    9.9252,
    78.1198,
    ST_SetSRID(ST_MakePoint(78.1198, 9.9252), 4326)
),
(
    'Karnataka',
    'Bangalore Urban',
    'Bangalore',
    '560001',
    'MG Road',
    12.9716,
    77.5946,
    ST_SetSRID(ST_MakePoint(77.5946, 12.9716), 4326)
),
(
    'Telangana',
    'Hyderabad',
    'Hyderabad',
    '500001',
    'Banjara Hills',
    17.3850,
    78.4867,
    ST_SetSRID(ST_MakePoint(78.4867, 17.3850), 4326)
)
ON CONFLICT DO NOTHING;