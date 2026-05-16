INSERT INTO facilities (
    facility_name,
    facility_type,
    location_id,
    license_number,
    contact_email,
    emergency_contact,
    operating_hours,
    is_24x7
)
SELECT
    'Apollo Hospital Chennai',
    'HOSPITAL',
    location_id,
    'TN-HSP-001',
    'apollo@hospital.com',
    '9000000101',
    '24 Hours',
    TRUE
FROM locations
WHERE city = 'Chennai'
ON CONFLICT DO NOTHING;

INSERT INTO facilities (
    facility_name,
    facility_type,
    location_id,
    license_number,
    contact_email,
    emergency_contact,
    operating_hours,
    is_24x7
)
SELECT
    'Fortis Medical Center',
    'HOSPITAL',
    location_id,
    'MH-HSP-002',
    'fortis@hospital.com',
    '9000000102',
    '24 Hours',
    TRUE
FROM locations
WHERE city = 'Coimbatore'
ON CONFLICT DO NOTHING;

INSERT INTO facilities (
    facility_name,
    facility_type,
    location_id,
    license_number,
    contact_email,
    emergency_contact,
    operating_hours,
    is_24x7
)
SELECT 
    'MedPlus Pharmacy Chennai',
    'MEDICAL_SHOP',
    location_id,
    'TN-SHP-001',
    'medplus@shop.com',
    '9000000103',
    '9 AM - 9 PM',
    FALSE
FROM locations
WHERE city = 'Chennai'
ON CONFLICT DO NOTHING;

INSERT INTO facilities (
    facility_name,
    facility_type,
    location_id,
    license_number,
    contact_email,
    emergency_contact,
    operating_hours,
    is_24x7
)
SELECT
    'WellCare Pharmacy Hyderabad',
    'MEDICAL_SHOP',
    location_id,
    'TG-SHP-001',
    'wellcare@shop.com',
    '9000000104',
    '9 AM - 10 PM',
    FALSE
FROM locations
WHERE city = 'Hyderabad'
ON CONFLICT DO NOTHING;

INSERT INTO facilities (
    facility_name,
    facility_type,
    location_id,
    license_number,
    contact_email,
    emergency_contact,
    operating_hours,
    is_24x7
)
SELECT 
    'SouthCare Suppliers',
    'SUPPLIER',
    location_id,
    'KA-SUP-001',
    'supplier@southcare.com',
    '9000000105',
    '24 Hours',
    TRUE
FROM locations
WHERE city = 'Bangalore'
ON CONFLICT DO NOTHING;
