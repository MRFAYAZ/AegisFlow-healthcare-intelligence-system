-- =====================================================
-- AEGISFLOW
-- HEALTHCARE FACILITIES
-- =====================================================

INSERT INTO facilities (
    facility_name,
    facility_type,
    location_id,
    license_number,
    contact_email,
    emergency_contact,
    is_24x7
)

SELECT
    'Apollo Hospital Chennai',
    'HOSPITAL'::facility_type_enum,
    location_id,
    'TN-HOSP-1001',
    'apollo@hospital.com',
    '04411111111',
    TRUE
FROM locations
WHERE city='Anna Nagar'

UNION ALL

SELECT
    'Government General Hospital',
    'HOSPITAL'::facility_type_enum,
    location_id,
    'TN-HOSP-1002',
    'ggh@tn.gov.in',
    '04422222222',
    TRUE
FROM locations
WHERE city='Tambaram'

UNION ALL

SELECT
    'SIMS Hospital',
    'HOSPITAL'::facility_type_enum,
    location_id,
    'TN-HOSP-1003',
    'sims@hospital.com',
    '04433333333',
    TRUE
FROM locations
WHERE city='Porur'

UNION ALL

SELECT
    'Apollo Pharmacy',
    'MEDICAL_SHOP'::facility_type_enum,
    location_id,
    'TN-MED-2001',
    'apollo@pharmacy.com',
    '04444444444',
    FALSE
FROM locations
WHERE city='Velachery'

UNION ALL

SELECT
    'MedPlus Pharmacy',
    'MEDICAL_SHOP'::facility_type_enum,
    location_id,
    'TN-MED-2002',
    'medplus@pharmacy.com',
    '04455555555',
    FALSE
FROM locations
WHERE city='T Nagar'

UNION ALL

SELECT
    'Aster Medical Supplier',
    'SUPPLIER'::facility_type_enum,
    location_id,
    'TN-SUP-3001',
    'supplier@aster.com',
    '04466666666',
    FALSE
FROM locations
WHERE city='OMR';