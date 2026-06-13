-- =====================================================
-- AEGISFLOW
-- CHENNAI HEALTHCARE LOCATIONS
-- =====================================================

INSERT INTO locations (
    country,
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
    'India',
    'Tamil Nadu',
    'Chennai',
    'Anna Nagar',
    '600040',
    '2nd Avenue Anna Nagar',
    13.0849,
    80.2101,
    ST_SetSRID(ST_MakePoint(80.2101,13.0849),4326)::geography
),

(
    'India',
    'Tamil Nadu',
    'Chennai',
    'Velachery',
    '600042',
    'Velachery Main Road',
    12.9750,
    80.2200,
    ST_SetSRID(ST_MakePoint(80.2200,12.9750),4326)::geography
),

(
    'India',
    'Tamil Nadu',
    'Chennai',
    'Tambaram',
    '600045',
    'GST Road Tambaram',
    12.9249,
    80.1000,
    ST_SetSRID(ST_MakePoint(80.1000,12.9249),4326)::geography
),

(
    'India',
    'Tamil Nadu',
    'Chennai',
    'Porur',
    '600116',
    'Mount Poonamallee Road',
    13.0380,
    80.1565,
    ST_SetSRID(ST_MakePoint(80.1565,13.0380),4326)::geography
),

(
    'India',
    'Tamil Nadu',
    'Chennai',
    'OMR',
    '600119',
    'Old Mahabalipuram Road',
    12.9121,
    80.2295,
    ST_SetSRID(ST_MakePoint(80.2295,12.9121),4326)::geography
),

(
    'India',
    'Tamil Nadu',
    'Chennai',
    'T Nagar',
    '600017',
    'Usman Road',
    13.0418,
    80.2341,
    ST_SetSRID(ST_MakePoint(80.2341,13.0418),4326)::geography
);